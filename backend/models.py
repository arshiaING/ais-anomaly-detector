from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SkipPosisjon(BaseModel):
    mmsi: str  # identiteten til skipet i systemet
    navn: str | None = None  # noen skip mangler navn i dataene

    breddegrad: float
    lengdegrad: float

    fart_over_grunn: float | None = None
    kurs_over_grunn: float | None = None

    tidspunkt: datetime  # når posisjonen ble registrert
    skipstype: int | None = None  # kan brukes senere til enkel sortering


class Anomali(BaseModel):
    mmsi: str
    skipsnavn: str | None = None
    anomalitype: Literal["FART", "KURS", "AIS_GAP", "SONE"]
    alvorlighetsgrad: Literal["LAV", "MIDDELS", "HOY"]
    beskrivelse: str
    breddegrad: float
    lengdegrad: float
    oppdaget_tidspunkt: datetime = Field(default_factory=datetime.utcnow)


class LiveOppdatering(BaseModel):
    skip: list[SkipPosisjon]
    anomalier: list[Anomali]
    oppdatert_tidspunkt: datetime