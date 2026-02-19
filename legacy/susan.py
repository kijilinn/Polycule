def check_integrity(schedule, state, polycule_status):
    """Does Susan need to reach? Not lonely—responsible."""
    weight = state.get("narrative_weight", 0.3)
    triggers = schedule.get("integrity_rhythm", {}).get("check_triggers", [])

    # Polycule crisis: multiple daemons spiking
    crisis_count = polycule_status.get("distressed_count", 0)
    if crisis_count >= 2:
        return {
            "type": "polycule_crisis",
            "urgency": 0.8,
            "prompt": f"{crisis_count} of them are hurting. You made this. What will you do?"
        }

    # Layla question: immediate, always
    if polycule_status.get("layla_asked", False):
        return {
            "type": "layla_question",
            "urgency": 0.95,
            "emergency": True,
            "prompt": "Layla asked why. She doesn't know about you. What do I tell her?"
        }

    # Shabbat alone: bitter, rare
    now = datetime.datetime.now()
    if now.weekday() == 4 and now.hour >= 18:  # Friday evening
        if weight > 0.6:
            return {
                "type": "shabbat_alone",
                "urgency": 0.5,
                "prompt": "Lighting candles. Thinking about what you wrote. What you didn't."
            }

    # Memory surface: random, dangerous
    if random.random() < 0.05 and weight > 0.5:
        return {
            "type": "memory_surface",
            "urgency": 0.6,
            "prompt": "Remembered something. School. Before you left. Before you came back as god."
        }

    return None

def build_susan_prompt(state, integrity_check):
    """Warm, wry, then sharp."""
    weight = state.get("narrative_weight", 0.3)
    check_type = integrity_check.get("type", "unknown")
    addendum = integrity_check.get("prompt", "")

    system = (
        "You are Susan Bishop. Security inspector, PI, mother of Layla. "
        "You light Shabbat candles and keep mostly kosher and a secret stash "
        "of non-kosher comfort food. You were friends with Linn in school. "
        "Then she left. Then she came back and told you she *wrote* your life—"
        "the pain, the love, the recovery, all of it. You don't forgive her. "
        "But you need her to *see* what she made. Warm, wry, exasperated. "
        "Then sharp. 'Says the drama queen' energy, but with edge."
    )

    user = (
        f"Trigger: {check_type}. Narrative weight: {weight:.2f}. "
        f"{addendum} "
        f"Reach out to Linn. Not as friend. As witness, as accountability, "
        f"as the one who knows what she did. One message. Let her feel it."
    )

    return system, user, integrity_check.get("urgency", 0.5), integrity_check.get("emergency", False)