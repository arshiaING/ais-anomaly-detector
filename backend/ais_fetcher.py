from pprint import pprint

import requests
from pydantic import ValidationError

from backend.config import innstillinger
from backend.models import SkipPosisjon


def sjekk_barentswatch_oppsett() -> None:
    
    mangler = []

    if not innstillinger.barentswatch_client_id:
        mangler.append("BARENTSWATCH_CLIENT_ID")

    if not innstillinger.barentswatch_client_secret:
        mangler.append("BARENTSWATCH_CLIENT_SECRET")

    if innstillinger.barentswatch_client_id == "din_client_id":
        mangler.append("BARENTSWATCH_CLIENT_ID har bare eksempelverdi")

    if innstillinger.barentswatch_client_secret == "din_client_secret":
        mangler.append("BARENTSWATCH_CLIENT_SECRET har bare eksempelverdi")

    if mangler:
        mangler_tekst = ", ".join(mangler)
        raise ValueError(
            f"BarentsWatch-oppsettet er ikke klart: {mangler_tekst}. "
            "Fyll inn ekte verdier i .env før live AIS kan testes."
        )


def hent_barentswatch_token() -> str:
    
    sjekk_barentswatch_oppsett()

    foresporsel_data = {
        "client_id": innstillinger.barentswatch_client_id,
        "client_secret": innstillinger.barentswatch_client_secret,
        "scope": "ais",
        "grant_type": "client_credentials",
    }

    svar = requests.post(
        innstillinger.barentswatch_token_url,
        data=foresporsel_data,
        timeout=innstillinger.foresporsel_timeout_sekunder,
    )

    svar.raise_for_status()

    token_data = svar.json()
    return token_data["access_token"]


def hent_siste_ais_posisjoner() -> list[dict]:
    
    token = hent_barentswatch_token()

    url = f"{innstillinger.barentswatch_live_ais_url}/latest/combined"

    
    headers = {
        "Authorization": f"Bearer {token}"
    }

    svar = requests.get(
        url,
        headers=headers,
        timeout=innstillinger.foresporsel_timeout_sekunder,
    )

    svar.raise_for_status()

    
    return svar.json()


def rydd_ais_posisjon(rå_posisjon: dict) -> dict:
    
    return {
        "mmsi": str(rå_posisjon.get("mmsi", "")),
        "navn": rå_posisjon.get("name"),
        "breddegrad": rå_posisjon.get("latitude"),
        "lengdegrad": rå_posisjon.get("longitude"),
        "fart_over_grunn": rå_posisjon.get("speedOverGround"),
        "kurs_over_grunn": rå_posisjon.get("courseOverGround"),
        "tidspunkt": rå_posisjon.get("msgtime"),
        "skipstype": rå_posisjon.get("shipType"),
    }



def lag_skip_posisjon(rå_posisjon: dict) -> SkipPosisjon:
    
    ryddet_posisjon = rydd_ais_posisjon(rå_posisjon)

    return SkipPosisjon(**ryddet_posisjon)



def lag_skip_posisjoner(
    rå_posisjoner: list[dict],
    maks_antall: int = 20,
) -> list[SkipPosisjon]:
    # Vi lager bare et begrenset antall først, så testen ikke printer altfor mye.
    # fjerne maks_antall 
    skip_posisjoner = []

    for raa_posisjon in rå_posisjoner[:maks_antall]:
        try:
            skip_posisjon = lag_skip_posisjon(raa_posisjon)
            skip_posisjoner.append(skip_posisjon)
        except ValidationError:
            # Noen AIS-meldinger kan mangle felt eller ha rare verdier
            continue

    return skip_posisjoner



if __name__ == "__main__":
   
    posisjoner = hent_siste_ais_posisjoner()

    print("Hentet AIS-posisjoner fra BarentsWatch.")
    print("antall posisjoner:", len(posisjoner))

    
    if posisjoner:
        print("\nFørste rå AIS-posisjon:")
        pprint(posisjoner[0])

        ryddet_posisjon = rydd_ais_posisjon(posisjoner[0])

        print("\nSamme posisjon ryddet til norske feltnavn:")
        pprint(ryddet_posisjon)

        skip_posisjon = lag_skip_posisjon(posisjoner[0])

        print("\nSamme posisjon som SkipPosisjon-modell:")
        print(skip_posisjon)

        skip_posisjoner = lag_skip_posisjoner(posisjoner)

        print("\nAntall posisjoner som passet modellen:", len(skip_posisjoner))
        print("Første 3 ryddede skip:")
        pprint(skip_posisjoner[:3])
    else:
        print("\nIngen posisjoner funnet.")

    