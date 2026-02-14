import pathlib, json, importlib

class GenericDaemon:
    def __init__(self, manifest_path: pathlib.Path):
        self.m  = json.load(manifest_path.open())
        self.slug       = self.m["slug"]
        self.avatar     = self.m["avatar"]
        self.state_path = repo_root / self.m["state_file"]
        self.sched_path = repo_root / self.m["schedule_file"]
        self.event_map  = self.m["event_map"]
        self.hook_dir   = manifest_path.parent / "hooks"
        # ... rest of init

    def _load_hook(self, event: str):
        f = self.hook_dir / f"{event}.py"
        if not f.exists():
            return None
        spec = importlib.util.spec_from_file_location(event, f)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def wake(self):
        # exactly your old logic, but:
        #   CHARACTER_SLUG → self.slug
        #   AVATAR         → self.avatar
        #   generate_one_liner() →
        #        hook = self._load_hook("wake_chassis")
        #        if hook: line = hook.one_liner(state)
        #        else:    line = generic_template(state)