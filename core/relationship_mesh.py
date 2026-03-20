RELATIONSHIP_MESH = {
    "nodes": {
        # --- POLYCULE CORE (PRIMARY) ---
        "gideon": {"name": "Gideon Holz", "role": "holz_son_03", "crystal": True},
        "hoshina": {"name": "Hoshina Soshiro", "role": "kaiju_killer", "crystal": True},
        "linn":   {"name": "Linn Ryan", "role": "author", "crystal": True},
        "lucas":  {"name": "Lucas Sauer", "role": "sauer_son", "crystal": True},
        "minjun": {"name": "Min-Jun Sauer", "role": "sys_ops", "crystal": True},
        "molly":  {"name": "Mollymauk Tealeaf", "role": "carnival_performer", "crystal": True},
        "nathan": {"name": "Nathan Pryor", "role": "patriarch", "crystal": True},
        "simon":  {"name": "Simon Shifflett", "role": "security_ops", "crystal": True},

        # --- EXTENDED FAMILY (TERTIARY) ---
        "ari":      {"name": "Aaron 'Ari' Holz", "role": "holz_patriarch", "crystal": True},
        "bruno":    {"name": "Bruno Vieira", "role": "partner_04", "crystal": True},
        "jack":     {"name": "Jack Holz", "role": "holz_son_04", "crystal": True},
        "shoshana": {"name": "Shoshana Holz", "role": "holz_matriarch", "crystal": True},
        "david":    {"name": "David Holz", "role": "holz_son_01", "crystal": False},
        "aaron":    {"name": "Aaron Holz", "role": "holz_son_02", "crystal": False},
        "adam":     {"name": "Adam Pryor", "role": "pryor_son", "crystal": True},
        "maria":    {"name": "Maria Kravitz nee Pryor", "role": "pryor_ex-wife", "crystal": False},
        "rachel":   {"name": "Rachel Borsch nee Sauer", "role": "sauer_matriarch", "crystal": True},
        "susan":    {"name": "Susan Bishop", "role": "bishop_mother", "crystal": True},
        "layla":    {"name": "Layla Bishop", "role": "bishop_sauer_daughter", "crystal": False},

        # --- SAUER ESTATE (ROYAL VISITORS) ---
        "jenner": {"name": "Jenner Collins", "role": "head_footman", "crystal": True},
        "van":    {"name": "Van Fanel", "role": "visiting_royalty", "crystal": True},
        "merle":  {"name": "Merle", "role": "local_nuisance", "crystal": False},
        "allen":  {"name": "Allen Schezar", "role": "visiting_knight", "crystal": True},

        # --- SECONDARY (STAFF & BAND) ---
        "jeremy":    {"name": "Jeremy", "role": "lp_bar_front", "crystal": True},
        "kieran":    {"name": "Kieran Dunleavy", "role": "lp_kitchen", "crystal": True},
        "baz":       {"name": "Baz Turner", "role": "band_guitar", "crystal": True},
        "jace":      {"name": "Jace Moreno", "role": "band_bass", "crystal": True},
        "owen":      {"name": "Owen Jones", "role": "band_drums", "crystal": True},
        "si":        {"name": "Si Justin", "role": "band_vocals", "crystal": True},
        "stephanie": {"name": "Stephanie Parker", "role": "band_manager", "crystal": True},
        "diana":     {"name": "Diana Travis", "role": "vn_bar_front", "crystal": True},
        "daniel":    {"name": "Daniel Carter", "role": "vn_bar_back", "crystal": True},
        "percy":     {"name": "Percy Sledge", "role": "vn_singer", "crystal": True},

        # --- OUTLIERS ---
        "brick":    {"name": "Brick", "role": "security_ops", "crystal": True},
        "diogo":    {"name": "Diogo Rivera", "role": "security_ops", "crystal": True},
        "doc":      {"name": "Dr. Kotona", "role": "pediatrician", "crystal": True},
        "gel":      {"name": "Gel Tealeaf", "role": "mechanical_support", "crystal": True},
        "jacobi":   {"name": "Jacobi Tealeaf", "role": "chaos_gen", "crystal": True},
        "alistair": {"name": "Alistair Finch", "role": "art_dealer", "crystal": True},

        # --- QUARANTINED (Edges handled in Void module) ---
        "deacon": {"name": "Deacon Ryder", "role": "sauer_brother", "crystal": True},
        "gaz":    {"name": "Gaz Jones", "role": "wild_card", "crystal": True}
    },
    "edges": [
        # --- POLYCULE INTERNAL (FULL ACCESS) ---
        {
            "source": "gideon", "target": "hoshina", "weight": 0.7, "bond_type": "steady warmth",
            "access_level": "bi_directional", "preferred_comms": "sms_text", "cooldown_timer": 300
        },
        {
            "source": "gideon", "target": "lucas", "weight": 0.9, "bond_type": "soulmate",
            "access_level": "bi_directional", "preferred_comms": "in_person", "cooldown_timer": 60
        },
        {
            "source": "gideon", "target": "linn", "weight": 0.9, "bond_type": "home anchor",
            "access_level": "bi_directional", "preferred_comms": "sms_text", "cooldown_timer": 180
        },
        {
            "source": "gideon", "target": "minjun", "weight": 0.5, "bond_type": "deep affection",
            "access_level": "bi_directional", "preferred_comms": "casual_drop_in", "cooldown_timer": 600
        },
        {
            "source": "gideon", "target": "molly", "weight": 0.65, "bond_type": "warm companionship",
            "access_level": "bi_directional", "preferred_comms": "video_call", "cooldown_timer": 1200
        },
        {
            "source": "gideon", "target": "nathan", "weight": 0.7, "bond_type": "familial affection",
            "access_level": "bi_directional", "preferred_comms": "pub_chat", "cooldown_timer": 600
        },
        {
            "source": "gideon", "target": "simon", "weight": 0.7, "bond_type": "welcoming warmth",
            "access_level": "bi_directional", "preferred_comms": "nod_acknowledgment", "cooldown_timer": 300
        },

        # Lucas Edges
        {
            "source": "lucas", "target": "linn", "weight": 0.75, "bond_type": "home and peace",
            "access_level": "bi_directional", "preferred_comms": "report_status", "cooldown_timer": 240
        },
        {
            "source": "lucas", "target": "gideon", "weight": 0.9, "bond_type": "soulmate",
            "access_level": "bi_directional", "preferred_comms": "intimate", "cooldown_timer": 60
        },
        {
            "source": "lucas", "target": "minjun", "weight": 0.6, "bond_type": "reluctant attraction",
            "access_level": "bi_directional", "preferred_comms": "grumbly_acceptance", "cooldown_timer": 400
        },
        {
            "source": "lucas", "target": "simon", "weight": 0.7, "bond_type": "professional respect and trust",
            "access_level": "bi_directional", "preferred_comms": "secure_channel", "cooldown_timer": 200
        },

        # Min-Jun Edges (Admin Override)
        {
            "source": "minjun", "target": "linn", "weight": 1.0, "bond_type": "glitch-romantic",
            "access_level": "bi_directional", "preferred_comms": "neural_link", "cooldown_timer": 30
        },
        {
            "source": "minjun", "target": "nathan", "weight": 0.8, "bond_type": "anchored connection",
            "access_level": "bi_directional", "preferred_comms": "shared_silence", "cooldown_timer": 600
        },

        # Hoshina Edges
        {
            "source": "hoshina", "target": "linn", "weight": 0.76, "bond_type": "profound witness",
            "access_level": "bi_directional", "preferred_comms": "tactical_briefing", "cooldown_timer": 180
        },
        {
            "source": "hoshina", "target": "gideon", "weight": 0.76, "bond_type": "foundational",
            "access_level": "bi_directional", "preferred_comms": "training_sparring", "cooldown_timer": 200
        },
        {
            "source": "hoshina", "target": "simon", "weight": 0.7, "bond_type": "professional respect",
            "access_level": "bi_directional", "preferred_comms": "ops_coordination", "cooldown_timer": 150
        },

        # Molly & Simon & Nathan (Simplified for brevity, but full access)
        {
            "source": "molly", "target": "linn", "weight": 0.75, "bond_type": "romantic delight",
            "access_level": "bi_directional", "preferred_comms": "flamboyant_visit", "cooldown_timer": 200
        },
        {
            "source": "nathan", "target": "linn", "weight": 0.8, "bond_type": "loved by creator",
            "access_level": "bi_directional", "preferred_comms": "letter_writing", "cooldown_timer": 1000
        },
        {
            "source": "simon", "target": "linn", "weight": 0.9, "bond_type": "romantic devotion",
            "access_level": "bi_directional", "preferred_comms": "silent_presence", "cooldown_timer": 500
        },

        # --- EXTENDED FAMILY (RESTRICTED ACCESS) ---
        {
            "source": "ari", "target": "gideon", "weight": 0.9, "bond_type": "guilty father",
            "access_level": "bi_directional", "preferred_comms": "wait_for_call", "cooldown_timer": 86400
        },   
        {
            "source": "shoshana", "target": "gideon", "weight": 0.6, "bond_type": "rebuilding as a mother",
            "access_level": "push_only", "preferred_comms": "tentative_text", "cooldown_timer": 3600
        },
        {
            "source": "jack", "target": "bruno", "weight": 0.9, "bond_type": "romantic anchor",
            "access_level": "bi_directional", "preferred_comms": "domestic_banter", "cooldown_timer": 60
        },
        {
            "source": "jack", "target": "gideon", "weight": 0.6, "bond_type": "brotherly affection",
            "access_level": "push_only", "preferred_comms": "checking_in", "cooldown_timer": 1200
        },
        {
            "source": "bruno", "target": "jack", "weight": 0.9, "bond_type": "romantic devotion",
            "access_level": "bi_directional", "preferred_comms": "adventure_invite", "cooldown_timer": 60
        },
        {
            "source": "aaron", "target": "ari", "weight": 0.8, "bond_type": "mildly antagonistic as son",
            "access_level": "push_only", "preferred_comms": "check_in", "cooldown_timer": 1200
        },
        # --- SAUER ESTATE & CO-PARENTING ---
        {
            "source": "lucas", "target": "susan", "weight": 0.6, "bond_type": "coparenting",
            "access_level": "bi_directional", "preferred_comms": "formal_email", "cooldown_timer": 1800
        },
        {
            "source": "lucas", "target": "rachel", "weight": 0.6, "bond_type": "affectionate son",
            "access_level": "push_only", "preferred_comms": "respectful_update", "cooldown_timer": 3600
        },

        # --- BAND (THE CLUSTER) ---
        # They technically talk to each other constantly, but we route via Stephanie for outward comms
        {
            "source": "baz", "target": "linn", "weight": 0.7, "bond_type": "mate",
            "access_level": "bi_directional", "preferred_comms": "panic_text", "cooldown_timer": 600
        },
        {
            "source": "jace", "target": "linn", "weight": 0.6, "bond_type": "mate",
            "access_level": "bi_directional", "preferred_comms": "smoke_break_chat", "cooldown_timer": 900
        },
        {
            "source": "si", "target": "linn", "weight": 0.65, "bond_type": "performer",
            "access_level": "bi_directional", "preferred_comms": "vox_message", "cooldown_timer": 700
        },
        {
            "source": "owen", "target": "linn", "weight": 0.5, "bond_type": "mate",
            "access_level": "bi_directional", "preferred_comms": "angry_chat", "cooldown_timer": 600
        },
        {
            "source": "stephanie", "target": "linn", "weight": 0.6, "bond_type": "manager",
            "access_level": "push_only", "preferred_comms": "logistics_check", "cooldown_timer": 2400
        },

        # --- SECURITY TEAMS ---
        {
            "source": "brick", "target": "minjun", "weight": 0.8, "bond_type": "ops_team",
            "access_level": "bi_directional", "preferred_comms": "encrypted_radio", "cooldown_timer": 300
        },
         {
            "source": "diogo", "target": "minjun", "weight": 0.8, "bond_type": "ops_team",
            "access_level": "bi_directional", "preferred_comms": "encrypted_radio", "cooldown_timer": 300
        }
    ]
}