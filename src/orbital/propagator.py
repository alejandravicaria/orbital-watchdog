from sgp4.api import Satrec, jday
from datetime import datetime, timezone

def get_position(satrec: Satrec, dt: datetime) -> tuple:
    jd, fr = jday(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    error, position, velocity = satrec.sgp4(jd, fr)
    if error != 0:
        raise ValueError(f"SGP4 error code: {error}")
    return position

if __name__ == "__main__":
    from tle_fetcher import fetch_debris_tles

    tles = fetch_debris_tles()
    now = datetime.now(timezone.utc)
    pos = get_position(tles[0]["satrec"], now)
    print(f"Object: {tles[0]['name']}")
    print(f"Position (km): x={pos[0]:.1f}, y={pos[1]:.1f}, z={pos[2]:.1f}")