import json
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ── Tool schemas (sent to OpenAI) ────────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current date and time for a given city or timezone. If no city is provided, returns local time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name to get the time for, e.g. 'New York', 'London', 'Tokyo'.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Returns mock weather information for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city, e.g. London",
                    }
                },
                "required": ["city"],
            },
        },
    },
]

# ── Mock weather data ─────────────────────────────────────────────────────────

MOCK_WEATHER = {
    "london":   {"temperature": "15°C", "condition": "Cloudy",  "humidity": "78%"},
    "new york": {"temperature": "22°C", "condition": "Sunny",   "humidity": "55%"},
    "tokyo":    {"temperature": "28°C", "condition": "Humid",   "humidity": "80%"},
    "paris":    {"temperature": "18°C", "condition": "Rainy",   "humidity": "85%"},
    "sydney":   {"temperature": "20°C", "condition": "Clear",   "humidity": "60%"},
    "dubai":    {"temperature": "38°C", "condition": "Hot",     "humidity": "40%"},
    "dhaka":    {"temperature": "32°C", "condition": "Sunny",   "humidity": "70%"},
}

# ── Tool implementations ──────────────────────────────────────────────────────

CITY_TIMEZONES = {
    "new york":     "America/New_York",
    "los angeles":  "America/Los_Angeles",
    "chicago":      "America/Chicago",
    "london":       "Europe/London",
    "paris":        "Europe/Paris",
    "berlin":       "Europe/Berlin",
    "tokyo":        "Asia/Tokyo",
    "dubai":        "Asia/Dubai",
    "karachi":      "Asia/Karachi",
    "islamabad":    "Asia/Karachi",
    "lahore":       "Asia/Karachi",
    "dhaka":        "Asia/Dhaka",
    "sydney":       "Australia/Sydney",
    "toronto":      "America/Toronto",
    "singapore":    "Asia/Singapore",
    "hong kong":    "Asia/Hong_Kong",
    "mumbai":       "Asia/Kolkata",
    "delhi":        "Asia/Kolkata",
}


def get_current_time(city: str = None) -> dict:
    if city:
        key = city.strip().lower()
        tz_name = CITY_TIMEZONES.get(key)
        if not tz_name:
            return {"error": f"Timezone not found for '{city}'. Try: {', '.join(c.title() for c in CITY_TIMEZONES)}"}
        try:
            now = datetime.now(ZoneInfo(tz_name))
            location = city.title()
        except ZoneInfoNotFoundError:
            return {"error": f"Invalid timezone: {tz_name}"}
    else:
        now = datetime.now()
        location = "Local"

    return {
        "location": location,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day":  now.strftime("%A"),
        "timezone": now.strftime("%Z"),
    }


def get_weather(city: str) -> dict:
    key = city.strip().lower()
    if key not in MOCK_WEATHER:
        return {
            "error": f"Weather data not available for '{city}'. "
                     f"Try: {', '.join(c.title() for c in MOCK_WEATHER)}"
        }
    data = MOCK_WEATHER[key]
    return {"city": city.title(), **data}


# ── Dispatcher ────────────────────────────────────────────────────────────────

def execute_tool(name: str, arguments: str) -> str:
    """Parse arguments and call the matching tool. Returns JSON string."""
    try:
        args = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid tool arguments JSON: {e}"})

    try:
        if name == "get_current_time":
            result = get_current_time(city=args.get("city"))
        elif name == "get_weather":
            city = args.get("city")
            if not city:
                return json.dumps({"error": "'city' argument is required."})
            result = get_weather(city)
        else:
            result = {"error": f"Unknown tool: '{name}'"}
    except Exception as e:
        result = {"error": f"Tool execution failed: {e}"}

    return json.dumps(result)
