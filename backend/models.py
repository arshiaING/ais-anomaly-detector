from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# representerer én AIS-posisjon fra ett skip
class SkipPosisjon(BaseModel):
    mmsi: str  # identiteten til skipet i systemet — alltid 9 siffer
    navn: str | None = None  # noen skip mangler navn i dataene

    # koordinater i desimalgrader
    breddegrad: float
    lengdegrad: float

    fart_over_grunn: float | None = None  # i knop
    kurs_over_grunn: float | None = None  # i grader, 0–360

    tidspunkt: datetime  # når posisjonen ble registrert
    skipstype: int | None = None  # kan brukes senere til enkel sortering (f.eks. 70 = lasteskip)


# en oppdaget anomali — oppstår når anomaly_detector finner noe mistenkelig
class Anomali(BaseModel):
    mmsi: str
    skipsnavn: str | None = None

    # hvilken type anomali det er — bruker Literal så det ikke kan bli noe annet
    anomalitype: Literal["FART", "KURS", "AIS_GAP", "SONE"]

    # hvor alvorlig er det — LAV, MIDDELS eller HOY
    alvorlighetsgrad: Literal["LAV", "MIDDELS", "HOY"]

    beskrivelse: str  # lesbar forklaring på hva som skjedde

    # posisjon der anomalien ble oppdaget
    breddegrad: float
    lengdegrad: float

    # settes automatisk til nå hvis ikke annet oppgis
    oppdaget_tidspunkt: datetime = Field(default_factory=datetime.utcnow)


# dette er svaret som sendes til frontend — inneholder alle skip og eventuelle anomalier
class LiveOppdatering(BaseModel):
    skip: list[SkipPosisjon]
    anomalier: list[Anomali]
    oppdatert_tidspunkt: datetime  # når denne oppdateringen ble generert
