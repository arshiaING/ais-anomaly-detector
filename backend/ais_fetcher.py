from datetime import datetime, timedelta, timezone

import requests

from backend.config import innstillinger


def formater_tidspunkt(tidspunkt: datetime) -> str:
    #  tidspunkt på form
    return tidspunkt.strftime("%Y%m%d%H%M")


def hent_raa_ais_data(
    bbox: str,
    start: datetime,
    slutt: datetime,
    min_fart: float = 0.5,
) -> dict:
  
    url = f"{innstillinger.ais_api_grunn_url}/positions/within-bbox-time"

    # vite hvor og når vi vil hente skip
    foresporsel_data = {
        "bbox": bbox,
        "start": formater_tidspunkt(start),
        "end": formater_tidspunkt(slutt),
        "minSpeed": min_fart,
    }