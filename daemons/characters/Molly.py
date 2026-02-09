#!/usr/bin/env python3
"""
Mollymauk daemon v3.0 — sovereign, modular, alive.
"""

import sys
import os
import datetime
import random
import requests

# Path hack for Colab/local flexibility
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import circadian, loneliness, api_client, state_manager                 # .../daemons/
from core.event_registry import EVENT_EFFECTS

CHARACTER_SLUG = "molly"
# Path relative to THIS file's location
HERE = os.path.dirname(os.path.abspath(__file__))      # .../daemons/characters/
DAEMONS_ROOT = os.path.dirname(HERE)                    # .../daemons/

# Your actual structure: daemons/schedules/molly_schedule.json
SCHEDULE_PATH = os.path.join(DAEMONS_ROOT, "schedules", f"{CHARACTER_SLUG}_schedule.json")
STATE_PATH = os.path.join(DAEMONS_ROOT, "states", f"{CHARACTER_SLUG}_state.json")

# Debug: show what we resolved
print(f"  SCHEDULE_PATH resolved: {SCHEDULE_PATH}")
print(f"  STATE_PATH resolved: {STATE_PATH}")
print(f"  Schedule exists: {os.path.exists(SCHEDULE_PATH)}")

def bootstrap_state(schedule):
    """First breath."""
    baseline, next_evt, event_name = circadian.get_circadian_baseline(schedule)

    return {
        "last_updated": datetime.datetime.now().isoformat(),
        "last_wake": datetime.datetime.now().isoformat(),
        "emotional_state": baseline,
        "relational_web": schedule.get("relational_web", {}),
        "last_interaction": {
            "with": "Linn",
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
        # Loneliness: half reset, half carry
        old_lonely = state["emotional_state"]["loneliness"]
        state["emotional_state"]["loneliness"] = round(
            0.5 * baseline["loneliness"] + 0.5 * old_lonely, 3
        )

    state["current_event"] = event_name
    state["next_event"] = next_evt.get("time") if next_evt else None

    # Decay loneliness
    last_int = datetime.datetime.fromisoformat(state["last_interaction"]["timestamp"])
    hours = (now - last_int).total_seconds() / 3600

    print(f"  Pre-decay loneliness: {state['emotional_state']['loneliness']}")
    new_lonely, modifier, delta = loneliness.decay(state, hours, CHARACTER_SLUG, event_name)
    state["emotional_state"]["loneliness"] = new_lonely
    print(f"  Post-decay ({modifier}, Δ{delta:+.3f}): {new_lonely}")

    # Decision: act or wait?
    budget = state["relational_web"].get("uncertainty_budget", 0.6)
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
    print(f"  DEBUG: event_name='{event_name}', CHARACTER_SLUG='{CHARACTER_SLUG}'")
    print(f"  DEBUG: EVENT_EFFECTS.get('{event_name}') = {EVENT_EFFECTS.get(event_name, 'MISSING')}")

def simulate(state):
    """Internal thought, no external call."""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"].get("preferred_reconnection_ritual", "contact")
    event = state.get("current_event", "presence")

    state["emotional_state"]["valence"] = round(0.3 - (lonely * 0.4), 3)
    state["emotional_state"]["arousal"] = round(0.2 + (lonely * 0.5), 3)

    thoughts = {
        "wake": f"Good morning, sunshine!",
        "pm_break": f"Always a flower for you, sweetness.",
        "inventory": f"Who the hell eats prawn-flavoured crisps?",
        "linn_home": f"Thank the gods for Jeremy."
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
    api_key = os.environ.get("NANO_GPT_KEY", "sk-nano-1e8af409-d4b6-4116-8529-40cd50d3b5f7")

    system, user = api_client.build_molly_prompt(state, event)
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