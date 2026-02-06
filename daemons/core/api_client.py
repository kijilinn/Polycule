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
        f"Desired ritual: {ritual}. Reach out to Linn. One sentence, in character."
    )

    return system, user