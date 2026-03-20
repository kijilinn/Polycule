import pathlib
import json
import datetime

# Locate the Repo Root (Same logic as Daemon)
_HERE = pathlib.Path(__file__).resolve()
for p in _HERE.parents:
    if (p / "core").is_dir():
        REPO_ROOT = p
        break
else:
    raise RuntimeError("repo-root not found")

CHARACTERS_DIR = REPO_ROOT / "characters"

def scan_locations():
    """
    Polls all state.json files and returns a list of 
    who is where and what they are doing.
    """
    report = []

    # Check all folders in /characters/
    for char_folder in CHARACTERS_DIR.iterdir():
        if not char_folder.is_dir():
            continue # Skip files, only want folders

        state_file = char_folder / "state.json"
        if not state_file.exists():
            continue # No daemon / offline

        # Load State
        try:
            with state_file.open() as f:
                state = json.load(f)
        except json.JSONDecodeError:
            continue # Corrupt file, skip

        # Extract Key Data
        slug = char_folder.name
        location = state.get("current_location", {}).get("specific_venue", "UNKNOWN")
        event = state.get("current_event", "UNKNOWN")
        loneliness = state.get("emotional_state", {}).get("loneliness", 0.0)
        last_update = state.get("last_updated", "Never")

        # Add to Report
        report.append({
            "slug": slug,
            "location": location,
            "event": event,
            "loneliness": loneliness,
            "last_seen": last_update
        })

    return report

if __name__ == "__main__":
    # 1. Run Scan
    data = scan_locations()

    # 2. Sort by Location (Group them up)
    data.sort(key=lambda x: x["location"])

    # 3. Print to Console (You can also dump to JSON)
    print(f"\n🌍 POLYCULE MAP SCAN - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)

    current_loc = "VOID"
    for entry in data:
        # Print Location Header if changed
        if entry["location"] != current_loc:
            current_loc = entry["location"]
            print(f"\n📍 {current_loc}")
            print("-" * 40)

        # Print Character Data
        print(f"  [{entry['loneliness']:.2f}] {entry['slug'].ljust(15)} | {entry['event']}")