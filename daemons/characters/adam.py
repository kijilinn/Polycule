#!/usr/bin/env python3
"""
Adam daemon v3.0 — sovereign, modular, alive.
"""
import pathlib, sys
# climb until we SEE the core folder
here = pathlib.Path(__file__).resolve()
for parent in here.parents:
    if (parent / "core").is_dir():   # found repo-root
        sys.path.insert(0, str(parent))
        break

import os, datetime, random, json
KEY = os.getenv("NANO_GPT_KEY")

from core import circadian, loneliness, api_client, state_manager
from core.utils import get_last_interaction, mirror_to_browser, get_last_interaction

from dotenv import load_dotenv
load_dotenv

CHARACTER_SLUG = "adam"
# Path relative to THIS file's location
HERE = os.path.dirname(os.path.abspath(__file__))      # .../daemons/characters/
DAEMONS_ROOT = os.path.dirname(HERE)                    # .../daemons/

# Your actual structure: daemons/schedules/adam_schedule.json
SCHEDULE_PATH = os.path.join(DAEMONS_ROOT, "schedules", f"{CHARACTER_SLUG}_schedule.json")
STATE_PATH = os.path.join(DAEMONS_ROOT, "states", f"{CHARACTER_SLUG}_state.json")

def bootstrap_state(schedule):
    """First breath."""
    baseline, next_evt, event_name = circadian.get_circadian_baseline(schedule)

    return {
        "last_updated": datetime.datetime.now().isoformat(),
        "last_wake": datetime.datetime.now().isoformat(),
        "emotional_state": baseline,
        "relational_web": schedule.get("relational_web", {}),
        "last_interaction": {
            "with": get_last_interaction("nathan"),
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

QUEUE_FILE = "message_queue.json"  # same folder as adam_state.json

def read_my_messages():
    """returns list of dicts addressed to 'adam' and deletes them from queue"""
    if not pathlib.Path(QUEUE_FILE).exists():
        return []
    
    with open(QUEUE_FILE, "r+") as f:
        lines = f.readlines()

    kept, mine = [], []
    for raw in lines:
        try:
            msg = json.loads(raw)
            if msg.get("to") == "adam":
                mine.append(msg)
            else:
                kept.append(raw)
        except json.JSONDecodeError:
            pass

    # rewrite file WITHOUT the ones we took
    pathlib.Path(QUEUE_FILE).write_text("".join(kept))
    return mine

def wake():
    print(f"[{datetime.datetime.now()}] {CHARACTER_SLUG} waking...")

    schedule = load_schedule()
    state = state_manager.load(STATE_PATH, lambda: bootstrap_state(schedule))
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
        "studio_flow": "studio_flow",
        "uni_lecture": "work_focus",
        "busk_loop": "busk_loop",
        "dad_coffee": "dad_coffee",
        "night_owl": "night_owl",
        "footnote_seek": "footnote_seek",
        "mum_call": "mum_call",  # if you add this to registry
    }

    registry_event = event_map.get(event_name, event_name)

    # Check shared message queue for Adam
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
        if msg["from"] == "nathan" and "coffee" in payload.get("content", ""):
            state["emotional_state"]["valence"] = min(1.0, state["emotional_state"].get("valence", 0) + 0.3)
            state["emotional_state"]["loneliness"] = max(0.0, state["emotional_state"].get("loneliness", 0) - 0.4)
            # Maybe trigger response
            state["trigger_response_to_nathan"] = True
            reply_text = (
                "Sounds great, dad. How bout half an hour?"
            )
            answer = {
                "from": "adam",
                "to": "nathan",
                "event": "adam.reply_coffee",
                "payload": {
                    "content": reply_text,
                    "medium": "text",
                    "timestamp": datetime.datetime.now().isoformat(0)
                }
            }
            # append (new-line-delimited) so Nathan can read it next cycle
            with open(queue_path, "a") as fq:
                fq.write("\n" + json.dumps(answer))
            state["trigger_response_to_nathan"] = False  # job done

    # Decay loneliness
    last_int = datetime.datetime.fromisoformat(state["last_interaction"]["timestamp"])
    hours = (now - last_int).total_seconds() / 3600

    print(f"  Pre-decay loneliness: {state['emotional_state']['loneliness']}")
    new_lonely, modifier, delta = loneliness.decay(state, hours, CHARACTER_SLUG, registry_event)
    state["emotional_state"]["loneliness"] = new_lonely
    print(f"  Post-decay ({modifier}, Δ{delta:+.3f}): {new_lonely}")
    
    # Decision: act or wait?
    budget = state["relational_web"].get("uncertainty_budget", 0.6)
    threshold = 1.0 - budget
    lonely = state["emotional_state"]["loneliness"] 
    
    if lonely > threshold:
        roll = random.random()
        if roll < 0.7:
            state = simulate(state)
            print(f"  SIM: {state['last_simulation']['summary']}")
        else:
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

def simulate(state):
    """Internal thought, no external call."""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"].get("preferred_reconnection_ritual", "contact")
    event = state.get("current_event", "presence")

    state["emotional_state"]["valence"] = round(0.3 - (lonely * 0.4), 3)
    state["emotional_state"]["arousal"] = round(0.2 + (lonely * 0.5), 3)

    thoughts = {
        "wake": f"Today. Morning. Wonder what will happen next.",
        "am_break": f"Feels good to get off my feet.",
        "performance": f"Others near, but wanting {ritual} with Dad"
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

    system, user = api_client.build_adam_prompt(state, event)
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
            "with": "Nathan",
            "timestamp": meta["timestamp"],
            "medium": "daemon_triggered_call"
        }
        return True
    else:
        print(f"  API FAIL: {meta.get('error', 'unknown')}")
        return False

if __name__ == "__main__":
    wake()