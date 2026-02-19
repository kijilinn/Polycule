import json
import os
import datetime

def load(path, default_factory):
    """Load JSON or bootstrap with factory function."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default_factory()

def save_atomic(path, data):
    """Write to temp, then atomic replace."""
    temp_path = str(path) + '.tmp'
    data["last_updated"] = datetime.datetime.now().isoformat()

    with open(temp_path, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(temp_path, path)
    return True