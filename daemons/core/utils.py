    # utils.py
import json, os, datetime

def get_last_interaction(character_slug, default_partner="linn", default_hours=2):
    """
    Reads <character>_state.json and returns a dict ready for
    bootstrap_state["last_interaction"].
    Falls back gracefully if file/key missing.
    """
    path = f"{character_slug}_state.json"
    fallback = {
        "with": default_partner,
        "timestamp": (datetime.datetime.now() -
                      datetime.timedelta(hours=default_hours)).isoformat(),
        "medium": "text"
    }

    if not os.path.exists(path):
        return fallback

    try:
        with open(path) as f:
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