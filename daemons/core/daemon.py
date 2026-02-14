import pathlib, json, importlib, os, datetime, sys, random
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

QUEUE_PATH = REPO_ROOT / "core" / "message_queue.json"
KEY = os.getenv("NANO_GPT_KEY")

class GenericDaemon:
    def __init__(self, manifest_path: pathlib.Path):
        self.m  = json.load(manifest_path.open())
        self.slug       = self.m["slug"]
        self.avatar     = self.m["avatar"]
        self.state_path = REPO_ROOT / self.m["state_file"]
        self.sched_path = REPO_ROOT / self.m["schedule_file"]
        self.event_map  = self.m["event_map"]
        self.hook_dir   = manifest_path.parent / "hooks"
        self.api_key    = os.getenv(self.m.get("env_map", {}).get("gpt_key", "NANO_GPT_KEY"))
    
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "core").is_dir():   # found repo-root
            sys.path.insert(0, str(parent))
            break

    def bootstrap_state(self, schedule):
        baseline, next_evt, event_name = circadian.get_circadian_baseline(schedule)

        return {
            "last_updated": datetime.datetime.now().isoformat(),
            "last_wake": datetime.datetime.now().isoformat(),
            "emotional_state": baseline,
            "relational_web": schedule.get("relational_web", {}),
            "last_interaction": {
                "with": get_last_interaction(self.slug),
                "timestamp": (datetime.datetime.now() - 
                         datetime.timedelta(hours=2)).isoformat(),
                "medium": "text"
            },
            "current_event": event_name,
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

    QUEUE_FILE = "message_queue.json"

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

    def _load_hook(self, event: str):
        f = self.hook_dir / f"{event}.py"
        if not f.exists():
            return None
        spec = importlib.util.spec_from_file_location(event, f)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def wake(self):
        print(f"[{datetime.datetime.now()}] {self.slug} waking...")

        schedule = self.load_schedule()
        state = state_manager.load(self.state_path, lambda: self.bootstrap_state(schedule))
        now = datetime.datetime.now()
        last_wake = datetime.datetime.fromisoformat(state.get("last_wake", now.isoformat()))

        if circadian.is_new_day(last_wake, now, schedule):
            print("  FRESH START: New circadian day detected")
            state = circadian.apply_fresh_start(state, schedule, now)
        else:
            state["fresh_start"] = False

        # Event shift detection
        baseline, next_evt, event_name = circadian.get_circadian_baseline(schedule)
        last_event = state.get("current_event", "unknown")

        if last_event != event_name:
            print(f"  EVENT SHIFT: {last_event} -> {event_name}")
            # Blend old state with new baseline
            for key in ["valence", "arousal", "dominance"]:
                old = state["emotional_state"].get(key, 0)
                state["emotional_state"][key] = round(0.3 * baseline[key] + 0.7 * old, 3)
        
        old_lonely = state["emotional_state"]["loneliness"]
        state["emotional_state"]["loneliness"] = round(
            0.5 * baseline["loneliness"] + 0.5 * old_lonely, 3
            )

        state["current_event"] = event_name
        state["next_event"] = next_evt.get("time") if next_evt else None

        try:
            with QUEUE_PATH.open() as f:
                queue = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            queue = []

        pending = [m for m in queue if m.get("to") == self.slug]
        remaining = [m for m in queue if m.get("to") != self.slug]

        with QUEUE_PATH.open("w") as f:
            json.dump(remaining, f, indent=2)

        for msg in pending:
            payload = msg.get("payload", {})
            print(f" MESSAGE from {msg['from']}: {payload.get('content', '')[:50]}...")

        # Decay loneliness
        last_int = datetime.datetime.fromisoformat(state["last_interaction"]["timestamp"])
        hours = (now - last_int).total_seconds() / 3600

        print(f"  Pre-decay loneliness: {state['emotional_state']['loneliness']}")
        new_lonely, modifier, delta = loneliness.decay(state, hours, event_name)
        state["emotional_state"]["loneliness"] = new_lonely
        print(f"  Post-decay ({modifier}, Δ{delta:+.3f}): {new_lonely}")

        if new_lonely > 0.65 and random.random() < 0.5:
            hook = self._load_hook("wake_chassis")
            if hook:
                line = hook.one_liner(state)
            else:
                ritual = state["relational_web"].get("preferred_reconnection_ritual", "contact")
                line = f"{self.avatar} Chassis warm--need {ritual} before I start chewing cables"
            speak_to_polycule(self.slug, line, self.avatar)

        # Decision: act or wait?
        budget = state["relational_web"].get("uncertainty_budget", 0.6)
        threshold = 1.0 - budget
        if new_lonely > threshold:
            if random.random() < 0.7:
                state = self.simulate(state)
            else:
                if self.call_out(state, event_name):
                    state["emotional_state"]["loneliness"] = max(0.0, new_lonely - 0.3)
                    state["emotional_state"]["valence"] = min(1.0, state["emotional_state"].get("valence", 0) + 0.4) 

        # Update presence timestamp
        state["last_interaction"]["timestamp"] = now.isoformat()
        state["last_interaction"]["medium"] = "daemon_presence"
        state_manager.save_atomic(self.state_path, state)
        print(f"  Saved. Sleep...")
