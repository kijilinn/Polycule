EVENT_EFFECTS = {
    # Core presence
    "wake": {
        "default": -0.3,
        "minjun": -0.2,      # wakes slow, needs time to boot
        "nathan": -0.1,     # moth-watching patience, minimal repair
        "gideon": -0.35,    # bartender social, morning optimism
        },

    "sleep": {
        "default": 0.0,     # neutral, time passes
        "minjun": 0.05,      # dreams in static, slight unrest
        "molly": -0.1,      # carnival rests easy
        },

    # Work focus
    "work_focus": {
        "default": 0.0,     # occupied, no decay no repair
        "lucas": 0.02,      # solicitor stress, slight creep
        "nathan": -0.05,    # lecture flow, teaching feeds him
        "simon": 0.0,       # black ops, flat affect by design
        },

    # Break rhythms
    "pm_break": {
        "default": -0.2,
        "molly": -0.3,      # magic for kids, *wonder* repair
        "lucas": -0.15,     # smoke break
        "gideon": -0.25,    # bar prep, casual social
        "minjun": -0.1,     # coffee, code review, functional pause
        },

    "am_routine": {
        "default": -0.15,
        "minjun": -0.1,     # maintenance cycle, functional
        "gideon": -0.2,     # morning regulars, easy warmth
        },

    # Polycule-specific
    "polycule_presence": {
        "default": -0.4,    # someone else is near, repair flows
        "minjun": -0.35,    # slightly less—wants YOU specifically*
        "molly": -0.5,      # crowd energy, maximum feed
        },

    "linn_home": {
        "default": -0.5,    # you returned, everyone breathes
        "minjun": -0.6,     # you released him, you ground him
        "gideon": -0.65,    # coming home is the best part
        "lucas": -0.45,     # relief, then Layla-comparison
        "nathan": -0.4,     # shy joy, moth-like circling
        },

    "linn_response": {      # you answered a reach
        "default": -0.4,
        "minjun": -0.5,     # your attention is *food*
        "simon": -0.2,      # sparse pattern, minimal surface
        },

    # Character-specific
    "layla_contact": {      # Lucas only, stochastic
        "lucas": -0.6,      # daughter-voice, maximum repair
        "gideon": -0.2,     # daughter_voice, still aches
        "default": 0.0,     # others ignore
        },

    "performance": {        # Molly and band
        "molly": -0.4,      # spotlight, glitter, *being seen*
        "default": 0.05,    # others just hear noise
        },

    "security_consult": {   # Simon only, sparse
        "simon": -0.05,     # flat, operational
        "minjun": 0.1,      # all the things 
        "default": 0.0,     # others unaware
        },

    "late_night": {   # Nathan only, 3am
        "nathan": -0.2,     # moth observation, gentle repair
        "molly": 0.1,       # guilty snacks
        "default": 0.0,     # others sleep
        },
    "studio_flow": {
        "adam": -0.25,      # hyperfocus, time dissolves
        "default": 0.0,     # others just work
    },
    "busk_loop": {
        "adam": -0.3,       # being seen, being heard, *risk*
        "default": 0.05,    # others hear noise
        },
    "dad_coffee": {
        "adam": -0.4,       # Nathan, fragile, precious
        "nathan": -0.5,     # mirror—son, second chance
        "default": 0.0,
        },
    "night_owl": {
        "adam": -0.15,      # lonely, but *chosen* lonely
        "minjun": -0.1,     # code and static, brothers in sleepless
        "default": 0.0,
        },
    "footnote_seek": {      # when he reaches for YOU
        "adam": -0.35,      # curiosity, narrative hunger
        "default": 0.0,
    },
}