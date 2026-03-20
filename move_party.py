import argparse
import json
import pathlib
import datetime

def main():
    parser = argparse.ArgumentParser(description="Move Polycule members to a new location.")
    parser.add_argument("--chars", required=True, help="Comma-separated list of slugs (e.g., gideon,lucas)")
    parser.add_argument("--region", required=True, help="Region ref (e.g., us_florida)")
    parser.add_argument("--location", required=True, help="Specific venue (e.g., jack_bruno_villa)")
    parser.add_argument("--status", default="home", choices=["home", "in_transit", "work"], help="Status of travel")

    args = parser.parse_args()

    # 1. Setup Paths
    _HERE = pathlib.Path(__file__).resolve().parent
    chars_dir = _HERE / "characters"

    # 2. Parse Slugs
    slugs = [s.strip() for s in args.chars.split(",")]

    print(f"🧭 **MOVE PARTY INITIATED** 🧭")
    print(f"   Destination: {args.location} ({args.region})")
    print(f"   Passengers:   {slugs}")

    # 3. Update Manifests
    for slug in slugs:
        manifest_path = chars_dir / slug / "manifest.json"

        if not manifest_path.exists():
            print(f"❌ ERROR: Manifest not found for {slug}")
            continue

        try:
            # Load
            with manifest_path.open("r+") as f:
                data = json.load(f)

                # Modify
                data["world_config"]["location_override"] = True
                data["world_config"]["current_location"] = {
                    "region_ref": args.region,
                    "specific_venue": args.location,
                    "status": args.status,
                    "geo_access": "public"
                }

                # Add metadata for debugging/history
                if "move_history" not in data["world_config"]:
                    data["world_config"]["move_history"] = []

                data["world_config"]["move_history"].append({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "from": data["world_config"]["current_location"].get("specific_venue", "Unknown"),
                    "to": args.location,
                    "reason": "admin_command"
                })

                # Write back (seek to start to overwrite)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()

            print(f"✅ {slug} moved to {args.location}.")

        except Exception as e:
            print(f"💥 CRASH: Failed to move {slug}: {e}")

    print(f"\n🧭 **OPERATION COMPLETE** 🧭")

if __name__ == "__main__":
    main()