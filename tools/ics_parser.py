import pathlib
import json
import datetime
import re

# --- CONFIG ---
ICS_FILE = pathlib.Path(__file__).parent / "Primary_Contacts.ics"
OUTPUT_DIR = pathlib.Path(__file__).parent / "characters"

# --- EMOTIONAL BASELINES (The "Default Feelings") ---
MOOD_BASELINES = {
    "idle-awake": { "valence": 0.5, "arousal": 0.3, "dominance": 0.5, "loneliness": 0.5 },
    "busy":       { "valence": 0.2, "arousal": 0.7, "dominance": 0.6, "loneliness": 0.7 },
    "asleep":     { "valence": 0.0, "arousal": 0.0, "dominance": 0.0, "loneliness": 0.0 },
    "dnd":        { "valence": 0.5, "arousal": 0.1, "dominance": 0.9, "loneliness": 0.1 }
}

def guess_category(event_title):
    """Simple heuristic to assign mood state from title."""
    title = event_title.lower()
    if any(x in title for x in ["work", "shift", "drills", "practice", "consult"]):
        return "busy"
    elif any(x in title for x in ["sleep", "nap"]):
        return "asleep"
    elif "dnd" in title:
        return "dnd"
    else:
        return "idle-awake"

def fuzzy_map_location(location_string):
    """Maps human locations to slugs."""
    if not location_string: return "polycule_flat"

    loc = location_string.lower()
    if "flat" in loc: return "uk_london/islington_band_flat"
    if "pipe" in loc: return "uk_london/islington_leaky_pipe"
    if "camden" in loc: return "uk_london/camden_music_shop"
    if "transit" in loc: return "uk_london/transit"
    return "uk_london/islington_band_flat" # Default

def parse_ics_rich():
    print(f"📂 Parsing {ICS_FILE}... (Rich Format)")

    if not ICS_FILE.exists():
        print(" ❌ ERROR: ICS file not found.")
        return

    with ICS_FILE.open(encoding="utf-8") as f:
        lines = f.readlines()

    events_by_name = {} # Name -> [List of Rich Events]
    name_match = re.compile(r"SUMMARY:([A-Za-z]+)")

    current_event = {}

    for line in lines:
        line = line.strip()

        if line.startswith("BEGIN:VEVENT"):
            current_event = {}
            continue

        if line.startswith("END:VEVENT"):
            if "summary" in current_event and "dtstart" in current_event:
                raw_name = name_match.search(current_event["summary"])
                if not raw_name: continue

                slug = raw_name.group(1).lower().replace(" ", "_").replace("-", "_")

                # 1. EXTRACT DATA
                time_str = current_event["dtstart"].strftime("%H:%M")
                event_title = current_event["summary"]
                location_string = current_event.get("location", "")

                # 2. DETERMINE STATE
                mood_state = guess_category(event_title)
                mood_data = MOOD_BASELINES[mood_state]

                # 3. BUILD RICH OBJECT
                rich_event = {
                    "name": event_title,
                    "time": time_str,
                    "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"], # Default to all days for now
                    "location": fuzzy_map_location(location_string),
                    "emotional_state": mood_data,
                    "description": f"{event_title}. {mood_state} state."
                }

                # 4. APPEND TO LIST
                if slug not in events_by_name:
                    events_by_name[slug] = []

                events_by_name[slug].append(rich_event)

            current_event = {}
            continue

        # PARSERS ...
        if line.startswith("SUMMARY:"):
            current_event["summary"] = line.replace("SUMMARY:", "")
        elif line.startswith("DTSTART"):
            try:
                val_str = line.split(":")[-1]
                current_event["dtstart"] = datetime.datetime.strptime(val_str, "%Y%m%dT%H%M%S")
            except: pass
        elif line.startswith("LOCATION"):
            current_event["location"] = line.replace("LOCATION:", "").strip()

    # 5. WRITE TO FILES
    print(f"  Found {len(events_by_name)} characters.")

    for slug, event_list in events_by_name.items():
        # Target Directory
        target_dir = OUTPUT_DIR / slug
        if not target_dir.exists():
            print(f"  ⚠️  Skipping {slug}: No folder.")
            continue

        # WRAP IN RICH STRUCTURE
        schedule_data = {
            "circadian_profile": {
                "timezone": "Europe/London",
                "anchor_events": event_list
            }
        }

        # Write
        out_file = target_dir / "schedule.json"
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(schedule_data, f, indent=2)
        print(f"  ✅ Wrote RICH schedule for: {slug}")

if __name__ == "__main__":
    parse_ics_rich()