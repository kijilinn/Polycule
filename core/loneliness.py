import datetime

def decay(state, hours, event_name, mesh_data=None):
    # --- SANITY CHECK ---
    if mesh_data is None:
        mesh_data = {"nodes": {}, "edges": []} 

    # 1. Get Event
    event = event_name or state.get("current_event", "idle")

    # 2. Get Event Modifiers FROM SCHEDULE (Not Registry)
    # Note: 'state' needs access to the schedule, or we pass it in.
    # For now, we assume 'state' or 'event_context' handles this.
    # But let's add a fallback for 'type' of event.

    # 3. Default Rate
    rate = 0.05 # Standard decay per hour

    # 4. Modifiers (Heuristics)
    if "work" in event.lower() or "focus" in event.lower():
        rate = 0.03 # Slow decay when busy
        modifier = "reduced"
    elif "presence" in event.lower() or "home" in event.lower():
        rate = -0.02 # Repair when safe
        modifier = "repair"
    else:
        modifier = "standard"

    # 5. CALCULATE
    # FIX: Used variable 'hours' instead of non-existent 'hours_elapsed'
    delta = hours * rate

    # FIX: Removed extra closing parenthesis
    new_lonely = max(0.0, min(1.0, state["emotional_state"]["loneliness"] + delta))

    return round(new_lonely, 3), modifier, delta