from sqlalchemy import Column, DECIMAL, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry, WKTElement

Base = declarative_base()

# Модель таблицы vehicle_locations
class VehicleLocation(Base):
    __tablename__ = "vehicle_locations"

    id: Column[Integer] = Column(Integer, primary_key=True)
    geom: Column[Geometry] = Column(Geometry("Point", 4326))
    speed: Column[Integer] = Column(Integer)
    gps_time: Column[DateTime] = Column(DateTime)
    vehicle_id: Column[Integer] = Column(Integer, index=True) # Генерируем индекс по столбцу, т.к. он используется в запросах по условию

    # Метод класса, который валидирует данные
    @classmethod
    def validate(cls, **kwargs):
        for k in kwargs:
            column = getattr(cls.__table__.c, k)
            if column.name == "geom":
                try:
                    lon, lat = str(kwargs[k])[7:-1].split(" ")
                    lon, lat = float(lon), float(lat)
                except:
                    raise ValueError(f"Type of {k} is not Geometry ({k}: {kwargs[k]})")
            elif type(kwargs[k]) is not column.type.python_type:
                raise ValueError(f"Type of {k} is not {column.type} ({k}: {kwargs[k]})")
        return cls(**kwargs)

