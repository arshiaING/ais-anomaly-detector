from fastapi import FastAPI, HTTPException
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
def hent_live_skip():
    # Denne routen er en enkel test på at backend kan hente live AIS-data.
    # Token og BarentsWatch-kall skjer inne i fetcheren, ikke i nettleseren.
    try:
        raa_posisjoner = hent_siste_ais_posisjoner()

        skip_posisjoner, antall_hoppet_over = lag_skip_posisjoner(
            raa_posisjoner,
            maks_antall=50,
        )

        return {
            "antall": len(skip_posisjoner),
            "antall_hoppet_over": antall_hoppet_over,
            "skip": skip_posisjoner,
        }

    except ValueError as feil:
        # hvis .env mangler
        raise HTTPException(
            status_code=400,
            detail=str(feil),
        )

    except RequestException:
        #  nettverk eller token-feil.
        raise HTTPException(
            status_code=502,
            detail="Klarte ikke å hente AIS-data fra BarentsWatch akkurat nå.",
        )