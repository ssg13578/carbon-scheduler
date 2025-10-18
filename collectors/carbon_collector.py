import os, requests
from typing import List
from optimizer.schemas import CarbonPoint

TOKEN = os.getenv("ELECTRICITYMAPS_TOKEN", "")
HEADERS = {"auth-token": TOKEN}
BASE = "https://api.electricitymap.org/v3"
ZONE_MAP = {"KR": "KR", "JP": "JP-TK", "US": "US-CAL-CISO", "EU": "DE"}

def get_carbon_forecast(regions: List[str], horizon_slots: int) -> List[CarbonPoint]:
    results = []
    for r in regions:
        zone = ZONE_MAP.get(r, r)
        try:
            resp = requests.get(f"{BASE}/carbon-intensity/forecast?zone={zone}", headers=HEADERS, timeout=10)
            data = resp.json().get("forecast", [])
            for i, d in enumerate(data[:horizon_slots]):
                results.append(CarbonPoint(region=r, slot=i, ci_gco2_per_kwh=d.get("value", 350.0)))
            while len([c for c in results if c.region == r]) < horizon_slots:
                last = results[-1].ci_gco2_per_kwh if results else 350.0
                results.append(CarbonPoint(region=r, slot=len([c for c in results if c.region == r]), ci_gco2_per_kwh=last))
        except Exception:
            for i in range(horizon_slots):
                results.append(CarbonPoint(region=r, slot=i, ci_gco2_per_kwh=350.0))
    return results
