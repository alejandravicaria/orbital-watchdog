import requests
from sgp4.api import Satrec


def fetch_debris_tles() -> list:
    # Cosmos 1408 debris cloud - Russian antisatellite test 2021
    url = "https://celestrak.org/NORAD/elements/gp.php?NAME=COSMOS%201408%20DEB&FORMAT=TLE"
    headers = {"User-Agent": "orbital-watchdog/1.0 (educational project)"}

    response = requests.get(url, timeout=10, headers=headers)
    response.raise_for_status()

    # FORMAT=TLE returns plain text, parse it into a list of TLEs
    tle_lines = response.text.strip().splitlines()

    debris_tles = []
    for i in range(0, len(tle_lines), 3):
        if i + 2 >= len(tle_lines):
            continue
        name = tle_lines[i].strip()
        line1 = tle_lines[i + 1].strip()
        line2 = tle_lines[i + 2].strip()
        try:
            satrec = Satrec.twoline2rv(line1, line2)
            debris_tles.append({
                "name": name,
                "line1": line1,
                "line2": line2,
                "satrec": satrec
            })
        except Exception as e:
            print(f"Error parsing TLE for {name}: {e}")

    return debris_tles


if __name__ == "__main__":
    tles = fetch_debris_tles()
    print(f"Fetched {len(tles)} debris TLEs")
    if tles:
        print(f"First object: {tles[0]['name']}")