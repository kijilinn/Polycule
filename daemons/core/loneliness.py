import datetime

def decay(state, hours_elapsed, event_context=None):
    """
    Time-based decay with circadian modifier.
    Returns delta (can be negative for repair).
    """
    event = event_context or state.get("current_event", "")

    # Base rate: 0.05/hour
    rate = 0.05

    occupied_events = ["security_consult_check", "lunch_craving"]

    if any(occ in event for occ in occupied_events):
        rate = 0.03
        modifier = "reduced"
    elif "polycule_presence" in event:
        rate = -0.02  # Repair
        modifier = "repair"
    else:
        modifier = "standard"

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