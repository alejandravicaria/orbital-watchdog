TOOL_SCHEMAS = [
    {
        "name": "fetch_and_screen",
        "description": "Fetches live debris TLEs from CelesTrak and screens for conjunctions with the user's satellite",
        "input_schema": {
            "type": "object",
            "properties": {
                "tle_line1": {"type": "string", "description": "First line of the satellite TLE"},
                "tle_line2": {"type": "string", "description": "Second line of the satellite TLE"},
                "hours":     {"type": "integer", "description": "Hours to analyze, default 24"}
            },
            "required": ["tle_line1", "tle_line2"]
        }
    },
    {
        "name": "assess_risk",
        "description": "Assesses the risk of a conjunction based on its minimum distance",
        "input_schema": {
            "type": "object",
            "properties": {
                "min_distance_km": {"type": "number", "description": "Minimum distance in km"}
            },
            "required": ["min_distance_km"]
        }
    },
    {
        "name": "generate_report",
        "description": "Generates a comprehensive report of conjunction analysis results",
        "input_schema": {
            "type": "object",
            "properties": {
                "satellite_name": {"type": "string", "description": "Name of the user's satellite"},
                "conjunctions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the debris object"},
                            "min_distance_km": {"type": "number", "description": "Minimum distance in km"},
                            "closest_approach_time": {"type": "string", "description": "ISO timestamp of closest approach"},
                        },
                        "required": ["name", "min_distance_km", "closest_approach_time"]
                    }
                },
                "hours_analyzed": {"type": "integer", "description": "Number of hours analyzed"}
            },
            "required": ["satellite_name", "conjunctions", "hours_analyzed"]
        }

    }
]