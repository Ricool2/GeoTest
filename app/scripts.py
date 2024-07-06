from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
import geojson
from pandas import DataFrame, read_excel
from pydantic import FilePath
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from datetime import datetime

from .schemas import VehicleLocation as Schema

# функция парсинга excel файла 
def pars_excel(path: str | FilePath = '2_5420464171701519891.xlsx') -> list[tuple]:
    df: DataFrame = read_excel(path,)
    return list(df.itertuples(index=False,name=None))

# Функция вставки данных в таблицу
async def insert_data(data: list[Schema], async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add_all(data)

# Перевод данных python в модель бд
def data_to_sqlmodel(data: list[dict]) -> list[Schema]:
    result: list[Schema] = []
    for row in data:
        try:
            # Валидация по типам атрибутов
            vehicle_location = Schema.validate(
                    id = row[0],
                    geom = WKTElement(f"POINT({row[1]} {row[2]})", srid=4326), # Переводим координаты в тип Geometry,
                    speed = row[3],
                    gps_time = datetime.fromisoformat(row[4]).replace(tzinfo=None),
                    vehicle_id = row[5],
                )
            result.append(vehicle_location)

        except ValueError as ex:
            print(f'\033[33mWARNING\033[0m:  Where is error with incoming data: "{ex}"')
        
    return result

# Создание GeoJSON из данных модели бд
async def create_geojson(sorted_data: list[Schema]) -> geojson.FeatureCollection:
    sorted_data = geometry_to_str(sorted_data)
    features = []
    for item in sorted_data:
        
        # Получаем широту и долготу из типа точки
        longitude, latitude = item.geom[7:-1].split(" ")

        # Собираем Футуру с новыми данными координат
        geojson_feature = geojson.Feature(
            geometry=geojson.Point([float(longitude), float(latitude)]),
            properties={
                "gps_time": item.gps_time.isoformat(),
                "vehicle_id": item.vehicle_id,
                "id": item.id,
                "speed": item.speed
            }
        )
        features.append(geojson_feature)

    return geojson.FeatureCollection(features)

# Перевод геометрических данных в читаемый вид
def geometry_to_str(data: list[Schema]) -> list[Schema]:
    for item in data:
        item.geom = to_shape(item.geom).wkt
    return data