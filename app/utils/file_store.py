import json
from pathlib import Path


def load_json(path: Path):
    if not path.exists():
        return []

    with open(path, "r") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
