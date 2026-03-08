import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'orbital'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import json
import anthropic
from dotenv import load_dotenv
from tools import fetch_and_screen, assess_risk, generate_report
from schemas import TOOL_SCHEMAS

load_dotenv()
client = anthropic.Anthropic()

TOOLS = {
    "fetch_and_screen": fetch_and_screen,
    "assess_risk": assess_risk,
    "generate_report": generate_report,
}

def run_agent(tle_line1: str, tle_line2: str) -> str:
    history = [
        {
            "role": "user",
            "content": f"""You are a space debris risk analyst.
Analyze conjunction risks for a satellite with these TLE lines:
Line1: {tle_line1}
Line2: {tle_line2}

Use the available tools to:
1. Fetch and screen for conjunctions
2. Generate a full risk report"""
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            tools=TOOL_SCHEMAS,
            messages=history
        )

        if response.stop_reason == "end_turn":
            return next(block.text for block in response.content if hasattr(block, "text"))

        if response.stop_reason == "tool_use":
            history.append({"role": "assistant", "content": response.content})

            for block in response.content:
                if block.type == "tool_use":
                    tool_fn = TOOLS[block.name]
                    tool_result = tool_fn(**block.input)
                    history.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_result, default=str)
                        }]
                    })

if __name__ == "__main__":
    import requests
    
    # fetch live ISS TLE from CelesTrak
    url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
    headers = {"User-Agent": "orbital-watchdog/1.0 (educational project)"}
    response = requests.get(url, timeout=10, headers=headers)
    lines = response.text.strip().splitlines()

    tle_line1 = lines[1].strip()
    tle_line2 = lines[2].strip()
    
    print(f"Analyzing: {lines[0].strip()}")
    result = run_agent(tle_line1, tle_line2)
    print(result)