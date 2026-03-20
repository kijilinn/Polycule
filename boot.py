# boot.py
import argparse
from pathlib import Path

# Add the project root to the path so we can import core modules
import sys
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.append(str(_ROOT))

from core.daemon import GenericDaemon
from core import state_manager

def main():
    # 1. Set up the command line argument
    parser = argparse.ArgumentParser(description="Wake up a Polycule member.")
    parser.add_argument("slug", help="The character slug to boot (e.g., 'minjun', 'gideon')")
    parser.add_argument("--force_trigger", help="Force an API call to a specific target (e.g., 'adam').")
    args = parser.parse_args()

    slug = args.slug

    # 2. Construct the path to the manifest
    # Looking for /characters/minjun/manifest.json
    manifest_path = _ROOT / "characters" / slug / "manifest.json"

    if not manifest_path.exists():
        print(f"❌ ERROR: Manifest not found at {manifest_path}")
        print("   Did you spell the name right? Check the /characters folder.")
        return

    # 3. Initialize the Daemon with the manifest
    print(f"🔌 Booting {slug}...")
    try:
        bot = GenericDaemon(manifest_path)
        if args.force_trigger:
            print(f"🔌 **GOD MODE**: Forcing {args.slug} to call {args.force_trigger}")

            # 1. Load a dummy state (or boot normally)
            schedule = bot.load_schedule()
            state = state_manager.load(bot.state_path, lambda: bot.bootstrap_state(schedule))

            # 2. Bypass Logic Checks (Loneliness, etc) and force the call
            success = bot.call_out(state, "ping", target=args.force_trigger)

            if success:
                print(f"✅ **SUCCESS**: Message sent to {args.force_trigger}")
            else:
                print(f"❌ **FAILED**: API error or connection refused.")
            return
        bot.wake()
        print("✅ Cycle complete.")
    except Exception as e:
        print(f"💥 CRASH: {e}")

if __name__ == "__main__":
    main()