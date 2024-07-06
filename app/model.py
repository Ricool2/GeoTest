from datetime import datetime
from pydantic import BaseModel, Field
from geoalchemy2.elements import WKTElement
from typing import Annotated

class VehicleLocation(BaseModel):
    id: int = Field(title="Идентификатор записи")
    geom: str = Field(title="Координаты (долгота, ширина)")
    speed: int = Field(title="Скорость в км/ч")
    gps_time: datetime = Field(title="Время записи")
    vehicle_id: int = Field(title="Идентификатор трансорта")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    'id': 111,
                    'geom': "POINT (01.000001 01.000001)",
                    'speed': 100,
                    'gps_time': "2020-01-01T00:00:00",
                    'vehicle_id': 12345,
                }
            ]
        }
    }