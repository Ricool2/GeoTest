from fastapi import FastAPI
from geojson import FeatureCollection
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from contextlib import asynccontextmanager
from os import environ

from .scripts import geometry_to_str, pars_excel, insert_data, data_to_sqlmodel, create_geojson
from .schemas import Base, VehicleLocation
from .model import VehicleLocation as Model

# Получаем переменные окружения
db_url: str = environ.get("DATABASE_URL")
engine = create_async_engine(db_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# ЖЦ приложения в виде контекстного менеджера
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # очищаем таблицу в бд
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis")) # подключаем PostGIS
        await conn.run_sync(Base.metadata.create_all) # создаем таблицу в бд
    
    # Заполнение таблицы данными из Эксель файла
    try:
        data: list[tuple] = pars_excel()
        vehicle_locations: list[VehicleLocation] = data_to_sqlmodel(data)
        await insert_data(vehicle_locations, async_session)

    # Любая ошибка на данном этапе незначительна, приложение может работать дальше
    except Exception as ex:
        print(f'\033[33mWARNING\033[0m:  Data from the excel-file was never inserted, because of "{ex}".\nStill, application is running.')

    yield # Промежуточное состояние после запуска приложения

    await engine.dispose() # Закрытие подключения

app = FastAPI(lifespan=lifespan, title="Geo Test")

# GET запрос для получения всех машин с последней геометрией
@app.get("/vehicles", tags=['Vehicles'], name="запрос для получения всех машин с последней геометрией" ,response_model=list[Model])
async def get_last_geometry_all():
    async with async_session() as session:
        vehicles = await session.execute(
            select(VehicleLocation)
            )
        vehicles_db = vehicles.scalars().all()
        return geometry_to_str(vehicles_db)

# GET запрос для получения конкретной машины с последней геометрией
@app.get("/vehicles/{vehicle_id}", tags=['Vehicles'], name="запрос для получения конкретной машины с последней геометрией", response_model=list[Model])
async def get_last_geometry_by_vehicleid(vehicle_id: int):
    async with async_session() as session:
        vehicles = await session.execute(
            select(VehicleLocation).order_by(
                VehicleLocation.vehicle_id
                ).where(
                    VehicleLocation.vehicle_id == vehicle_id
                )
            )
        vehicles_db = vehicles.scalars().all()
        return geometry_to_str(vehicles_db)

# GET запрос для построения трека по дате или временному диапазону для конкретной машины.
@app.get("/vehicles/{vehicle_id}/track", name="запрос для построения трека по дате или временному диапазону для конкретной машины", tags=['Vehicles'],)
async def get_timetrack_vehicle_by_id(vehicle_id: int):
    async with async_session() as session:
        vehicles = await session.execute(
            select(VehicleLocation).order_by(
                VehicleLocation.vehicle_id
                ).where(
                    VehicleLocation.vehicle_id == vehicle_id
                ).order_by(VehicleLocation.gps_time)
            )
        track: FeatureCollection = await create_geojson(vehicles.scalars().all())
        return track