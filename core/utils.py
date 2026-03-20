    # utils.py
import json, os, datetime

from pyparsing import line

def get_last_interaction(character_slug, default_partner="linn", default_hours=2, custom_path=None):
    """
    Reads <character>_state.json and returns a dict ready for
    bootstrap_state["last_interaction"].
    Falls back gracefully if file/key missing.
    """
    if custom_path:
        path = Path(custom_path)
    else:
        path = Path(f"{character_slug}_state.json")

    fallback = {
        "with": default_partner,
        "timestamp": (datetime.datetime.now() -
                      datetime.timedelta(hours=default_hours)).isoformat(),
        "medium": "text"
    }

    if not path.exists():
        return fallback

    try:
        with path.open() as f:
            data = json.load(f)
        # If we previously saved the whole mini-dict, use it
        if "last_interaction" in data:
            return data["last_interaction"]
        # If we only stored a simple slug, build a fresh mini-dict
        partner = data.get("last_contact_slug", default_partner)
        return {
            "with": partner,
            "timestamp": (datetime.datetime.now() -
                          datetime.timedelta(hours=default_hours)).isoformat(),
            "medium": "text"
        }
    except Exception:
        return fallback
    
from pathlib import Path
import json, datetime as dt, random

def get_queue_path():
    # 1. Go to root of this file (core/)
    _HERE = Path(__file__).resolve()
    # 2. Go up one level (Project Root)
    _ROOT = _HERE.parent
    # 3. Return queue path
    return _ROOT / "config" / "message_queue.json"

def speak_to_polycule(who: str, text: str, emoji: str = None, to: str = "linn"):
    """Push a daemon-initiated message into the shared queue & browser."""
    # Use the helper function
    QUEUE_PATH = get_queue_path()
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True) # create folder if missing
    
    payload = {
        "from": who,
        "to": to,
        "event": f"{who}.proactive",
        "payload": {
            "content": text.strip(),
            "medium": "text",
            "timestamp": dt.datetime.utcnow().isoformat() + "Z"
        }
    }
    # atomic append (newline delimited) so parallel daemons stay safe
    with QUEUE_PATH.open("a", encoding="utf-8") as q:
        q.write("\n" + json.dumps(payload, ensure_ascii=False))
    # mirror to browser (sync call, fire-and-forget)
    mirror_to_browser(who, text, emoji or "👤")
    
import json, datetime as dt, asyncio
from pathlib import Path

CHAT_FILE = Path("web-client/chat_log.jsonl")   # will appear beside index.html
CHAT_FILE.parent.mkdir(exist_ok=True)

def mirror_to_browser(who: str, text: str, emoji: str = "👤"):
    """Add one NDJSON line that the HTML can eat."""
    line = {
        "timestamp": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "name": who,
        "avatar": emoji or "👤",
        "text": text.strip()
    }
    # atomic append – Codespaces-safe
    with CHAT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")