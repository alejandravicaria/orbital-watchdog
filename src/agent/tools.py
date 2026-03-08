import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'orbital'))

from tle_fetcher import fetch_debris_tles
from conjunction import find_conjunctions
from sgp4.api import Satrec
from datetime import datetime, timezone


def fetch_and_screen(tle_line1: str, tle_line2: str, hours: int = 24) -> dict:
    my_satrec = Satrec.twoline2rv(tle_line1, tle_line2)
    tles = fetch_debris_tles()
    conj = find_conjunctions(my_satrec,tles,hours=24,time_step_seconds=60,warning_threshold_km=1000.0)
    return {
        "satellite_name": "User Satellite",
        "conjunctions": conj,
        "hours_analyzed": hours
    }

def assess_risk(min_distance_km: float) -> dict:
    if min_distance_km < 5.0:
        return {"risk_level": "CRITICAL", "action": "immediate maneuver required"}
    elif min_distance_km < 50.0:
        return {"risk_level": "HIGH", "action": "maneuver planning required"}
    elif min_distance_km < 200.0:
        return {"risk_level": "MEDIUM", "action": "monitor closely, prepare contingency maneuver"}
    else:
        return {"risk_level": "LOW", "action": "monitor periodically"}

def generate_report(satellite_name: str, conjunctions: list, hours_analyzed: int) -> dict:
    risk_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    for c in conjunctions:
        risk_info = assess_risk(c["min_distance_km"])
        c["risk_level"] = risk_info["risk_level"]
        c["action"] = risk_info["action"]
    return {
        "satellite_name": satellite_name,
        "analysis_window_hours": hours_analyzed,
        "total_conjunctions": len(conjunctions),
        "highest_risk_level": max((c["risk_level"] for c in conjunctions), key=lambda r: risk_order.index(r)) if conjunctions else "NONE",
        "conjunctions": conjunctions,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
