from typing import List
from pydantic import BaseModel, Field


class BanxicoDataPoint(BaseModel):
    """Single data point from Banxico API"""

    fecha: str
    dato: str


class BanxicoSeries(BaseModel):
    """Time series from Banxico API"""

    idSerie: str
    titulo: str
    datos: List[BanxicoDataPoint]


class BanxicoSeriesContainer(BaseModel):
    """Container for Banxico series data"""

    series: List[BanxicoSeries]


class BanxicoResponse(BaseModel):
    """Top-level Banxico API response"""

    bmx: BanxicoSeriesContainer = Field(
        ...,
        example={
            "series": [
                {
                    "idSerie": "SF43718",
                    "titulo": "Tipo de cambio Pesos por dólar E.U.A.",
                    "datos": [
                        {"fecha": "16/07/2025", "dato": "18.2450"},
                        {"fecha": "15/07/2025", "dato": "18.1890"},
                    ],
                }
            ]
        },
    )
