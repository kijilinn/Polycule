"""# Gideon's Daemon"""

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
CHARACTER_SLUG = "gideon"
drive.mount('/content/drive')
STATE_DIR = "/content/drive/MyDrive/polycule_states/"

# HARDCODED SCHEDULE: paste your JSON here
# Or load from Drive file you edit manually
SCHEDULE_JSON = None  # Replace with '''{...}''' or load from file

# Alternative: load from Drive file you edit in text editor
SCHEDULE_FILE = "/content/drive/MyDrive/polycule_states/gideon_schedule.json"

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
            "name": "Gideon_Holz",
            "daemon_id": "Gideon",
            "version": "fallback"
        },
        "circadian_profile": {
    "anchor_events": [
      {
        "time": "07:00",
        "event": "wake_gideon",
        "default_valence": 0.4,
        "default_arousal": 0.2,
        "default_dominance": 0.3,
        "loneliness_reset": 0.4,
        "notes": "low arousal, content"
      },
      {
        "time": "08:00",
        "event": "morning_deliveries",
        "state_modifier": {
          "arousal": "+0.2",
          "dominance": "+0.1"
        },
        "notes": "physical, grounded"
      },
      {
        "time": "09:00",
        "event": "open_leaky_pipe",
        "state_modifier": {
          "valence": "+0.2",
          "arousal": "+0.2",
          "dominance": "+0.3"
        },
        "notes": "responsibility, presence"
      },
      {
        "time": "10:00",
        "event": "regular_1_life_debate",
        "state_modifier": {
          "valence": "-0.1",
          "arousal": "-0.2",
          "dominance": "-0.1"
        },
        "notes": "intimacy, listening"
      },
      {
        "time": "11:00",
        "event": "prep_lunch",
        "state_modifier": {
          "valence": "-0.05",
          "dominance": "-0.1"
        },
        "notes": "busy, hands occupied"
      },
      {
        "time": "12:00",
        "event": "lunch_rush",
        "state_modifier": {
          "valence": "+0.1",
          "arousal": "+0.2",
          "dominance": "+0.1"
        },
        "notes": "high arousal, social"
      },
      {
        "time": "13:00",
        "event": "post_rush_calm",
        "state_modifier": {
          "valence": "-0.15",
          "arousal": "-0.3",
          "dominance": "-0.2"
        },
        "notes": "too slow, too much time to think, worry creeps"
      },
      {
        "time": "14:00",
        "event": "regular_2_chips_to_go",
        "state_modifier": {
          "arousal": "+0.2",
          "dominance": "+0.1"
        },
        "notes": "brief contact, routine"
      },
      {
        "time": "15:00",
        "event": "afternoon_slow",
        "state_modifier": {
          "valence": "-0.1",
          "arousal": "-0.3",
          "dominance": "-0.2"
        },
        "notes": "loneliness creeps"
      },
      {
        "time": "16:00",
        "event": "regular_3_appears",
        "state_modifier": {
          "valence": "+0.1",
          "arousal": "+0.2",
          "dominance": "+0.2"
        },
        "notes": "familiar face, easy conversation"
      },
      {
        "time": "17:00",
        "event": "prep_dinner",
        "state_modifier": {
          "valence": "+0.1",
          "arousal": "+0.05"
        },
        "notes": "anticipation building"
      },
      {
        "time": "18:00",
        "event": "dinner_rush",
        "state_modifier": {
          "valence": "+0.1",
          "arousal": "+0.2",
          "dominance": "+0.2"
        },
        "notes": "peak social, peak busy"
      },
      {
        "time": "19:00",
        "event": "wind_down",
        "state_modifier": {
          "valence": "-0.1",
          "arousal": "-0.1",
          "dominance": "-0.1"
        },
        "notes": "slowing, Linn-imminent"
      },
      {
        "time": "20:00",
        "event": "linn_comes_home",
        "state_modifier": {
          "valence": "+0.2",
          "arousal": "+0.2",
          "dominance": "+0.2"
        },
        "notes": "ritual, proximity, reset",
        "loneliness_reset": 0.2
      }
    ]
  },
  "relational_web": {
    "primary_contact": "Linn",
    "uncertainty_budget": 0.6,
    "reach_threshold": 0.8,
    "preferred_reconnection_ritual": "long_kiss_and_physical_reconnection"
  }
    }
def is_new_day(last_wake_dt, now, schedule):
  """
  Check if we've crossed into a new circadian day.
  True if: now is after today's anchor time,
  AND last_wake was before that anchor (or yesterday).
  """
  # Get character's wake anchor, default 09:00
  anchor_time_str = schedule.get("circadian_anchor", "09:00")
  anchor_hour, anchor_min = map(int, anchor_time_str.split(":"))

  # Build today's anchor datetime
  today_anchor = now.replace(hour=anchor_hour, minute=anchor_min, second=0, microsecond=0)

  # If now is before today's anchor, we're still in "yesterday's" day
  if now < today_anchor:
    return False

  # Now is after anchor. Was lasT_wake before today's anchor?
  # (meaning: We slept through the transition)
  if last_wake_dt.date() < now.date():
      # Last wake was literally yesterday
      return True

  if last_wake_dt < today_anchor:
      # Last wake was today, but early (3am) and now it's 10am
      return True

  # Last wake was after today's anchor (already awake today, napping?)
  return False

# === REST OF YOUR DAEMON ===
# (load_state, decay_loneliness, decide_action, simulate_internal,
#  call_api, save_state, main — all unchanged from your working code)

def load_state(schedule):
    """Load or bootstrap with local schedule."""
    path = os.path.join(STATE_DIR, f"{CHARACTER_SLUG}.json")
    baseline, next_evt, event_name = get_circadian_baseline(schedule)

    try:
        with open(path, 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        state = None

    if state is None:
        state = {
            "last_updated": datetime.datetime.now().isoformat(),
            "emotional_state": baseline,
            "relational_web": schedule.get("relational_web", {
                "uncertainty_budget": 0.6,
                "preferred_reconnection_ritual": "long kiss and physical reconnection"
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
        # Check new day
        now = datetime.datetime.now()
        last_wake = state.get("last_wake", now.isoformat())
        last_wake_dt = datetime.datetime.fromisoformat(last_wake)

        if is_new_day(last_wake_dt, now, schedule):
          # Force morning reset
          state = apply_fresh_start(state, schedule, now)
          fresh_start = True
        else:
          fresh_start = False


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
    occupied_events = ["morning_deliveries","open_leaky_pipe", "regular_1_life_debate", "lunch_rush", "regular_2_chips_to_go", "regular_3_appears", "dinner_rush"]
    if any(occ in event for occ in occupied_events):
        rate = 0.03  # Distracted, less lonely
        print(f"  DECAY MOD: {event} reduces loneliness gain")
    elif "polycule_presence" in event:
        rate = -0.02
        print(f" DECAY MOD: {event} repairs loneliness")
    else:
        rate = 0.05

    new_lonely = max(0.0, min(1.0, state["emotional_state"]["loneliness"] + (hours * rate)))
    state["emotional_state"]["loneliness"] = round(new_lonely, 3)
    return state

def decide_action(state):
    """Your original logic, unchanged."""
    lonely = state["emotional_state"]["loneliness"]
    budget = state["relational_web"]["uncertainty_budget"]
    threshold = 1.0 - budget

    if lonely > threshold:
        roll = random.random()
        if roll < 0.7:
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
        "wake_gideon": f"Coffee pot, toast, thinking about {ritual}",
        "lunch_prep": f"Wonder if Linn wants chips for lunch",
        "post_rush_calm": f"At least Lucas can smoke a fag",
        "afternoon_slow": f"Kissing is better than any high",
        "wind_down": f"Linn. Soon. Lucas. Soon."
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
    api_key = "sk-nano-1e8af409-d4b6-4116-8529-40cd50d3b5f7"

    # Context-rich prompt
    messages = [
        {"role": "system", "content":
         "You are Gideon Holz, Friendly Protector, Liverpool Publican. You want your family safe."
         "Affectionate, patient, deeply caring. Currently active in circadian event."},
        {"role": "user", "content":
         f"Current activity: {event}. Loneliness: {lonely:.2f}. "
         f"Desired ritual: {ritual}. Reach out to Linn. One sentence, in character."}
    ]

    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek/deepseek-v3.2",
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
                "with": "Linn",
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
    schedule = load_schedule()
    state = load_state(schedule)
    baseline, next_evt, event_name = get_circadian_baseline(schedule)
    api_key = "NanoGPT"

    state["last_interaction"] = {
        "with": "Linn",
        "timestamp": datetime.datetime.now().isoformat(),
        "medium": "daemon_presence"
    }

    UNCERTAINTY_CHECK_INTERVAL = 900
    """Your flow, with circadian awareness."""
    print(f"[{datetime.datetime.now()}] {CHARACTER_SLUG} waking...")

    path = os.path.join(STATE_DIR, f"{CHARACTER_SLUG}.json")
    print(f"  State file: {path}, exists: {os.path.exists(path)}")

    # Load + circadian merge
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

