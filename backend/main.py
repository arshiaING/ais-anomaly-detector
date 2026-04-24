from datetime import datetime

from fastapi import FastAPI

from backend.config import innstillinger
from backend.models import Anomali, LiveOppdatering, SkipPosisjon

app = FastAPI(title=innstillinger.app_navn)


@app.get("/")
async def hjem():
    return {"melding": "AIS Anomalidetektor kjører"}


@app.get("/health")
async def helse():
    return {
        "status": "ok",
        "app_navn": innstillinger.app_navn,
        "oppdateringsintervall_sekunder": innstillinger.oppdateringsintervall_sekunder,
        "foresporsel_timeout_sekunder": innstillinger.foresporsel_timeout_sekunder,
    }


@app.get("/eksempel")
async def eksempel():
    skip = SkipPosisjon(
        mmsi="123456789",
        navn="Testskip",
        breddegrad=59.91,
        lengdegrad=10.75,
        fart_over_grunn=12.5,
        kurs_over_grunn=95.0,
        tidspunkt=datetime.utcnow(),
        skipstype=70,
    )

    anomali = Anomali(
        mmsi="123456789",
        skipsnavn="Testskip",
        anomalitype="FART",
        alvorlighetsgrad="HOY",
        beskrivelse="Brå fartsendring oppdaget",
        breddegrad=59.91,
        lengdegrad=10.75,
    )

    svar = LiveOppdatering(
        skip=[skip],
        anomalier=[anomali],
        oppdatert_tidspunkt=datetime.utcnow(),
    )

    return svar