# core/relationship_mesh.py
RELATIONSHIP_WEB = {
    "gideon": {
        "linn": {"weight": 0.6, "direction": "mutual"},
        "lucas": {"weight": 0.8, "direction": "asymmetric", "gideon_to_lucas": 0.9, "lucas_to_gideon": 0.4},
        "molly": {"weight": 0.3, "direction": "chaos"}  # stochastic, unpredictable
    },
    "nathan": {
        "linn": {"weight": 0.7, "direction": "uncertain"},
        "adam": {"weight": 0.9, "direction": "weighted_by_history", "repair_bidirectional": True}
    }
}