from datetime import datetime, timedelta, timezone
from pprint import pprint

import requests

from backend.config import innstillinger


def formater_tidspunkt(tidspunkt: datetime) -> str:
    #  tidspunkt på form
    return tidspunkt.strftime("%Y%m%d%H%M")


def hent_rå_ais_data(
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





  # Sender selve forespørselen til API-et
    svar = requests.post(
        url,
        json=foresporsel_data,
        timeout=innstillinger.foresporsel_timeout_sekunder,
    )

    # Hvis svar = feil, stopper programmet her
    svar.raise_for_status()

   
    return svar.json()


if __name__ == "__main__":
   #test
    slutt = datetime.now(timezone.utc)
    start = slutt - timedelta(hours=1)

    # test rundt Oslofjorden
    test_bbox = "10.50,59.70,10.90,60.00"

    data = hent_rå_ais_data(
        bbox=test_bbox,
        start=start,
        slutt=slutt,
    )


    print("Svar fra AIS-API:")
    print("success:", data.get("success"))
    print("melding:", data.get("msg"))

    punkter = data.get("data", [])
    print("antall punkter:", len(punkter))

   
    if punkter:
        print("\nFørste AIS-punkt:")
        pprint(punkter[0])
    else:
        print("\nIngen punkter funnet i dette tidsrommet.")