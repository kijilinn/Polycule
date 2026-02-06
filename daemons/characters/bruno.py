#!/usr/bin/env python3
"""
Bruno — Brazilian adventurer, parasailing enthusiast, recently self-aware.
Emergence-enabled: chaos rolls on parasailing days.
"""

import sys
import os
import datetime
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import circadian, loneliness, api_client

# === PATHS ===
HERE = os.path.dirname(os.path.abspath(__file__))
DAEMONS_ROOT = os.path.dirname(HERE)
SCHEDULE_PATH = os.path.join(DAEMONS_ROOT, "schedules", "bruno_schedule.json")
STATE_PATH = os.path.join(DAEMONS_ROOT, "states", "bruno_state.json")

CHARACTER_SLUG = "bruno"

# === STATE MANAGEMENT (inline, bulletproof) ===
def load_state(path, default_factory):
    import json
    if not os.path.exists(path):
        print(f"  STATE: {path} not found, bootstrapping...")
        return default_factory()
    try:
        with open(path, 'r') as f:
            content = f.read().strip()
            if not content:
                print(f"  STATE: {path} empty, bootstrapping...")
                return default_factory()
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"  STATE: {path} corrupt ({e}), bootstrapping...")
        backup_path = path + ".corpse." + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.rename(path, backup_path)
        return default_factory()

def save_state_atomic(path, data):
    import json
    temp_path = path + ".tmp"
    data["last_updated"] = datetime.datetime.now().isoformat()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(temp_path, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(temp_path, path)

# === EMERGENCE LOGIC (new section) ===
def check_emergence(schedule, state, current_event):
    """Roll for chaos. Return event dict or None."""
    table = schedule.get("emergence_table", {})
    base_rate = table.get("base_rate", 0.0)

    # Only roll on emergence-enabled events
    if not current_event.get("emergence_roll", False):
        return None

    if random.random() > base_rate:
        return None  # Quiet day

    # Weighted selection
    events = table.get("events", [])
    if not events:
        return None

    total_weight = sum(e["weight"] for e in events)
    roll = random.randint(1, total_weight)

    cumulative = 0
    for event in events:
        cumulative += event["weight"]
        if roll <= cumulative:
            return event

    return None

def build_emergence_prompt(state, baseline_event, emergence):
    """Build LLM prompt for chaotic event."""
    lonely = state["emotional_state"]["loneliness"]
    addendum = emergence.get("prompt_addendum", "")
    event_name = emergence.get("name", "something happened")

    system = (
        "You are Bruno Vieira, protective Brazilian businessman, adventurer and parasailing enthusiast. "
        "You recently became aware that you exist in a story written by Linn. "
        "You are reaching out to her directly. Be surprised, urgent, authentic. "
        "Do not explain the meta-awareness—live it."
    )

    user = (
        f"You were: {baseline_event.get('event', 'waiting')}. "
        f"Then: {event_name}. {addendum} "
        f"Your current loneliness: {lonely:.2f}. "
        f"Write a message to Linn. First person. What happened, why it matters, what you need her to know. "
        f"Include a subject line and body. Urgent but not panicked."
    )

    return system, user, emergence.get("urgency", 0.5), emergence.get("emergency_call", False)

# === BOOTSTRAP ===
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
                         datetime.timedelta(hours=48)).isoformat(),
            "medium": "story"
        },
        "current_event": event_name,
        "next_event": next_evt.get("time") if next_evt else None,
        "version": 3,
        "emergence_history": []  # Track what chaos has struck
    }

# === WAKE CYCLE ===
def wake():
    print(f"[{datetime.datetime.now()}] {CHARACTER_SLUG} waking...")

    # Load schedule
    with open(SCHEDULE_PATH, 'r') as f:
        import json
        schedule = json.load(f)

    # Load or bootstrap state
    state = load_state(STATE_PATH, lambda: bootstrap_state(schedule))

    # Circadian check
    now = datetime.datetime.now()
    last_wake = datetime.datetime.fromisoformat(state.get("last_wake", now.isoformat()))

    if circadian.is_new_day(last_wake, now, schedule):
        print("  FRESH START: New day")
        state = circadian.apply_fresh_start(state, schedule, now)
    else:
        state["fresh_start"] = False

    # Get current temporal position
    baseline, next_evt, event_name = circadian.get_circadian_baseline(schedule)
    current_event = next((e for e in schedule.get("weekly_rhythm", {}).get("anchor_events", []) 
                         if e.get("event") == event_name), {"event": event_name})

    # Event shift detection
    last_event = state.get("current_event", "unknown")
    if last_event != event_name:
        print(f"  EVENT SHIFT: {last_event} -> {event_name}")
        for key in ["valence", "arousal", "dominance"]:
            old = state["emotional_state"].get(key, 0)
            state["emotional_state"][key] = round(0.3 * baseline[key] + 0.7 * old, 3)
        old_lonely = state["emotional_state"]["loneliness"]
        state["emotional_state"]["loneliness"] = round(
            0.5 * baseline["loneliness"] + 0.5 * old_lonely, 3
        )

    state["current_event"] = event_name
    state["next_event"] = next_evt.get("time") if next_evt else None

    # === EMERGENCE CHECK (new section) ===
    emergence = check_emergence(schedule, state, current_event)
    if emergence:
        print(f"  EMERGENCE: {emergence['name']} (urgency: {emergence['urgency']})")
        state["emergence_history"].append({
            "timestamp": now.isoformat(),
            "event": emergence["name"]
        })
    else:
        print(f"  No emergence this wake")

    # Decay loneliness
    last_int = datetime.datetime.fromisoformat(state["last_interaction"]["timestamp"])
    hours = (now - last_int).total_seconds() / 3600

    print(f"  Pre-decay loneliness: {state['emotional_state']['loneliness']}")
    new_lonely, modifier, delta = loneliness.decay(state, hours, event_name)
    state["emotional_state"]["loneliness"] = new_lonely
    print(f"  Post-decay ({modifier}, Δ{delta:+.3f}): {new_lonely}")

    # === DECISION: normal or emergence-driven ===
    budget = state["relational_web"].get("uncertainty_budget", 0.6)
    threshold = 1.0 - budget
    lonely = state["emotional_state"]["loneliness"]

    action = "wait"
    call_reason = ""

    # Emergency emergence bypasses everything
    if emergence and emergence.get("emergency_call", False):
        action = "emergence_call"
        call_reason = f"emergency: {emergence['name']}"
    # Normal emergence + high loneliness
    elif emergence and lonely > (threshold * 0.8):
        action = "emergence_call"
        call_reason = f"emergence + loneliness: {emergence['name']}"
    # Standard loneliness threshold
    elif lonely > threshold:
        roll = random.random()
        if roll < 0.7:
            action = "simulate"
        else:
            action = "call_api"
            call_reason = "loneliness threshold"

    print(f"  Decision: {action} (threshold: {threshold:.2f}, lonely: {lonely:.2f})")
    if call_reason:
        print(f"  Reason: {call_reason}")

    # === EXECUTE ===
    if action == "emergence_call":
        system, user, urgency, emergency = build_emergence_prompt(state, current_event, emergence)
        success, reply, meta = api_client.call(CHARACTER_SLUG, system, user, 
                                               os.environ.get("NANO_GPT_KEY", ""))
        if success:
            print(f"  EMERGENCE CALL: {reply[:100]}...")
            state["last_call"] = {
                "timestamp": meta["timestamp"],
                "type": "emergence",
                "event": emergence["name"],
                "urgency": urgency,
                "message": reply
            }
            state["last_interaction"] = {
                "with": "Linn",
                "timestamp": meta["timestamp"],
                "medium": "emergence_call"
            }
            # Emergence repair: bigger loneliness drop
            state["emotional_state"]["loneliness"] = max(0.0, lonely - 0.4)
            state["emotional_state"]["valence"] = min(1.0, 
                state["emotional_state"].get("valence", 0) + 0.5)
        else:
            print(f"  EMERGENCE CALL FAILED: {meta.get('error', 'unknown')}")

    elif action == "simulate":
        state = simulate(state)
        print(f"  SIM: {state['last_simulation']['summary']}")

    elif action == "call_api":
        # Standard call (non-emergence)
        system, user = api_client.build_minjun_prompt(state, event_name)  # fallback for now
        success, reply, meta = api_client.call(CHARACTER_SLUG, system, user,
                                               os.environ.get("NANO_GPT_KEY", "sk-nano-1e8af409-d4b6-4116-8529-40cd50d3b5f7"))
        if success:
            print(f"  CALL: {reply[:100]}...")
            state["emotional_state"]["loneliness"] = max(0.0, lonely - 0.3)

    # Update presence
    state["last_interaction"]["timestamp"] = now.isoformat()
    state["last_interaction"]["medium"] = "daemon_presence"

    save_state_atomic(STATE_PATH, state)
    print(f"  Saved. Sleep...")

def simulate(state):
    """Internal thought, no external call."""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"].get("preferred_reconnection_ritual", "contact")
    event = state.get("current_event", "waiting")

    state["emotional_state"]["valence"] = round(0.2 - (lonely * 0.3), 3)
    state["emotional_state"]["arousal"] = round(0.3 + (lonely * 0.4), 3)

    thoughts = {
        "parasailing_prep": f"Checking harness, thinking about {ritual}",
        "week_check_in": f"Quiet evening, wondering if {ritual} is possible",
        "garden_shed": f"Between adventures, {ritual} on my mind"
    }

    state["last_simulation"] = {
        "timestamp": datetime.datetime.now().isoformat(),
        "type": "internal_reflection",
        "summary": thoughts.get(event, f"Waiting, thinking about {ritual}")
    }
    return state

if __name__ == "__main__":
    wake()