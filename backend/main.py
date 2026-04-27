from fastapi import FastAPI, HTTPException, Query
from requests.exceptions import RequestException

from backend.config import innstillinger
from backend.ais_fetcher import hent_siste_ais_posisjoner, lag_skip_posisjoner

# oppretter FastAPI-appen — tittelen hentes fra .env via innstillinger
app = FastAPI(title=innstillinger.app_navn)


# rot-endepunkt, bare for å sjekke at appen lever
@app.get("/")
async def hjem():
    return {"melding": "AIS Anomalidetektor kjører"}


# helsesjekk — nyttig for Docker og overvåking, returnerer nøkkelinnstillinger
@app.get("/health")
async def helse():
    return {
        "status": "ok",
        "app_navn": innstillinger.app_navn,
        "oppdateringsintervall_sekunder": innstillinger.oppdateringsintervall_sekunder,
        "foresporsel_timeout_sekunder": innstillinger.foresporsel_timeout_sekunder,
    }


@app.get("/skip/live")
def hent_live_skip(
    maks_antall: int = Query(50, ge=1, le=500),
):
    # Denne routen henter live AIS-data og returnerer et begrenset antall skip.
    # maks_antall kan styres i URL-en, for eksempel /skip/live?maks_antall=20.
    try:
        rå_posisjoner = hent_siste_ais_posisjoner()

        skip_posisjoner, antall_hoppet_over = lag_skip_posisjoner(
            rå_posisjoner,
            maks_antall=maks_antall,
        )

        return {
            "antall": len(skip_posisjoner),
            "maks_antall": maks_antall,
            "antall_hoppet_over": antall_hoppet_over,
            "skip": skip_posisjoner,
        }

    except ValueError as feil:
        # Dette skjer typisk hvis .env mangler BarentsWatch-oppsett.
        raise HTTPException(
            status_code=400,
            detail=str(feil),
        )

    except RequestException:
        # Dette skjer hvis kall mot BarentsWatch feiler.
        raise HTTPException(
            status_code=502,
            detail="Klarte ikke å hente AIS-data fra BarentsWatch akkurat nå.",
        )