"""Bounded, atomic local Workspace storage. No privileged operations."""
import json
import os
from pathlib import Path
import tempfile

SPACES = ("personal", "creative", "development")
MAX_NOTE = 100_000


class StateStore:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.path = self.directory / "workspace.json"

    def load(self):
        default = {"theme": "dark", "notes": {key: "" for key in SPACES}}
        try:
            if self.path.stat().st_size > 2_000_000:
                return default
            value = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                return default
            default["theme"] = "light" if value.get("theme") == "light" else "dark"
            notes = value.get("notes", {})
            if isinstance(notes, dict):
                for key in SPACES:
                    if isinstance(notes.get(key), str):
                        default["notes"][key] = notes[key][:MAX_NOTE]
        except (OSError, ValueError):
            pass
        return default

    def save(self, value):
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=".workspace-", dir=self.directory)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(value, stream, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.path)
        finally:
            if os.path.exists(name):
                os.unlink(name)
