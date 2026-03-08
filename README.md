# 🛰️ Orbital Watchdog

A space debris conjunction screener that combines real orbital mechanics with an agentic AI risk analyst — deployed as a serverless REST API on AWS Lambda.

---

## What It Does

Given a satellite's TLE (Two-Line Element set), the system:

1. **Fetches live debris TLEs** from CelesTrak's GP catalog (real tracked objects)
2. **Propagates all orbits forward** over a 24-hour window using the SGP4 algorithm
3. **Identifies conjunction events** — close approaches below a configurable distance threshold
4. **Assesses risk level** per conjunction (LOW / MEDIUM / HIGH / CRITICAL)
5. **Returns a structured risk report** via a REST API endpoint

An agentic AI layer (Claude + ReAct loop) orchestrates the analysis, calling tools autonomously and producing a human-readable summary alongside the structured output.

---

## Architecture

```
POST /analyze  (TLE input)
        │
        ▼
┌──────────────────┐
│   FastAPI (AWS   │
│   Lambda + APIGW)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   ReAct Agent    │  ← Claude (Anthropic SDK)
│   (agent.py)     │    tool_use loop
└────────┬─────────┘
         │
    ┌────┴──────────────────┐
    │                       │
    ▼                       ▼
fetch_and_screen()    generate_report()
    │
    ├── tle_fetcher.py      (CelesTrak REST API)
    ├── propagator.py       (SGP4 orbit propagation)
    └── conjunction.py      (min distance calculation)
         │
         ▼
    assess_risk()           (distance → risk level)

Optional:
    yolo_inference.py       (debris visual classification)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent framework | Anthropic SDK (Claude, native tool use) |
| Orbital mechanics | SGP4 (`sgp4` Python library) |
| Debris catalog | CelesTrak GP API (live data) |
| CV module | YOLOv8 (Ultralytics) |
| API | FastAPI |
| Deployment | AWS Lambda + API Gateway (Docker container) |
| Language | Python 3.11 |

---

## Project Structure

```
orbital-watchdog/
├── src/
│   ├── detector/
│   │   └── yolo_inference.py      # YOLO debris classification
│   ├── orbital/
│   │   ├── tle_fetcher.py         # CelesTrak TLE fetching
│   │   ├── propagator.py          # SGP4 orbit propagation
│   │   └── conjunction.py         # Close approach detection
│   ├── agent/
│   │   ├── tools.py               # Agent tool functions
│   │   ├── schemas.py             # Tool schemas for Claude
│   │   └── agent.py               # ReAct agent loop
│   └── api/
│       └── main.py                # FastAPI app
├── models/
│   └── yolov8n.pt                 # YOLO weights
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## Key Modules

### `tle_fetcher.py`
Fetches real TLE data from CelesTrak's GP API. Test case uses the **Cosmos 1408 debris cloud** — fragments from a 2021 Russian antisatellite test that created 1,500+ tracked objects and forced ISS crew to shelter.

### `propagator.py`
Wraps the SGP4 algorithm to compute ECI (Earth Centered Inertial) position vectors (x, y, z in km) for any tracked object at any future time.

### `conjunction.py`
Samples orbital positions every 60 seconds over a 24-hour window. For each debris object, records the minimum approach distance and the time it occurs. Optimized by caching the primary satellite's positions to avoid redundant computation.

**Example output (real data, ISS vs Cosmos 1408 debris):**
```
COSMOS 1408 DEB: 64.77 km at 2026-03-09T04:09:25 UTC  → MEDIUM risk
COSMOS 1408 DEB: 71.91 km at 2026-03-09T18:05:25 UTC  → MEDIUM risk
COSMOS 1408 DEB: 625.23 km at 2026-03-09T18:03:25 UTC → LOW risk
```

### `agent.py`
Implements a ReAct (Reason + Act) agent loop using the Anthropic SDK's native tool use. The agent autonomously decides which tools to call and in what order based on intermediate results — not a fixed pipeline.

**Risk classification:**
| Distance | Risk Level | Action |
|---|---|---|
| < 5 km | CRITICAL | Immediate maneuver required |
| 5–50 km | HIGH | Maneuver planning required |
| 50–200 km | MEDIUM | Monitor closely, prepare contingency |
| > 200 km | LOW | Monitor periodically |

---

## API Usage

```bash
curl -X POST https://<api-gateway-url>/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "tle_line1": "1 25544U 98067A   26068.50000000  .00001234  00000-0  12345-4 0  9999",
    "tle_line2": "2 25544  51.6400 123.4567 0001234  12.3456 347.6543 15.49812345"
  }'
```

**Response:**
```json
{
  "satellite_name": "User Satellite",
  "analysis_window_hours": 24,
  "total_conjunctions": 3,
  "highest_risk_level": "MEDIUM",
  "conjunctions": [
    {
      "name": "COSMOS 1408 DEB",
      "min_distance_km": 64.77,
      "closest_approach_time": "2026-03-09T04:09:25+00:00",
      "risk_level": "MEDIUM",
      "action": "monitor closely, prepare contingency maneuver"
    }
  ],
  "generated_at": "2026-03-08T21:00:00+00:00"
}
```

---

## Setup

```bash
git clone https://github.com/yourusername/orbital-watchdog
cd orbital-watchdog
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your ANTHROPIC_API_KEY
```

Run conjunction analysis directly:
```bash
python src/orbital/conjunction.py
```

Run the full agent:
```bash
python src/agent/agent.py
```

---

## Design Decisions

**Why SGP4 instead of numerical propagation?**
SGP4 is the industry standard for TLE-based orbit prediction. It's fast (analytical, not numerical), accurate enough for conjunction screening over 24-hour windows, and directly compatible with CelesTrak's data format.

**Why ReAct agent instead of a fixed pipeline?**
The agent can adapt based on results — if no conjunctions are found, it skips the report generation step. This mirrors how a real analyst would work, and makes the system extensible to more complex workflows (e.g. querying multiple debris catalogs, escalating to human review for CRITICAL events).

**Why Lambda instead of always-on server?**
Conjunction screening is request-driven, not continuous. Serverless keeps costs near zero at low traffic volumes and scales automatically during batch screening operations.

**Production upgrade path:**
Replace the YOLO label mapping with a model fine-tuned on the DIOr debris dataset. Replace the risk table with real collision probability calculations using high-fidelity TLEs and Monte Carlo methods — the same architecture supports both.

---

## Limitations (Prototype)

- Uses Cosmos 1408 debris only (CelesTrak rate limits during development). Production queries the full catalog of 25,000+ tracked objects.
- Risk table is heuristic. Production uses collision probability (Pc) calculations.
- YOLO model uses pretrained COCO weights with label mapping. Production fine-tunes on the DIOr debris imagery dataset.
- 60-second time step may miss very fast close approaches. Production uses adaptive step sizing.

---

## Background

Space debris is one of the defining infrastructure risks of the next decade. At LEO velocities (~7.7 km/s), even a 1cm fragment carries enough kinetic energy to disable a satellite. The Cosmos 1408 event alone added 1,500+ tracked fragments to an already congested orbital regime — and each one is a potential conjunction event for every satellite in a similar orbit.

This project is a prototype of the software layer that sits between raw tracking data and operator decisions.

---

*Built in one day as an interview preparation project.*