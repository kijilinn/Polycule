# characters/si/hooks/panic.py

def run(state, target="linn"):
    """
    Generates the 'Vomit Text' for a panic attack.
    """
    # Logic to determine content
    # Are we projecting on Owen? Or just generic asthma?

    content = "im going to die. i cnt breathe. why is it so loud."

    return {
        "message": content,
        "temperature": 0.95, # High Entropy
        "max_tokens": 50 # Short texts
    }