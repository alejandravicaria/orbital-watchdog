import numpy as np
from datetime import datetime, timezone, timedelta
from sgp4.api import Satrec
from propagator import get_position

def find_conjunctions(
    my_satrec: Satrec,
    debris_list: list,
    hours: int = 24,
    time_step_seconds: int = 60,
    warning_threshold_km: float = 5.0
) -> list:
    now = datetime.now(timezone.utc)
    timestamps = []
    for i in range(0, hours * 3600 + 1, time_step_seconds):
        timestamps.append(now + timedelta(seconds=i))
    
    my_positions = {ts: get_position(my_satrec, ts) for ts in timestamps}

    for o in debris_list:
        for ts in timestamps:
            my_pos = my_positions[ts]
            debris_pos = get_position(o["satrec"], ts)

            distance_km = np.linalg.norm(np.array(my_pos) - np.array(debris_pos))
            if distance_km < o.get("min_distance_km", float('inf')):
                o["min_distance_km"] = distance_km
                o["closest_approach_time"] = ts

    results = [
        {
            "name": o["name"],
            "min_distance_km": round(o["min_distance_km"], 2),
            "closest_approach_time": o["closest_approach_time"].isoformat()
        }
        for o in debris_list
        if o["min_distance_km"] < warning_threshold_km
    ]
    results.sort(key=lambda x: x["min_distance_km"])
    return results

if __name__ == "__main__":
    import requests
    from sgp4.api import Satrec
    from tle_fetcher import fetch_debris_tles

    # fetch live ISS TLE
    url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
    headers = {"User-Agent": "orbital-watchdog/1.0 (educational project)"}
    response = requests.get(url, timeout=10, headers=headers)
    lines = response.text.strip().splitlines()
    my_satrec = Satrec.twoline2rv(lines[1].strip(), lines[2].strip())
    print(f"My satellite: {lines[0].strip()}")

    debris_list = fetch_debris_tles()
    print(f"Checking {len(debris_list)} debris objects over 24 hours...")

    results = find_conjunctions(
        my_satrec,
        debris_list,
        hours=24,
        time_step_seconds=60,
        warning_threshold_km=1000.0
    )

    print(f"\nFound {len(results)} conjunction(s):")
    for r in results:
        print(f"  {r['name']}: {r['min_distance_km']} km at {r['closest_approach_time']}")