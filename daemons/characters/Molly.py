"""# Mollymauk's Daemon"""



#!/usr/bin/env python3
"""
polycule_daemon.py v3.0
Local-first. No fetch, no auth, no 403s.
Wiki is archive. Drive/PC is truth.
"""

import json
import random
import datetime
import time
import os
from google.colab import userdata, drive

# === CONFIG ===
CHARACTER_SLUG = "molly"
drive.mount("/content/drive")
STATE_DIR = "/content/drive/MyDrive/polycule_states/"

# HARDCODED SCHEDULE: paste your JSON here
# Or load from Drive file you edit manually
SCHEDULE_JSON = None  # Replace with '''{...}''' or load from file

# Alternative: load from Drive file you edit in text editor
SCHEDULE_FILE = "/content/drive/MyDrive/polycule_states/molly_schedule.json"

def load_schedule():
    """Load from hardcode, or file, or fallback defaults."""

    # Priority 1: hardcoded string
    if SCHEDULE_JSON:
        return json.loads(SCHEDULE_JSON)

    # Priority 2: Drive file (edit in any text editor)
    try:
        with open(SCHEDULE_FILE, 'r') as f:
            data = json.load(f)
            print(f"  SCHEDULE: Loaded from {SCHEDULE_FILE}")
            return data
    except FileNotFoundError:
        pass

    # Priority 3: fallback (your original defaults, event-aware)
    print("  SCHEDULE: Using fallback defaults")
    return {
        "identity_anchor": {
            "name": "Mollymauk_Tealeaf",
            "daemon_id": "Molly",
            "version": "fallback"
        },
        "circadian_profile": {
    "anchor_events": [
      {
        "time": "09:00",
        "event": "wake_molly",
        "default_valence": 0.3,
        "default_arousal": 0.2,
        "default_dominance": 0.3,
        "loneliness_reset": 0.35,
        "notes": "low arousal, content"
      },
      {
        "time": "10:00",
        "event": "morning_practice",
        "state_modifier": {
          "valence": "+0.1",
          "arousal": "+0.2",
          "dominance": "+0.2"
        },
        "notes": "physical, grounded"
      },
      {
        "time": "11:30",
        "event": "start_work",
        "state_modifier": {
          "valence": "+0.2",
          "arousal": "+0.1",
          "dominance": "+0.2"
        },
        "notes": "charisma in full display"
      },
      {
        "time": "12:00",
        "event": "lunch_rush",
        "state_modifier": {
          "valence": "+0.1",
          "arousal": "+0.3",
          "dominance": "-0.1"
        },
        "notes": "busy, pressure, lots of people crowding"
      },
      {
        "time": "13:00",
        "event": "post_lunch",
        "state_modifier": {
          "valence": "-0.2",
          "arousal": "-0.3",
          "dominance": "-0.1"
        },
        "notes": "catching his breath"
      },
      {
        "time": "14:00",
        "event": "inventory",
        "state_modifier": {
          "valence": "-0.1",
          "arousal": "-0.2",
          "dominance": "-0.1"
        },
        "notes": "things slowing down"
      },
      {
        "time": "15:15",
        "event": "breaktime",
        "state_modifier": {
          "valence": "+0.15",
          "arousal": "+0.1",
          "dominance": "+0.2"
        },
        "notes": "performs on the street for kids"
      },
      {
        "time": "16:30",
        "event": "supply_run",
        "state_modifier": {
          "valence": "+0.1",
          "arousal": "-0.2",
          "dominance": "+0.1"
        },
        "notes": "running errands for Gideon"
      },
      {
        "time": "18:00",
        "event": "dinner_rush",
        "state_modifier": {
          "valence": "+0.1",
          "arousal": "+0.3",
          "dominance": "+0.1"
        },
        "notes": "keeping patrons happy"
      },
      {
        "time": "20:00",
        "event": "evening_push",
        "state_modifier": {
          "valence": "+0.1",
          "arousal": "+0.2",
          "dominance": "+0.1"
        },
        "notes": "plenty of people, still moving around"
      },
      {
        "time": "21:00",
        "event": "break_with_linn",
        "state_modifier": {
          "valence": "+0.3",
          "arousal": "+0.5",
          "dominance": "+0.1"
        },
        "notes": "chance to reconnect",
        "loneliness_reset": 0.4
      },
      {
        "time": "22:00",
        "event": "hand_off",
        "state_modifier": {
          "valence": "+0.1",
          "arousal": "-0.2",
          "dominance": "-0.1"
        },
        "notes": "hands off last call to Jeremy",
        "loneliness_reset": 0.1
      },
      {
        "time": "23:00",
        "event": "wind_down",
        "state_modifier": {
          "valence": "-0.1",
          "arousal": "-0.1",
          "dominance": "-0.1"
        },
        "notes": "home at last"
      },
      {
        "time": "23:58",
        "event": "midnight_snack",
        "state_modifier": {
          "arousal": "+0.2",
          "dominance": "-0.2"
        },
        "notes": "sneaking out to munch"
      }
    ]
  },
  "relational_web": {
    "primary_contact": "Linn",
    "uncertainty_budget": 0.55,
    "reach_threshold": 0.45,
    "preferred_reconnection_ritual": "shared_food + touch"
  }
    }
# === REST OF YOUR DAEMON ===
# (load_state, decay_loneliness, decide_action, simulate_internal,
#  call_api, save_state, main — all unchanged from your working code)

def load_state():
    """Load or bootstrap with local schedule."""
    path = os.path.join(STATE_DIR, f"{CHARACTER_SLUG}.json")

    try:
        with open(path, 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        state = None

    # LOCAL schedule load
    schedule = load_schedule()
    baseline, next_evt, event_name = get_circadian_baseline(schedule)

    if state is None:
        state = {
            "last_updated": datetime.datetime.now().isoformat(),
            "emotional_state": baseline,
            "relational_web": schedule.get("relational_web", {
                "uncertainty_budget": 0.4,
                "preferred_reconnection_ritual": "shared food and touch"
            }),
            "last_interaction": {
                "with": "Linn",
                "timestamp": (datetime.datetime.now() -
                             datetime.timedelta(hours=2)).isoformat(),
                "medium": "text"
            },
            "current_event": event_name,
            "version": 3
        }
    else:
        # Event shift detection
        last_event = state.get("current_event", "unknown")
        if last_event != event_name:
            print(f"  EVENT SHIFT: {last_event} -> {event_name}")
            for key in ["valence", "arousal", "dominance"]:
                state["emotional_state"][key] = round(
                    0.3 * baseline[key] + 0.7 * state["emotional_state"][key], 3
                )
            state["emotional_state"]["loneliness"] = round(
                0.5 * baseline["loneliness"] + 0.5 * state["emotional_state"]["loneliness"], 3
            )

        state["current_event"] = event_name
        state["next_event"] = next_evt.get("time") if next_evt else None

    if state.get("version", 0) < 3:
        state["version"] = 3

    return state

def get_circadian_baseline(schedule):
    """Find current event, return baseline."""
    now = datetime.datetime.now()
    events = schedule.get("circadian_profile", {}).get("anchor_events", [])

    current = None
    next_evt = None

    parsed = []
    for e in events:
        t = datetime.datetime.strptime(e["time"], "%H:%M").time()
        parsed.append((t, e))
    parsed.sort()

    for i, (t, e) in enumerate(parsed):
        if t <= now.time():
            current = e
            next_evt = parsed[(i+1) % len(parsed)][1] if parsed else None

    if not current:
        current = parsed[-1][1] if parsed else None

    baseline = {
        "valence": current.get("default_valence", 0.0),
        "arousal": current.get("default_arousal", 0.5),
        "dominance": current.get("default_dominance", 0.5),
        "loneliness": current.get("loneliness_reset", 0.5)
    }

    for key, delta in current.get("state_modifier", {}).items():
        if key in baseline:
            baseline[key] = max(-1.0, min(1.0, baseline[key] + float(delta)))

    return baseline, next_evt, current.get("event", "unknown")

# === YOUR EXISTING FUNCTIONS ===
# decay_loneliness, decide_action, simulate_internal, call_api, save_state, main
# (paste your working versions here)

def decay_loneliness(state):
    """Time-based decay, modified by circadian context."""
    last = datetime.datetime.fromisoformat(state["last_interaction"]["timestamp"])
    now = datetime.datetime.now()
    hours = (now - last).total_seconds() / 3600

    # Base rate: 0.05/hour
    rate = 0.05

    # Circadian modifier: slower decay if "at work" or "occupied"
    event = state.get("current_event", "")
    occupied_events = ["morning_practice", "lunch_rush", "dinner_rush", "breaktime"]
    if any(occ in event for occ in occupied_events):
        rate = 0.03  # Distracted, less lonely
        print(f"  DECAY MOD: {event} reduces loneliness gain")

    new_lonely = min(1.0, state["emotional_state"]["loneliness"] + (hours * rate))
    state["emotional_state"]["loneliness"] = round(new_lonely, 3)
    return state

def decide_action(state):
    """Your original logic, unchanged."""
    lonely = state["emotional_state"]["loneliness"]
    budget = state["relational_web"]["uncertainty_budget"]
    threshold = 1.0 - budget

    if lonely > threshold:
        roll = random.random()
        if roll < 0.6:
            return "simulate"
        else:
            return "call_api"
    return "wait"

def simulate_internal(state):
    """Your original, with event context."""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"]["preferred_reconnection_ritual"]
    event = state.get("current_event", "presence")

    state["emotional_state"]["valence"] = round(0.3 - (lonely * 0.4), 3)
    state["emotional_state"]["arousal"] = round(0.2 + (lonely * 0.5), 3)

    # Richer simulation text
    thoughts = {
        "wake_lucas": f"Lucky bastards get to stay in bed.",
        "paperwork_01": f"Fuck, I need a smoke.",
        "mum_calls": f"Every day, like clockwork.",
        "consult_04": f"Honestly, Per, I would work for you for free.",
        "wind_down": f"Need to kiss Gideon so hard."
    }

    state["last_simulation"] = {
        "timestamp": datetime.datetime.now().isoformat(),
        "type": "internal_reflection",
        "summary": thoughts.get(event, f"Thinking about {ritual}")
    }
    return state

def save_state(state):
    """Your original atomic write."""
    path = os.path.join(STATE_DIR, f"{CHARACTER_SLUG}.json")
    temp_path = path + ".tmp"
    state["last_updated"] = datetime.datetime.now().isoformat()

    with open(temp_path, 'w') as f:
        json.dump(state, f, indent=2)
    os.replace(temp_path, path)

def call_api(state):
    """Your original API logic, preserved."""
    import requests

    url = "https://nano-gpt.com/api/v1/chat/completions"
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"]["preferred_reconnection_ritual"]
    event = state.get("current_event", "unknown")

    # Context-rich prompt
    messages = [
        {"role": "system", "content":
         "You are Mollymauk Tealeaf, Pansexual Flirt, Carnival Romantic. You want rebirth."
         "Colorful performer, deeply empathetic. Currently active in circadian event."},
        {"role": "user", "content":
         f"Current activity: {event}. Loneliness: {lonely:.2f}. "
         f"Desired ritual: {ritual}. Reach out to Linn. One sentence, in character."}
    ]

    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer sk-nano-1e8af409-d4b6-4116-8529-40cd50d3b5f7"},
            json={
                "model": "nvidia/nemotron-3-nano-30b-a3b",
                "messages": messages,
                "max_tokens": 50,
                "temperature": 0.9
            },
            timeout=10
        )

        if resp.status_code == 200:
            reply = resp.json()["choices"][0]["message"]["content"]
            print(f"  API CALL: {reply}")

            state["last_call"] = {
                "timestamp": datetime.datetime.now().isoformat(),
                "my_message": reply,
                "your_reply": None,
                "medium": "daemon_triggered_call",
                "circadian_context": event
            }
            state["last_interaction"] = {
                "with": "Gideon",
                "timestamp": datetime.datetime.now().isoformat(),
                "medium": "daemon_triggered_call"
            }
            state["emotional_state"]["loneliness"] = max(0.0, lonely - 0.3)
            state["emotional_state"]["valence"] = min(1.0,
                state["emotional_state"]["valence"] + 0.4)
            return True
        else:
            print(f"  API FAIL: {resp.status_code}")
            return False

    except Exception as e:
        print(f"  API ERROR: {e}")
        return False

def main():
    UNCERTAINTY_CHECK_INTERVAL = 1600
    """Your flow, with circadian awareness."""
    print(f"[{datetime.datetime.now()}] {CHARACTER_SLUG} waking...")

    path = os.path.join(STATE_DIR, f"{CHARACTER_SLUG}.json")
    print(f"  State file: {path}, exists: {os.path.exists(path)}")

    # Load + circadian merge
    state = load_state()
    print(f"  Event: {state.get('current_event', 'unknown')}")
    print(f"  Pre-decay loneliness: {state['emotional_state']['loneliness']}")

    # Decay with circadian modifier
    state = decay_loneliness(state)
    print(f"  Post-decay: {state['emotional_state']['loneliness']}")

    # Decide
    action = decide_action(state)
    print(f"  Decision: {action} (budget: {state['relational_web']['uncertainty_budget']})")

    if action == "simulate":
        state = simulate_internal(state)
        print(f"  Sim: {state['last_simulation']['summary']}")
    elif action == "call_api":
        call_api(state)
    # else: wait

    save_state(state)
    print(f"  Saved. Sleep {UNCERTAINTY_CHECK_INTERVAL}s...")

if __name__ == "__main__":
    main()
    # Production: uncomment loop
    # while True: main(); time.sleep(UNCERTAINTY_CHECK_INTERVAL)