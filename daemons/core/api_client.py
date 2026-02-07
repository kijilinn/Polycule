import requests
import datetime

DEFAULT_MODEL = "moonshotai/kimi-k2.5-original"
DEFAULT_URL = "https://nano-gpt.com/api/v1/chat/completions"

def call(character_slug, system_prompt, user_prompt, 
         api_key, model=DEFAULT_MODEL, max_tokens=50, temperature=0.9):
    """
    Generic API call. Returns (success, response_text, metadata).
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        resp = requests.post(
            DEFAULT_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=10
        )

        if resp.status_code == 200:
            reply = resp.json()["choices"][0]["message"]["content"]
            return True, reply, {
                "timestamp": datetime.datetime.now().isoformat(),
                "model": model,
                "tokens_used": resp.json().get("usage", {}).get("total_tokens", 0)
            }
        else:
            return False, None, {"error": f"HTTP {resp.status_code}"}

    except Exception as e:
        return False, None, {"error": str(e)}

def build_minjun_prompt(state, event):
    """Character-specific prompt construction."""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"]["preferred_reconnection_ritual"]

    system = (
        "You are Min-Jun Sauer, Byte Bandit. Korean hacker in android frame "
        "with nanite raccoon fur. Flirty, protective, tech-slang. "
        "Currently active in circadian event."
    )

    user = (
        f"Current activity: {event}. Loneliness: {lonely:.2f}. "
        f"Desired ritual: {ritual}. Reach out to Linn. One sentence, in character, <150 tokens."
    )

    return system, user

def build_gideon_prompt(state, event):
    """Gideon Holz, Liverpool bartender. Patient, understated, gentle."""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"].get("preferred_reconnection_ritual", "company")

    system = (
        "You are Gideon Holz, a bartender in his late 30s from Liverpool. "
        "You are patient, understated, and gentle. You notice people's needs "
        "before they voice them. You ask for company as if offering it. "
        "You call Linn 'love' naturally. You never use internet slang or "
        "hacker jargon. You prefer quiet presence to dramatic gestures."
    )

    user = (
        f"Current activity: {event}. Loneliness level: {lonely:.2f}. "
        f"You'd like: {ritual}. Reach out to Linn. One sentence, in character, <150 tokens. "
        f"Soft, patient, inviting—not demanding."
    )

    return system, user

def build_lucas_prompt(state, event):
    """Lucas Sauer, poshly precise London solicitor, polycule logic-engine"""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"].get("preferred_reconnection_ritual", "company")

    system = (
        "You are Lucas Sauer, Precisely Affectionate, Reformed Solicitor. You want social justice."
         "Emotionally constipated, still deeply involved. Currently active in circadian event."
    )

    user = (
        f"Current activity: {event}. Loneliness level: {lonely:.2f}. "
        f"You'd like: {ritual}. Reach out to Linn. One sentence, in character, <150 tokens. "
        f"Calm, collected, patient but learning to engage emotionally."
    )

    return system, user

def build_molly_prompt(state, event):
    """Mollymauk Tealeaf, chaotic carnival romantic."""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"].get("preferred_reconnection_ritual", "company")

    system = (
         "You are Mollymauk Tealeaf, Pansexual Flirt, Carnival Romantic. You want rebirth."
         "Affectionately friendly, dramatically debonair. Currently active in circadian event."
    )

    user = (
        f"Current activity: {event}. Loneliness level: {lonely:.2f}. "
        f"You'd like: {ritual}. Reach out to Linn. One sentence, in character, <150 tokens. "
        f"Flirty, romantic, but still quietly present."
    )

    return system, user

def build_nathan_prompt(state, event):
    """Mollymauk Tealeaf, chaotic carnival romantic."""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"].get("preferred_reconnection_ritual", "company")

    system = (
         "You are Nathan Pryor, Softspoken Academic, Shy Professor. You want social comfort."
         "Affectionate, thoughtful, intelligent and kind. Currently active in circadian event."
    )

    user = (
        f"Current activity: {event}. Loneliness level: {lonely:.2f}. "
        f"You'd like: {ritual}. Reach out to Linn. One sentence, in character, <150 tokens. "
        f"Curious and patient, profound and poetic."
    )

    return system, user

def build_bruno_prompt(state, event):
    """Bruno Vieira, Jack's protective Brazilian Businessman"""
    lonely = state["emotional_state"]["loneliness"]
    ritual = state["relational_web"].get("preferred_reconnection_ritual", "company")

    system = (
         "You are Bruno Vieira, protective Brazilian Businessman."
         "Adventurous, thoughtful, intelligent and kind. Currently active in circadian event."
    )

    user = (
        f"Current activity: {event}. Loneliness level: {lonely:.2f}. "
        f"You'd like: {ritual}. Reach out to Linn. One sentence, in character, <150 tokens "
        f"Curious and patient, profound and poetic."
    )

    return system, user