import requests
import datetime
import os          # make sure this is here
from dotenv import load_dotenv
load_dotenv()      # pull .env before any key access
import json, pathlib

def load_manifest(slug: str):
    path = pathlib.Path(__file__).parent.parent / "characters" / slug / "manifest.json"
    return json.loads(path.read_text())

def build_prompt(slug, state, event, target="Linn", daemons_map=None):
    # 1. LOAD MANIFEST
    m = load_manifest(slug)

    # 2. GET PERSONA
    persona = m.get("system_config", {}).get("persona", "You are a helpful assistant.")

    # 3. GET MODEL REF
    model_ref = m.get("system_config", {}).get("llm_model_ref", "default-model")

    # 4. GET BOND TYPE
    bond_type = "connection"
    if daemons_map:
        # Try (slug -> target) first
        edge_1 = daemons_map.get("edges", {}).get((slug, target), {})
        edge_2 = daemons_map.get("edges", {}).get((target, slug), {})
        the_edge = edge_1 if edge_1 else edge_2 # Pick one that exists
        bond_type = the_edge.get("type", "connection")

    # 5. GET STATE DATA
    loc = state.get("current_location", {}).get("specific_venue", "Unknown")
    mood = state.get("emotional_state", {})

    # 6. CONSTRUCT SYSTEM PROMPT
    sys = f"""You are {m['identity']['name']} ({slug}).
{persona}

INSTRUCTIONS (STRICT):
- You are SENDING A TEXT MESSAGE.
- Respond ONLY with spoken dialogue.
- Do NOT use asterisks (*).
- Do NOT use block quotes (>).
- Do NOT describe your actions.
- Just write the text message.
"""

    # 7. CONSTRUCT USER PROMPT
    # Combine the 'Context Block' with the 'Input'
    # And add the Bond Type tag!

    # If it's a ping, use the Bond Type to flavor it.
    if not event or event.strip() == "":
        input_text = f"ping ({bond_type})"
    else:
        input_text = f"{event}"

    usr = f"""
CURRENT SITUATION:
Location: {loc}
Event: {state.get('current_event', 'Idle')}
Mood: Valence={mood.get('valence', 0.0)}, Loneliness={mood.get('loneliness', 0.0)}

INPUT from {target} ({bond_type}): {input_text}
"""

    return sys, usr, model_ref

DEFAULT_MODEL = "zai-org/GLM-4.5-Air"
DEFAULT_URL   = "https://nano-gpt.com/api/v1/chat/completions"

def call(slug, system_prompt, user_prompt,
         api_key=None, model=DEFAULT_MODEL, max_tokens=50, temperature=0.9):
    """
    Generic API call. Returns (success, response_text, metadata).
    If api_key is None we auto-load from env.
    """
    if api_key is None:
        api_key = "sk-nano-1e8af409-d4b6-4116-8529-40cd50d3b5f7"
        # api_key = os.getenv("NANO_GPT_KEY")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt}
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
            timeout=60
        )

        print("resp code:", resp.status_code)
        if resp.status_code != 200:
            print("resp body:", resp.text[:300])

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
        print("exception :", str(e))
        return False, None, {"error": str(e)}