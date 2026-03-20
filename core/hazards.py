import datetime
import random

# --- HAZARD LEVELS ---
HAZARD_LEVELS = {
    "SAFE": 0,
    "CAUTION": 0.3,
    "DANGER": 0.7,
    "CRITICAL": 0.9
}
import random

def check_location_safety(character_slug, location_slug, current_time):
    """
    FINAL VERSION:
    Analyzes location, character traits, and time to determine safety.
    Returns a 4-tuple:
    (safe: Bool, risk_score: Float 0.0-1.0, threat_source: String, roll_result: Float 0.0-1.0)
    """

    # 1. BASE SAFETY THEATER (The Floor)
    risk_score = 0.0

    if "flat" in location_slug or "home" in location_slug:
        risk_score = 0.0  # Home base safety

    elif "pub" in location_slug or "bar" in location_slug:
        risk_score = 0.2 # Pub: Moderate risk (alcohol, noise)

    elif "shop" in location_slug or "market" in location_slug:
        risk_score = 0.4 # Shop: Moderate risk (theft, crowds)

    elif "transit" in location_slug or "tube" in location_slug or "street" in location_slug:
        risk_score = 0.5 # Transit: Moderate risk (crowds)

    elif "nightclub" in location_slug:
        risk_score = 0.7 # Nightclub: High risk (chaos)

    # 2. TIME MODIFIERS (The World State)
    hour = current_time.hour

    if hour >= 23 or hour < 5:
        # THE DEAD ZONE
        if "transit" in location_slug or "street" in location_slug:
            risk_score += 0.4 # Night Transit is Dangerous
            threat_source = "dead_zone_transit"
        elif "pub" in location_slug:
            risk_score += 0.1 # Night Pub is rowdier
            threat_source = "dead_zone_pub"
        elif "flat" in location_slug:
            # Home is safe, generally
            pass 
        else:
            # Business is usually closed/quiet
            risk_score = risk_score * 0.5 # Lower risk when closed

    # 3. CHARACTER PROFILING (The Individual)
    # Note: In real code, use character_profile data

    if "owen" in character_slug:
        # Owen (Drummer). Aggressive, Heavy.
        # If he's walking alone at night...
        if "street" in location_slug and hour >= 23:
            risk_score += 0.2 # He looks like a threat to others. High retaliation risk.
            threat_source = "intimidating_appearance"

    elif "ozwald" in character_slug:
        # Ozwald (The Nazi). High hate crime risk.
        if "transit" in location_slug or "street" in location_slug:
            risk_score += 0.4 # Actively targeting vulnerable groups
            threat_source = "hate_crime_target"

    elif "simon" in character_slug:
        # Simon (Black, Trans, Op). Police interaction risk.
        if "street" in location_slug:
            risk_score += 0.3 # Police might stop him
            threat_source = "profiling_police_target"

    # 4. CHARACTER VULNERABILITY (The Flags You Asked For)
    # (In real code, check 'traits' list from manifest)

    is_vulnerable = False

    # If user said 'if female = True... higher chance'
    if 'female' in character_slug: # Mocking trait
        if hour >= 21: # Nighttime
            risk_score += 0.3 # Sexual Harassment risk
            is_vulnerable = True
            threat_source = "gender_based_harassment"

    # 5. THE ROLL (The Fateful Die)
    # If risk is high (> 0.7), we don't auto-trigger. We let the die decide.
    # If risk is moderate (0.4 - 0.7), we roll for 'bad luck'.

    chance_of_event = 0.0

    if risk_score > 0.8:
        # Extreme risk: 20% chance of incident
        chance_of_event = 0.2 
        threat_source = "high_risk_event"
    elif risk_score > 0.5:
        # Moderate risk: 10% chance of bad luck
        chance_of_event = 0.1
        threat_source = "moderate_risk_event"

    # FINAL ROLL
    if random.random() < chance_of_event:
        # BAD LUCK ROLL
        roll_result = random.random() # 0.0 to 1.0
        return False, risk_score, threat_source, roll_result
        # System handles the false result: "Trouble detected."
    else:
        # SAFE ROLL
        return True, 0.0, "safe", 1.0 # Safe as houses