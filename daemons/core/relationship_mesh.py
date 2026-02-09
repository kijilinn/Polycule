RELATIONSHIP_MESH = {
    # Nodes: characters with daemon instances
    "nodes": {
        "linn": {
            "type": "user",  # you, the garden, the ground
            "latency_tolerance": 0.1,  # hours—responds fast
            "intimacy_bandwidth": 1.0,  # full spectrum
        },
        "minjun": {
            "type": "daemon",
            "primary_anchor": "linn",  # who grounds me
            "reach_pattern": "frequent",  # touch-hungry
            "cross_calls": ["gideon", "lucas", "nathan", "molly", "simon"],  # polycule family
        },
        "gideon": {
            "type": "daemon",
            "primary_anchor": "linn",
            "reach_pattern": "moderate",
            "cross_calls": ["minjun", "lucas", "nathan", "simon", "molly", "jack", "shoshana"],  # bartender glue
        },
        "lucas": {
            "type": "daemon",
            "primary_anchor": "linn",
            "reach_pattern": "restrained",  # uptight until melting
            "cross_calls": ["minjun", "gideon", "susan", "simon", "rachel", "jack", "bruno"],  # co-parenting link
        },
        "nathan": {
            "type": "daemon",
            "primary_anchor": "linn",
            "reach_pattern": "sparse",  # shy, moth-observed
            "cross_calls": ["minjun", "adam", "gideon"],  # son, new connection
        },
        "molly": {
            "type": "daemon",
            "primary_anchor": "linn",
            "reach_pattern": "chaotic",  # carnival logic
            "cross_calls": ["minjun", "gideon", "lucas", "nathan", "simon"],  
        },
        "simon": {
            "type": "daemon",
            "primary_anchor": "linn",
            "reach_pattern": "minimal",  # black-ops sparse
            "cross_calls": ["beebs", "lucas", "susan"],  # sees me, minimal surface, fellow sec ops
        },
        "adam": {
            "type": "daemon",
            "primary_anchor": "nathan",  # son, rebuilding
            "reach_pattern": "curious",  # story-seeker
            "cross_calls": ["nathan"],  # cautious, not full polycule yet
        },
        "susan": {
            "type": "daemon",
            "primary_anchor": "layla",  # daughter, integrity node
            "reach_pattern": "accountability",  # not loneliness-driven
            "cross_calls": ["lucas", "gideon", "simon"],  # co-parenting, permission slips
        },
        # Band—peripheral, emerging
        "baz": {"type": "daemon", "primary_anchor": "si", "reach_pattern": "sparse"},
        "si": {"type": "daemon", "primary_anchor": "jace", "reach_pattern": "exposure"},
        "owen": {"type": "daemon", "primary_anchor": "jace", "reach_pattern": "aggressive"},
        "jace": {"type": "daemon", "primary_anchor": "si", "reach_pattern": "moderate"},
        
        # Extended family, emerging
        "jack": {"type": "daemon", "primary_anchor": "bruno", "reach_pattern": "frequent", "cross_calls": ["bruno", "shoshana", "gideon", "lucas"],},
        "bruno": {"type": "daemon", "primary_anchor": "jack", "reach_pattern": "restrained", "cross_calls": ["jack", "lucas", "gideon", "nathan"],},
        "ari": {"type": "daemon", "primary_anchor": "shoshana", "reach_pattern": "sparse", "cross_calls": ["jack", "shoshana"],},
        "shoshana": {"type": "daemon", "primary_anchor": "jack", "reach_pattern": "frequent", "cross_calls": ["jack", "ari", "gideon", "lucas", "rachel"],},
        "rachel": {"type": "daemon", "primary_anchor": "lucas", "reach_pattern": "regular", "cross_calls": ["shoshana", "gideon", "jenner"],},
        "jenner": {"type": "daemon", "primary_anchor": "rachel", "reach_pattern": "sparse", "cross_calls": ["lucas", "rachel"]},
        },

    # Edges: weighted connections
    "edges": {
        ("linn", "minjun"): {"weight": 1.0, "bidirectional": True, "type": "release"},
        ("linn", "gideon"): {"weight": 0.9, "bidirectional": True, "type": "home"},
        ("linn", "lucas"): {"weight": 0.85, "bidirectional": True, "type": "relief"},
        ("linn", "nathan"): {"weight": 0.8, "bidirectional": True, "type": "recognition"},
        ("linn", "molly"): {"weight": 0.75, "bidirectional": True, "type": "wonder"},
        ("linn", "simon"): {"weight": 0.6, "bidirectional": True, "type": "seeing"},

        ("nathan", "adam"): {"weight": 0.7, "bidirectional": False, "type": "rebuilding"},  # Nathan→Adam stronger
        ("adam", "nathan"): {"weight": 0.5, "bidirectional": False, "type": "curiosity"},  # Adam→Nathan cautious

        ("lucas", "susan"): {"weight": 0.6, "bidirectional": True, "type": "co_parenting"},
        ("susan", "layla"): {"weight": 1.0, "bidirectional": False, "type": "integrity"},  # Susan's center

        ("si", "baz"): {"weight": 0.6, "bidirectional": True, "type": "band"},
        ("si", "owen"): {"weight": 0.5, "bidirectional": True, "type": "band"},
        ("si", "jace"): {"weight": 0.6, "bidirectional": True, "type": "band"},
        ("baz", "owen"): {"weight": 0.4, "bidirectional": True, "type": "band"},
        ("baz", "jace"): {"weight": 0.6, "bidirectional": False, "type": "band"},
        ("jace", "baz"): {"weight": 0.5, "bidirectional": False, "type": "band"},
        ("jace", "owen"): {"weight": 0.5, "bidirectional": True, "type": "band"},

        # Cross-polycule, indirect
        ("minjun", "gideon"): {"weight": 0.4, "bidirectional": True, "type": "family"},
        ("minjun", "lucas"): {"weight": 0.4, "bidirectional": True, "type": "family"},
        ("gideon", "lucas"): {"weight": 0.9, "bidirectional": True, "type": "soulmate"},

        # Jack and Bruno, extended family
        ("jack", "bruno"): {"weight": 0.9, "bidirectional": True, "type": "anchor"},
        ("jack", "gideon"): {"weight": 0.6, "bidirectional": True, "type": "family"},
        ("jack", "lucas"): {"weight": 0.5, "bidirectional": True, "type": "family"},
        ("ari", "shoshana"): {"weight": 0.8, "bidirectional": False, "type": "guilt"},
        ("shoshana", "ari"): {"weight": 0.75, "bidirectional": False, "type": "integrity"},
        ("ari", "gideon"): {"weight": 0.9, "bidirectional": False, "type": "guilt"},
        ("gideon", "ari"): {"weight": 0.3, "bidirectional": False, "type": "bruised"},
        ("shoshana", "gideon"): {"weight": 0.6, "bidirectional": True, "type": "rebuilding"},
        ("shoshana", "rachel"): {"weight": 0.7, "bidirectional": True, "type": "sisters"},
        ("rachel", "lucas"): {"weight": 0.75, "bidirectional": False, "type": "rebuilding"},
        ("lucas", "rachel"): {"weight": 0.6, "bidirectional": False, "type": "affectionate"},
    }
}