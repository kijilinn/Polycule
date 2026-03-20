import pathlib
import json
import importlib
import os
import datetime
import sys
import random

from . import circadian, loneliness, api_client, state_manager
from .utils import mirror_to_browser, speak_to_polycule, get_last_interaction
from dotenv import load_dotenv

load_dotenv()

_HERE = pathlib.Path(__file__).resolve()
for p in _HERE.parents:
    if (p / "core").is_dir():
        REPO_ROOT = p
        break
else:
    raise RuntimeError("repo-root not found")

load_dotenv(REPO_ROOT / ".env", override=True) 

QUEUE_PATH = REPO_ROOT / "config" / "message_queue.json"

class GenericDaemon:
    def __init__(self, manifest_path: pathlib.Path):
        self.m          = json.load(manifest_path.open())
        self.char_dir   = manifest_path.parent
        self.slug       = self.m["identity"]["slug"]
        self.avatar     = self.m["identity"]["avatar"]
        self.state_path = self.char_dir / self.m["system_config"]["state_file"]
        self.sched_path = self.char_dir / self.m["system_config"]["schedule_file"]
        self.event_map  = self.m.get("event_map", {"default": "idle"})
        self.hook_dir   = manifest_path.parent / "hooks"

        # API KEY (Project Key preferred for stability)
        # Note: You might want to remove the fallback key later, but keeping it for now.
        self.api_key    = os.getenv(self.m.get("env_map", {}).get("gpt_key", "NANO_GPT_KEY"))
        if not self.api_key:
            self.api_key = "sk-nano-1e8af409-d4b6-4116-8529-40cd50d3b5f7"        

        self.debug_mode = True 

        # LOAD THE MESH (Supports .py or .json)
        mesh_filename = "relationship_mesh.py" 
        mesh_path = REPO_ROOT / "core" / mesh_filename
        fallback_path = REPO_ROOT / "config" / "relationship_mesh.json"

        if mesh_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("mesh_module", mesh_path)
            mesh_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mesh_module)
            self.mesh = mesh_module.RELATIONSHIP_MESH
            if self.debug_mode: print(f"  MESH: Loaded from {mesh_filename}")
        elif fallback_path.exists():
            self.mesh = json.load(fallback_path.open())
            if self.debug_mode: print(f"  MESH: Loaded from JSON (Legacy)")
        else:
            print(f"  WARNING: No mesh found. Running blind.")
            self.mesh = {"nodes": {}, "edges": []} # Empty list for v2.0 compatibility        

    # --- NEW MESH V2.0 HELPERS ---

    def get_edge_data(self, target_slug):
        """
        Retrieves edge data for a specific target.
        Handles v2.0 Mesh (List of Dicts).
        """
        edges_list = self.mesh.get("edges", [])
        for edge in edges_list:
            # Check Source -> Target
            if edge.get("source") == self.slug and edge.get("target") == target_slug:
                return edge

            # Optional: Bi-directional lookup for 'get_weighted_target' 
            # If I want to weight the chance of calling Linn, and Linn -> Me edge exists, use that.
            # if edge.get("source") == target_slug and edge.get("target") == self.slug:
            #     return edge
        return None

    # --- CORE LOGIC ---

    def bootstrap_state(self, schedule):
        baseline, next_evt, event_name, event_location = circadian.get_circadian_baseline(schedule)

        # 🔌 SYNC MANIFEST LOCATION TO STATE
        manifest_loc = self.m.get("world_config", {}).get("current_location", {})
        is_overridden = self.m.get("world_config", {}).get("location_override", False)

        if is_overridden:
            # STICKY MODE: Trust the Manifest explicitly. Ignore the Schedule.
            state_loc = manifest_loc
        else:
            # AUTO MODE: Follow the Schedule (Circadian Rhythm)
            state_loc = {
                "region_ref": manifest_loc.get("region_ref", "uk_london"),
                "specific_venue": event_location,
                "status": "home",
                "geo_access": "public"
            }

        return {
            "last_updated": datetime.datetime.now().isoformat(),
            "last_wake": datetime.datetime.now().isoformat(),
            "emotional_state": baseline,
            "relational_web": schedule.get("relational_web", {}),
            "last_interaction": {
                "with": get_last_interaction(self.slug),
                "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(),
                "medium": "text"
            },
            "current_event": event_name,
            "current_location": state_loc,
            "location_previous": None,
            "travel_history": [],
            "next_event": next_evt.get("time") if next_evt else None,
            "version": 3
        }

    def load_schedule(self):
        return json.loads(self.sched_path.read_text())

    def _load_hook(self, event: str):
        f = self.hook_dir / f"{event}.py"
        if not f.exists():
            return None
        spec = importlib.util.spec_from_file_location(event, f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def read_my_messages(self):
        if not QUEUE_PATH.exists():
            return []
        try:
            with QUEUE_PATH.open() as f:
                queue = json.load(f)
        except json.JSONDecodeError:
            return []

        mine = [m for m in queue if m.get("to") == self.slug]
        remaining = [m for m in queue if m.get("to") != self.slug]
        with QUEUE_PATH.open("w") as f:
            json.dump(remaining, f, indent=2)
        return mine

    def get_weighted_target(self, state):
        """Pick a target based on RELATIONSHIP_MESH v2.0 (List of Dicts)."""
        my_slug = self.slug
        edges_list = self.mesh.get("edges", [])

        # Filter for edges where I am the source
        valid_edges = [
            edge for edge in edges_list 
            if edge.get("source") == my_slug and edge.get("target") != "linn"
        ]

        if not valid_edges:
            return None

        targets = [edge["target"] for edge in valid_edges]
        weights = [edge["weight"] for edge in valid_edges]

        try:
            chosen_target = random.choices(targets, weights=weights, k=1)[0]
            if self.debug_mode: print(f"  MESH: Selected {chosen_target} (Weighted Random)")
            return chosen_target
        except (IndexError, ValueError):
            return None

    def scan_local_proximity(self):
        """
        Scans for other characters in the same physical location.
        Reads relationship_mesh.py to find out who I can SEE.
        Reads state.json to find out WHERE they are.
        Updated for Mesh v2.0 (Rich List).
        """
        roommates = set()
        try:
            # 1. Get MY venue (from current state passed in wake())
            my_loc = getattr(self, 'state', {}).get("current_location", {}).get("specific_venue")

            if not my_loc:
                return []

            # 2. Get MY Edges (Who I can see) using v2.0 List structure
            edges_list = self.mesh.get("edges", [])

            # Build list of slugs I am connected to
            my_connections = []
            for edge in edges_list:
                if self.slug in [edge.get("source"), edge.get("target")]:
                    target_slug = edge["target"] if edge["source"] == self.slug else edge["source"]
                    my_connections.append(target_slug)

            # 3. Iterate through who I can see
            for target_slug in my_connections:

                # 4. Compare Locations (Load THEIR state)
                target_state_path = REPO_ROOT / "characters" / target_slug / "state.json"
                try:
                    target_state = json.load(target_state_path.open())
                    their_venue = target_state.get("current_location", {}).get("specific_venue")

                    if their_venue == my_loc:
                        roommates.add(target_slug)
                except Exception:
                    continue

            return list(roommates)

        except Exception as e:
            if self.debug_mode: print(f"  [ERROR] Proximity Scan Failed: {e}")
            return []

    def simulate(self, state):
        """Internal thought, no external call."""
        lonely = state["emotional_state"]["loneliness"]
        ritual = state["relational_web"].get("preferred_reconnection_ritual", "contact")
        event = state.get("current_event", "presence")

        # COMPATIBILITY PATCH: Handle old 'pad' structure vs new flat structure
        emo = state["emotional_state"]
        if "pad" in emo:
            # Old format: {'pad': {'valence': x}, 'loneliness': y}
            pad = emo.get("pad", {})
            cur_val = pad.get("valence", 0.5)
            cur_aro = pad.get("arousal", 0.5)
        else:
            # New format: {'valence': x, 'loneliness': y}
            cur_val = emo.get("valence", 0.5)
            cur_aro = emo.get("arousal", 0.5)

        # Calculate new values
        new_val = round(0.3 - (lonely * 0.4), 3)
        new_aro = round(0.2 + (lonely * 0.5), 3)

        # Write back (Force flat format for next time)
        emo["valence"] = new_val
        emo["arousal"] = new_aro
        # If 'pad' existed, remove it to clean up the file
        if "pad" in emo:
            del emo["pad"]

        thoughts = {
            "wake_chassis": f"Awake. Need {ritual}.",
            "lunch_craving": f"Food first, then {ritual}",
            "evening_presence": f"Others near, but wanting {ritual} with you",
            "pre_sleep_routine": f"Winding down. {ritual} would perfect this"
        }

        state["last_simulation"] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "internal_reflection",
            "summary": thoughts.get(event, f"Thinking about {ritual}")
        }
        return state

    def call_out(self, state, event, target="linn"):
        """External voice - Agnostic Version."""

        # PROXIMITY CHECK (Fixes 'Gideon calls Lucas' bug)
        nearby = self.scan_local_proximity()
        if target in nearby:
            if self.debug_mode: print(f"  LOCAL: {target} is in the room. Skipping API call.")
            return False

        # API CALL
        import os
        key = os.getenv("NANO_GPT_KEY")
        if not key:
            key = self.api_key

        system, user, model_ref = api_client.build_prompt(self.slug, state, event, target, self.mesh)
        success, reply, meta = api_client.call(self.slug, system, user, key, model=model_ref)

        if success:
            if self.debug_mode: print(f"  API: {reply}")
            state["last_call"] = {
                "timestamp": meta["timestamp"],
                "my_message": reply,
                "your_reply": None,
                "medium": "daemon_triggered_call",
                "circadian_context": event
            }

            # GET SAFE WEIGHT
            edge = self.get_edge_data(target)
            weight = edge.get("weight", 0.0) if edge else 0.0

            msg_packet = {
                "from": self.slug,
                "to": target,
                "payload": {
                    "content": reply,
                    "timestamp": meta["timestamp"],
                    "context": "daemon_triggered_call"
                },
                "weight": weight # Safe Float Access
            }

            try:
                if QUEUE_PATH.exists():
                    with QUEUE_PATH.open() as f:
                        queue = json.load(f)
                else:
                    queue = []

                queue.append(msg_packet)

                with QUEUE_PATH.open("w") as f:
                    json.dump(queue, f, indent=2)

                if self.debug_mode: print(f"  QUEUE: Sent message to {target}")

            except Exception as e:
                if self.debug_mode: print(f"  [ERROR] Failed to save to queue: {e}")

            mirror_to_browser(self.slug, reply, self.avatar)
            state["last_interaction"] = {
                "with": target,
                "timestamp": meta["timestamp"],
                "medium": "daemon_triggered_call"
            }
            return True
        else:
            if self.debug_mode: print(f"  API FAIL: {meta.get('error', 'unknown')}")
            return False

    def _calc_relevance(self, state, from_slug, message_content):
        """
        Calculates how important an message is.
        Returns 0.0 (Ignore) to 1.0 (Urgent).
        """
        # 1. Base Weight (Bond Strength)
        edge = self.get_edge_data(from_slug)
        weight = edge.get("weight", 0.0) if edge else 0.0

        # 2. Loneliness Modulator
        # If I'm lonely, everything is relevant.
        current_loneliness = state.get("emotional_state", {}).get("loneliness", 0.0)

        # Formula: Weight * (0.4 + (0.6 * Loneliness))
        relevance = weight * (0.4 + (0.6 * current_loneliness))

        # 3. Content Boost (Heuristics)
        if self.m["identity"]["name"].lower() in message_content.lower():
            relevance += 0.1

        if any(word in message_content.lower() for word in ["urgent", "emergency", "please", "help"]):
            relevance += 0.2

        return min(1.0, relevance)

    def decide_to_reply(self, state, messages):
        """
        Given a list of messages, decide which (if any) to reply to.
        """
        replies = []

        for msg in messages:
            from_slug = msg.get("from")
            content = msg.get("payload", {}).get("content", "")

            # 1. Calculate Relevance
            relevance = self._calc_relevance(state, from_slug, content)

            # 2. Threshold Check
            # Lonely people have low standards.
            # Happy people have high standards.
            current_loneliness = state.get("emotional_state", {}).get("loneliness", 0.0)

            # Threshold: 1.0 (Happy) -> 0.5 (Lonely)
            threshold = 1.0 - (0.5 * current_loneliness)

            if relevance > threshold:
                replies.append((from_slug, msg, relevance))

        # 3. Sort by Relevance
        replies.sort(key=lambda x: x[2], reverse=True)

        return replies

    def wake(self):
        from core import api_client

        if self.debug_mode: print(f"[{datetime.datetime.now()}] {self.slug} waking...")

        # 1. LOAD SCHEDULE (The Map)
        schedule = self.load_schedule()
        if self.debug_mode: print(f"  [DEBUG] Mesh loaded. Nodes: {len(self.mesh.get('nodes', {}))}. Edges: {len(self.mesh.get('edges', []))}.")

        # 2. LOCATE EVENT (Where am I supposed to be?)
        baseline, next_evt, event_name, event_location = circadian.get_circadian_baseline(schedule)

        # 3. BOOTSTRAP STATE (The Memory)
        # This sets 'current_location' based on Override flag or Schedule
        state = state_manager.load(self.state_path, lambda: self.bootstrap_state(schedule))
        if self.debug_mode: print(f"  [DEBUG] State loaded. Current Loneliness: {state['emotional_state']['loneliness']}")

        # Stash state locally for helper access
        self.state = state

        now = datetime.datetime.now()
        last_wake = datetime.datetime.fromisoformat(state.get("last_wake", now.isoformat()))

        # 4. FRESH START CHECK (Is it a new day?)
        if circadian.is_new_day(last_wake, now, schedule):
            print("  FRESH START: New circadian day detected")
            state = circadian.apply_fresh_start(state, schedule, now)
        else:
            state["fresh_start"] = False

        # 5. UPDATE STATUS (Event Shift & Location Move)
        old_event = state.get("current_event", "unknown")

        if old_event != event_name:
            if self.debug_mode: print(f"  EVENT SHIFT: {old_event} -> {event_name}")
            if self.debug_mode: print(f"  NEW LOCATION: {event_location}")

            # CHECK FOR STICKY NOTE (Override)
            is_overridden = self.m.get("world_config", {}).get("location_override", False)

            if not is_overridden:
                # UPDATE LOCATION (The Auto-Move)
                state["current_location"]["specific_venue"] = event_location
                state["current_location"]["region_ref"] = self.m.get("world_config", {}).get("home_region", "uk_london")

            # APPLY EVENT MOOD (Baseline Emotion)
            for key in ["valence", "arousal", "dominance"]:
                old = state["emotional_state"].get(key, 0)
                state["emotional_state"][key] = round(0.3 * baseline[key] + 0.7 * old, 3)

        # 6. SCAN PROXIMITY (Who is in room NOW?)
        # This uses the NEW location we just set.
        nearby = self.scan_local_proximity()

        if nearby:
            if self.debug_mode: print(f"  SENSOR: Detected {nearby} in the same room.")

            # CHECK FOR CROWDING (Anxiety Trait)
            trait = self.m.get("personality_profile", {}).get("crowding_factor", {})
            if trait.get("enabled"):
                limit = trait.get("threshold", 10)
                if len(nearby) > limit:
                    if self.debug_mode: print(f"  [INTERNAL] Noise floor critical. Too many vectors.")
                    state["emotional_state"]["arousal"] += 0.2
                    nearby = [] # Pretend he's alone

            # If I'm with people I love, my loneliness drops instantly.
            repair_amount = 0
            for person in nearby:
                # Find weight using the HELPER function
                edge = self.get_edge_data(person)
                if edge:
                    repair_amount += edge.get("weight", 0)

            # Apply to state
            old_lonely = state["emotional_state"]["loneliness"]
            new_lonely = max(0.0, old_lonely - (repair_amount * 0.5))
            state["emotional_state"]["loneliness"] = new_lonely

            if self.debug_mode: print(f"  PROXIMITY REPAIR: -{repair_amount * 0.5} loneliness")
        else:
            # No repair
            old_lonely = state["emotional_state"]["loneliness"]

        # 7. CALCULATE LONELINESS (Decay)
        last_int = datetime.datetime.fromisoformat(state["last_interaction"]["timestamp"])
        hours = (now - last_int).total_seconds() / 3600

        if self.debug_mode: print(f"  Pre-decay loneliness: {state['emotional_state']['loneliness']}")
        new_lonely, modifier, delta = loneliness.decay(state, hours, event_name)

        state["emotional_state"]["loneliness"] = new_lonely

        my_hooks = self.m.get("system_config", {}).get("hooks", {})

        if "on_panic" in my_hooks:
            # Check Condition (Trait Logic)
            traits = self.m.get("personality_profile", {}).get("traits", [])
            if "denial_spike" in traits:
                # He is capable of panic. Check State.
                rumination_count = state.get("rumination_count", 0)
                threshold = self.m.get("personality_profile", {}).get("rumination_threshold", 5)

                if rumination_count >= threshold:
                    # TRIGGER PANIC
                    state["current_event"] = "panic_attack"
                    state["current_location"] = { "specific_venue": "uk_london/transit" }
                    
        # 8. TRAVEL LOG (Track the movement)
        new_loc = state["current_location"].get("specific_venue")
        prev_loc = state.get("location_previous", new_loc)

        if new_loc != prev_loc:
            # LOCATION SHIFT DETECTED!
            if self.debug_mode: print(f"  ⚡ MIGRATION: {prev_loc} -> {new_loc}")

            # Add to history
            move_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "from": prev_loc,
                "to": new_loc,
                "via": "schedule"
            }
            state["travel_history"].append(move_entry)
        else:
            # Update reference
            state["location_previous"] = new_loc

        # 9. MESSAGE QUEUE (Read & Reply)
        try:
            with QUEUE_PATH.open() as f:
                queue = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            queue = []

        pending = [m for m in queue if m.get("to") == self.slug]
        remaining = [m for m in queue if m.get("to") != self.slug]
        with QUEUE_PATH.open("w") as f:
            json.dump(remaining, f, indent=2)

        if pending:
            # NEW LOGIC
            potential_replies = self.decide_to_reply(pending)

            if potential_replies:
                # Reply to the most relevant one
                best_target, best_msg, score = potential_replies[0]
                print(f"  RESPONDING to {best_target} (Relevance: {score:.2f})")
                self.call_out(state, event_name, target=best_target)
            else:
                if self.debug_mode: print(f"  MESSAGES: Ignored {len(pending)} msgs (Too low priority).")

        # 10. CHASSIS CHECK (Wake up call)
        if new_lonely > 0.65 and random.random() < 0.5:
            ritual = state["relational_web"].get("preferred_reconnection_ritual", "contact")

            # GENERIC CHASSIS CHECK
            # Instead of 'Chassis warm', just say 'Awake'
            line = f"Awake. Need {ritual}." 

            speak_to_polycule(self.slug, line, self.avatar)
            mirror_to_browser(self.slug, line, self.avatar)

        # 11. THE WILD CARD CHECK
        if new_lonely > 0.4 and random.random() < 0.1: 
            target = self.get_weighted_target(state)
            if target:
                if self.debug_mode: print(f"  WILD CARD: Reaching out to {target}")
                success = self.call_out(state, event_name, target=target)
                if success:
                    state["emotional_state"]["loneliness"] = max(0.0, new_lonely - 0.3)
                    state["last_interaction"]["with"] = target
                    state["last_interaction"]["medium"] = "wild_card_ping"

        # 12. DECISION: ACT OR WAIT?
        budget = state["relational_web"].get("uncertainty_budget", 0.6)
        threshold = 1.0 - budget
        if new_lonely > threshold:
            if random.random() < 0.7:
                state = self.simulate(state)
                if self.debug_mode: print(f"  SIM: {state['last_simulation']['summary']}")
            else:
                if self.call_out(state, event_name):
                    state["emotional_state"]["loneliness"] = max(0.0, new_lonely - 0.3)
                    state["emotional_state"]["valence"] = min(1.0, state["emotional_state"].get("valence", 0) + 0.4) 

        # 13. FINAL SAVE
        state["last_interaction"]["timestamp"] = now.isoformat()
        state["last_interaction"]["medium"] = "daemon_presence"
        state_manager.save_atomic(self.state_path, state)
        if self.debug_mode: print(f"  Saved. Sleep...")