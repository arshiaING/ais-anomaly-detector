from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SkipPosisjon(BaseModel):
    mmsi: str  # identiteten til skipet i AIS-systemet
    navn: str | None = None # navn
    Latitude: float
    Longitude: float
    fart: float = 0.0
    kurs: float = 0.0
    tidspunkt: datetime # Når posisjonen ble registrert så vi kan sammenligne tider 
    skipstype: int | None = None # kan brukes til å sortere 


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