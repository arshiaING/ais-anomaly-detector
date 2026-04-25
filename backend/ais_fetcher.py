import requests

from backend.config import innstillinger


def sjekk_barentswatch_oppsett() -> None:
    # ha client id og secret.
    if not innstillinger.barentswatch_client_id:
        raise ValueError("Mangler BARENTSWATCH_CLIENT_ID i .env")

    if not innstillinger.barentswatch_client_secret:
        raise ValueError("Mangler BARENTSWATCH_CLIENT_SECRET i .env")


def hent_barentswatch_token() -> str:
    # Første steg mot live AIS er å hente et access token.
    # Uten token får vi ikke lov til å kalle BarentsWatch sitt AIS-API.
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


if __name__ == "__main__":
    # test 
    token = hent_barentswatch_token()

    print("BarentsWatch-token hentet.")
    print("Lengde på token:", len(token))