from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


def hent_heltall_fra_miljo(navn: str, standardverdi: int) -> int:
    verdi = os.getenv(navn)
    if verdi is None or verdi == "":
        return standardverdi
    try:
        return int(verdi)
    except ValueError:
        return standardverdi



def hent_flyttall_fra_miljo(navn: str, standardverdi: float) -> float:
    verdi = os.getenv(navn)
    if verdi is None or verdi == "":
        return standardverdi
    try:
        return float(verdi)
    except ValueError:
        return standardverdi


@dataclass
class Innstillinger:
    app_navn: str = os.getenv("APP_NAVN", "AIS Anomalidetektor")
    ais_api_grunn_url: str = os.getenv(
        "AIS_API_GRUNN_URL",
        "https://kystdatahuset.no/ws/api/ais",
    )
    foresporsel_timeout_sekunder: int = hent_heltall_fra_miljo(
        "FORESPORSEL_TIMEOUT_SEKUNDER", 10
    )
    oppdateringsintervall_sekunder: int = hent_heltall_fra_miljo(
        "OPPDATERINGSINTERVALL_SEKUNDER", 30
    )

    fartshopp_terskel_knop: float = hent_flyttall_fra_miljo(
        "FARTSHOPP_TERSKEL_KNOP", 10.0
    )
    fartsvindu_minutter: int = hent_heltall_fra_miljo(
        "FARTSVINDU_MINUTTER", 5
    )

    kurshopp_terskel_grader: float = hent_flyttall_fra_miljo(
        "KURSHOPP_TERSKEL_GRADER", 45.0
    )
    kursvindu_minutter: int = hent_heltall_fra_miljo(
        "KURSVINDU_MINUTTER", 5
    )

    ais_gap_minutter: int = hent_heltall_fra_miljo(
        "AIS_GAP_MINUTTER",
        30
    )
    # jeg trenger sanntid data for å få fech til å fungere riktig
    barentswatch_token_url: str = os.getenv(
        "BARENTSWATCH_TOKEN_URL",
        "https://id.barentswatch.no/connect/token",
    )

    barentswatch_live_ais_url: str = os.getenv(
        "BARENTSWATCH_LIVE_AIS_URL",
        "https://live.ais.barentswatch.no/v1",
    )

    barentswatch_client_id: str | None = os.getenv("BARENTSWATCH_CLIENT_ID")
    barentswatch_client_secret: str | None = os.getenv("BARENTSWATCH_CLIENT_SECRET")

    telegram_bot_token: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = os.getenv("TELEGRAM_CHAT_ID")