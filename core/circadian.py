import datetime
import json

def is_new_day(last_wake_dt, now, schedule):
    """Check if we've crossed into a new circadian day."""
    anchor_time_str = schedule.get("circadian_anchor", "09:00")
    anchor_hour, anchor_min = map(int, anchor_time_str.split(":"))
    today_anchor = now.replace(hour=anchor_hour, minute=anchor_min, 
                               second=0, microsecond=0)

    if now < today_anchor:
        return False
    if last_wake_dt.date() < now.date():
        return True
    if last_wake_dt < today_anchor:
        return True
    return False

def get_circadian_baseline(schedule):
    """Find current event—handles daily or weekly rhythms."""
    now = datetime.datetime.now()

    # Try daily circadian profile first
    events = schedule.get("circadian_profile", {}).get("anchor_events", [])

    # Fallback to weekly rhythm
    if not events:
        weekly = schedule.get("weekly_rhythm", {}).get("anchor_events", [])
        # Filter to today
        today = now.strftime("%A")  # "Monday", "Tuesday", etc.
        events = [e for e in weekly if e.get("day") == today or e.get("day") == "any"]

    parsed = []
    for e in events:
        t = datetime.datetime.strptime(e["time"], "%H:%M").time()
        parsed.append((t, e))
    parsed.sort()

    current = None
    next_evt = None
    for i, (t, e) in enumerate(parsed):
        if t <= now.time():
            current = e
            next_evt = parsed[(i+1) % len(parsed)][1] if parsed else None

    if not current:
        current = parsed[-1][1] if parsed else None
        if current is None:
    # No event today—use relational_web defaults or hard baseline
            web = schedule.get("relational_web", {})
            current = {
                "event": "unscheduled",
                "default_valence": 0.0,
                "default_arousal": 0.3,
                "default_dominance": 0.5,
                "loneliness_reset": 0.5,
                "state_modifier": {}
        }

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

def apply_fresh_start(state, schedule, now):
    """Morning reset: preserve identity, refresh body."""
    baseline, next_evt, event_name = get_circadian_baseline(schedule)

    state["emotional_state"] = baseline
    state["current_event"] = event_name
    state["next_event"] = next_evt.get("time") if next_evt else None
    state["last_wake"] = now.isoformat()
    state["fresh_start"] = True

    return state