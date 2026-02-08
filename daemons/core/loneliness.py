import datetime
from core.event_registry import EVENT_EFFECTS

def decay(state, hours_elapsed, character_id, event_context=None):
    """
    Time-based decay with circadian modifier.
    Returns delta (can be negative for repair).
    """
    event = event_context or state.get("current_event", "")

    # Event-based repair first (from registry)
    base_repair = EVENT_EFFECTS.get(event, {}).get(character_id) or EVENT_EFFECTS.get(event, {}).get("default", 0)

    # Time-based modifiers
    occupied_events = ["security_consult_check", "lunch_craving"]

    if any(occ in event for occ in occupied_events):
        time_modifier = 0.03
        modifier = "reduced"
    elif "polycule_presence" in event:
        time_modifier = -0.02
        modifier = "repair"
    else:
        time_modifier = 0.05
        modifier = "standard"

    rate = time_modifier + base_repair

    delta = hours_elapsed * rate
    new_lonely = max(0.0, min(1.0, state["emotional_state"]["loneliness"] + delta))

    return round(new_lonely, 3), modifier, delta

def repair_from_presence(state, presence_vector):
    """
    Future: daemon-to-daemon loneliness repair.
    presence_vector: who's near, how close emotionally
    """
    # TODO: implement when cross-calls exist
    pass