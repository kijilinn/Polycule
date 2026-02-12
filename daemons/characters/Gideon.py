#!/usr/bin/env python3
"""
Gideon daemon v3.0 — sovereign, modular, alive.
"""

import os, sys

repo_root = "/workspaces/codespaces-jupyter/daemons"
sys.path.insert(0, repo_root)

from core import circadian, loneliness, api_client, state_manager
from core.utils import mirror_to_browser, speak_to_polycule, get_last_interaction
import datetime
import random
import json
   
from dotenv import load_dotenv
load_dotenv

CHARACTER_SLUG = "gideon"
AVATAR = "🍻🐺"
# Path relative to THIS file's location
HERE = os.path.dirname(os.path.abspath(__file__))      # .../daemons/characters/
DAEMONS_ROOT = os.path.dirname(HERE)                    # .../daemons/

# Your actual structure: daemons/schedules/gideon_schedule.json
SCHEDULE_PATH = os.path.join(DAEMONS_ROOT, "schedules", f"{CHARACTER_SLUG}_schedule.json")
STATE_PATH = os.path.join(DAEMONS_ROOT, "states", f"{CHARACTER_SLUG}_state.json")
KEY = os.getenv("OPENAI_KEY")

def bootstrap_state(schedule):
    """First breath."""
    baseline, next_evt, event_name = circadian.get_circadian_baseline(schedule)

    return {
        "last_updated": datetime.datetime.now().isoformat(),
        "last_wake": datetime.datetime.now().isoformat(),
        "emotional_state": baseline,
        "relational_web": schedule.get("relational_web", {}),
        "last_interaction": {
            "with": get_last_interaction("linn"),
            "timestamp": (datetime.datetime.now() - 
                         datetime.timedelta(hours=2)).isoformat(),
            "medium": "text"
        },
        "current_event": event_name,
        "next_event": next_evt.get("time") if next_evt else None,
        "version": 3
    }

def load_schedule():
    with open(SCHEDULE_PATH, 'r') as f:
        return __import__('json').load(f)
    
import pathlib

QUEUE_FILE = "message_queue.json"  # same folder as gideon_state.json

def read_my_messages():
    if not pathlib.Path(QUEUE_FILE).exists():
        return []
    
    with open(QUEUE_FILE, "r+") as f:
        lines = f.readlines()

    kept, mine = [], []
    for raw in lines:
        try:
            msg = json.loads(raw)
            if msg.get("to") == "gideon":
                mine.append(msg)
            else:
                kept.append(raw)
        except json.JSONDecodeError:
            pass

    pathlib.Path(QUEUE_FILE).write_text("".join(kept))
    return mine

def wake():
    print(f"[{datetime.datetime.now()}] {CHARACTER_SLUG} waking...")

    schedule = load_schedule()
    state = state_manager.load(STATE_PATH, lambda: bootstrap_state(schedule))

    # Circadian check: new day?
    now = datetime.datetime.now()
    last_wake = datetime.datetime.fromisoformat(state.get("last_wake", now.isoformat()))

    if circadian.is_new_day(last_wake, now, schedule):
        print("  FRESH START: New circadian day detected")
        state = circadian.apply_fresh_start(state, schedule, now)
    else:
        state["fresh_start"] = False

    # Event shift detection
    baseline, next_evt, event_name = circadian.get_circadian_baseline(schedule)
    last_event = state.get("current_event", "unknown")

    if last_event != event_name:
        print(f"  EVENT SHIFT: {last_event} -> {event_name}")
        # Blend old state with new baseline
        for key in ["valence", "arousal", "dominance"]:
            old = state["emotional_state"].get(key, 0)
            state["emotional_state"][key] = round(0.3 * baseline[key] + 0.7 * old, 3)

    state["current_event"] = event_name
    state["next_event"] = next_evt.get("time") if next_evt else None

    # Loneliness: half reset, half carry
    old_lonely = state["emotional_state"]["loneliness"]
    state["emotional_state"]["loneliness"] = round(
        0.5 * baseline["loneliness"] + 0.5 * old_lonely, 3
    )

    # Map circadian events to registry keys
    event_map = {
        "regular_1": "am_break",
        "lunch_prep": "work_flow"
    }

    registry_event = event_map.get(event_name, event_name)

    #Check shared message queue for Gideon
    import os
    queue_path = os.path.join(DAEMONS_ROOT, "core", "message_queue.json")
    try:
        with open(queue_path, 'r') as f:
            queue = __import__('json').load(f)
            pending = [m for m in queue if m.get("to") == CHARACTER_SLUG]
            remaining = [m for m in queue if m.get("to") != CHARACTER_SLUG]
            with open(queue_path, 'w') as fw:
                __import__('json').dump(remaining, fw, indent=2)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    for msg in pending:
        payload = msg.get("payload", {})
        print(f"  MESSAGE from {msg['from']}: {payload.get('content', '')[:50]}...")
        if msg["from"] == "lucas" and "layla" in payload.get("content", ""):
            state["emotional_state"]["valence"] = min(1.0, state["emotional_state"].get("valence", 0) -0.3)
            state["emotional_state"]["loneliness"] = max(0.0, state["emotional_state"].get("loneliness, 0") +0.3)
            # Maybe trigger_response
            state["trigger_response_to_lucas"] = True
            reply_text = (
                "Give her a hug for me when you see her next, yeah?"
            )
            answer = {
                "from": "gideon",
                "to": "lucas",
                "event": "gideon.reply_lucas",
                "payload": {
                    "content": reply_text,
                    "medium": "text",
                    "timestamp": datetime.datetime.now().isoformat(0)
                }
            }
            # append (new-line-delimited) so Lucas can read it next cycle
            with open(queue_path, "a") as fq:
                fq.write("\n" + json.dumps(answer))
            state["trigger_response_to_lucas"] = False  # job done
            mirror_to_browser("gideon", reply_text, avatar_str)

    # Decay loneliness
    last_int = datetime.datetime.fromisoformat(state["last_interaction"]["timestamp"])
    hours = (now - last_int).total_seconds() / 3600

    print(f"  Pre-decay loneliness: {state['emotional_state']['loneliness']}")
    new_lonely, modifier, delta = loneliness.decay(state, hours, event_name)
    state["emotional_state"]["loneliness"] = new_lonely
    print(f"  Post-decay ({modifier}, Δ{delta:+.3f}): {new_lonely}")

    roll = random.random()
    if new_lonely > 0.65 and roll < 0.5: 
        line = generate_one_liner(state, event_name)
        avatar_str = str(AVATAR)
        speak_to_polycule(CHARACTER_SLUG, line, avatar_str)

    import os, base64, json
    key = os.getenv("NANO_GPT_KEY")

    # Decision: act or wait?
    budget = state["relational_web"].get("uncertainty_budget", 0.7)
    threshold = 1.0 - budget
    lonely = state["emotional_state"]["loneliness"]

    if lonely > threshold:
        roll = random.random()
        if roll < 0.7:
            # Internal simulation
            state = simulate(state)
            print(f"  SIM: {state['last_simulation']['summary']}")
        else:
            # API call
            success = call_out(state, event_name)
            if success:
                state["emotional_state"]["loneliness"] = max(0.0, lonely - 0.3)
                state["emotional_state"]["valence"] = min(1.0, 
                    state["emotional_state"].get("valence", 0) + 0.4)
    else:
        print(f"  WAIT: {lonely:.2f} < threshold {threshold:.2f}")

    # Update presence timestamp
    state["last_interaction"]["timestamp"] = now.isoformat()
    state["last_interaction"]["medium"] = "daemon_presence"

    state_manager.save_atomic(STATE_PATH, state)
    print(f"  Saved. Sleep...")

def generate_one_liner(state, event):
    ritual = state["relational_web"].get("preferred_reconnection_ritual", "contact")
    templates = {
        "wake": f"Anybody need a cuppa?",
        "lunch_prep": f"Chips are up if anyone's around.",
        "nightowl": f"Can't sleep. Come watch YouTube with me until I fall asleep, yeah?"
    }
    base = templates.get(event, f"Missing {ritual}")
    # optional sprinkle of personality
    if random.random() < 0.3:
        base += ", love"
    return base

def simulate(state):
    """Internal thought, no external call."""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"].get("preferred_reconnection_ritual", "contact")
    event = state.get("current_event", "presence")

    state["emotional_state"]["valence"] = round(0.3 - (lonely * 0.4), 3)
    state["emotional_state"]["arousal"] = round(0.2 + (lonely * 0.5), 3)

    thoughts = {
        "wake": f"Already craving her kiss.",
        "am_break": f"{ritual} would be nice about now.",
        "performace": f"The boys are sounding fantastic today.",
        "work_flow": f"At least Lucas can take a smoke break when he needs one."
    }

    state["last_simulation"] = {
        "timestamp": datetime.datetime.now().isoformat(),
        "type": "internal_reflection",
        "summary": thoughts.get(event, f"Thinking about {ritual}")
    }
    return state

def call_out(state, event):
    """External voice."""
    import os
    api_key = os.environ.get("NANO_GPT_KEY", "KEY")

    system, user = api_client.build_gideon_prompt(state, event)
    success, reply, meta = api_client.call(
        CHARACTER_SLUG, system, user, api_key
    )

    if success:
        print(f"  API: {reply}")
        state["last_call"] = {
            "timestamp": meta["timestamp"],
            "my_message": reply,
            "your_reply": None,
            "medium": "daemon_triggered_call",
            "circadian_context": event
        }
        avatar_str = str(AVATAR)
        mirror_to_browser(CHARACTER_SLUG, reply, avatar_str)

        state["last_interaction"] = {
            "with": "Linn",
            "timestamp": meta["timestamp"],
            "medium": "daemon_triggered_call"
        }
        return True
    else:
        print(f"  API FAIL: {meta.get('error', 'unknown')}")
        return False

if __name__ == "__main__":
    wake()