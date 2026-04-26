from fastapi import FastAPI

from backend.config import innstillinger
from backend.ais_fetcher import hent_siste_ais_posisjoner, lag_skip_posisjoner

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


@app.get("/skip/live")
def hent_live_skip():
    
    rå_posisjoner = hent_siste_ais_posisjoner()

    skip_posisjoner, antall_hoppet_over = lag_skip_posisjoner(
        rå_posisjoner,
        maks_antall=50,
    )

    return {
        "antall": len(skip_posisjoner),
        "antall_hoppet_over": antall_hoppet_over,
        "skip": skip_posisjoner,
    }