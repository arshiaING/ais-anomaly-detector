from pprint import pprint

import requests
from pydantic import ValidationError

from backend.config import innstillinger
from backend.models import SkipPosisjon


# sjekker at BarentsWatch-kredensialene er satt i .env før vi prøver å koble til
def sjekk_barentswatch_oppsett() -> None:

    mangler = []

    if not innstillinger.barentswatch_client_id:
        mangler.append("BARENTSWATCH_CLIENT_ID")

    if not innstillinger.barentswatch_client_secret:
        mangler.append("BARENTSWATCH_CLIENT_SECRET")

    # fanger opp tilfeller der folk bare har kopiert .env.example uten å bytte verdiene
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


# henter OAuth2-token fra BarentsWatch — tokenet brukes på alle videre kall
def hent_barentswatch_token() -> str:

    sjekk_barentswatch_oppsett()

    # client_credentials = maskin-til-maskin autentisering, ingen bruker involvert
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

    # kaster feil med statuskode hvis noe gikk galt (f.eks. 401 feil credentials)
    svar.raise_for_status()

    token_data = svar.json()
    return token_data["access_token"]


# henter de siste AIS-posisjonene fra BarentsWatch — returnerer rå dict-liste
def hent_siste_ais_posisjoner() -> list[dict]:

    token = hent_barentswatch_token()

    # /latest/combined gir siste kjente posisjon per skip
    url = f"{innstillinger.barentswatch_live_ais_url}/latest/combined"

    # tokenet legges i Authorization-headeren som Bearer
    headers = {
        "Authorization": f"Bearer {token}"
    }

    svar = requests.get(
        url,
        headers=headers,
        timeout=innstillinger.foresporsel_timeout_sekunder,
    )

    svar.raise_for_status()

    # returnerer rå JSON — rydding skjer i rydd_ais_posisjon()
    return svar.json()


# mapper fra BarentsWatch sine engelske feltnavn til våre norske feltnavn
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


# konverterer én rå posisjon til et SkipPosisjon-objekt via Pydantic
def lag_skip_posisjon(rå_posisjon: dict) -> SkipPosisjon:

    ryddet_posisjon = rydd_ais_posisjon(rå_posisjon)

    # Pydantic validerer feltene her — kaster ValidationError hvis noe mangler
    return SkipPosisjon(**ryddet_posisjon)


# konverterer en liste med rå posisjoner til SkipPosisjon-objekter
# returnerer også antall som ble hoppet over pga. valideringsfeil
def lag_skip_posisjoner(
    rå_posisjoner: list[dict],
    maks_antall: int = 50,
) -> tuple[list[SkipPosisjon], int]:
    # Vi lager bare noen posisjoner først, så testen holder seg oversiktlig.
    # TODO: fjerne maks_antall når vi er klare for full kjøring
    skip_posisjoner = []
    antall_hoppet_over = 0

    for raa_posisjon in rå_posisjoner[:maks_antall]:
        try:
            skip_posisjon = lag_skip_posisjon(raa_posisjon)
            skip_posisjoner.append(skip_posisjon)
        except ValidationError:
            # Noen AIS-meldinger kan mangle felt eller ha rare verdier — vi skipper dem
            antall_hoppet_over += 1

    return skip_posisjoner, antall_hoppet_over


# kjør dette direkte for å teste at BarentsWatch-oppkobling fungerer
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

        skip_posisjoner, antall_hoppet_over = lag_skip_posisjoner(posisjoner)

        print("\nAntall posisjoner som passet modellen:", len(skip_posisjoner))
        print("Antall posisjoner hoppet over:", antall_hoppet_over)

        if skip_posisjoner:
            print("\nFørste 3 SkipPosisjon-objekter:")
            pprint(skip_posisjoner[:3])
    else:
        print("\nIngen posisjoner funnet.")
