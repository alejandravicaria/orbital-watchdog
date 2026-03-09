import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'orbital'))

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from agent import run_agent

app = FastAPI(title="Orbital Watchdog")

class AnalyzeRequest(BaseModel):
    satellite_name: str

def fetch_tle_by_name(satellite_name: str) -> tuple:
    url = f"https://celestrak.org/NORAD/elements/gp.php?NAME={satellite_name}&FORMAT=TLE"
    headers = {"User-Agent": "orbital-watchdog/1.0 (educational project)"}
    response = requests.get(url, timeout=10, headers=headers)
    response.raise_for_status()
    lines = response.text.strip().splitlines()
    if len(lines) < 3:
        raise ValueError(f"Satellite '{satellite_name}' not found in CelesTrak")
    return lines[1].strip(), lines[2].strip()

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open(os.path.join(os.path.dirname(__file__), "index.html")) as f:
        return f.read()

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        tle_line1, tle_line2 = fetch_tle_by_name(request.satellite_name)
        result = run_agent(tle_line1, tle_line2)
        return {"status": "success", "report": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))