import json
from pathlib import Path
from typing import Dict, Set


class ExtensionManager:
    _data: Dict[str, Set[str]]

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> Dict[str, Set[str]]:
        if not self.path.exists():
            return {}
        with open(self.path) as f:
            raw = json.load(f)
        return {k: set(v) for k, v in raw.items()}

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(
                {k: sorted(v) for k, v in self._data.items()},
                f,
                indent=2,
            )

    def _validate_ext(self, ext: str):
        if not ext or not isinstance(ext, str):
            raise ValueError("Extension must be a non-empty string")
        if ext.startswith("."):
            ext = ext[1:]
        return ext.lower()

    def add_extension(self, category: str, ext: str):
        ext = self._validate_ext(ext)
        self._data.setdefault(category, set()).add(ext)
        self._save()

    def remove_extension(self, category: str, ext: str):
        ext = self._validate_ext(ext)
        if category in self._data and ext in self._data[category]:
            self._data[category].remove(ext)
            if not self._data[category]:
                del self._data[category]  # auto-remove empty categories
            self._save()
        else:
            raise KeyError(f"{ext} not found in {category}")

    @property
    def data(self):
        return self._data
