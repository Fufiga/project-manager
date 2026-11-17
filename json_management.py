import json
from dataclasses import dataclass, asdict
from pathlib import Path


GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
BLUE   = "\033[34m"
RED    = "\033[31m"
GOLD = "\033[38;5;220m"
ORANGE = "\033[38;5;208m"
RESET = "\033[0m"


FILE = Path("data.json")


@dataclass
class Project:
    id: int
    name: str
    path: str
    language: list[str]
    last: bool


def _load():
    """Read the file and return a list of dicts (empty list if no file yet)."""
    if not FILE.exists():
        return []
    return json.loads(FILE.read_text(encoding="utf-8"))


def _save(data):
    FILE.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def is_empty():
    """Return True if the JSON file is missing, blank, or contains no projects."""
    if not FILE.exists():
        return True

    text = FILE.read_text(encoding="utf-8").strip()
    if not text:
        return True

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return True

    return not data


def put_intoJson(project):
    """Add a Project to the JSON file. Refuses duplicates by name."""
    data = _load()

    if any(d["name"].lower() == project.name.lower() for d in data):
        print(f"'{project.name}' already exists, not added.")
        return False

    project.id = max((d["id"] for d in data), default=0) + 1
    data.append(asdict(project))
    _save(data)
    return True


def retrieve_projectName(name):
    """Return the Project with this name, or None if not found."""
    for d in _load():
        if d["name"].lower() == name.lower():
            return Project(**d)
    return None


def retrieve_projectId(id):
    for d in _load():
        if d["id"] == int(id):
            return Project(**d)
    return None


def retrieve_last():
    for d in _load():
        if d["last"] == True:
            return Project(**d)
    return None


def switch_last(name):
    data = _load()                      # list of dicts

    target = None
    for d in data:
        if d["name"].lower() == name.lower():
            target = d
        d["last"] = False               # reset everyone

    if target is None:
        print(f"Project '{name}' not found.")
        return False

    target["last"] = True               # then flag the one we open
    _save(data)
    return True


def exists(name):
    data = _load()

    for d in data:
        if d["name"].lower() == name.lower():
            return True
    return False


def exists_id(id):
    data = _load()

    for d in data:
        if d["id"] == id:
            return True
    return False


def show_infos():
    data = _load()
    projectId = max((d["id"] for d in data), default=0)
    if projectId == 0:
        print("You have no projects.")
        return None
    print("Here are your projects: ")
    for d in _load():
        if (d["last"] == False):
            print("   " + str(d["id"]) + ". " + d["name"])
        else:
            print("   " + str(d["id"]) + ". " + GOLD + d["name"] + "*", RESET)
    print()
    print("* last opened project")


def registered_paths():
    return [Path(d["path"]).expanduser().resolve() for d in _load()]


def delete_project(name):
    data = _load()
    remaining = [d for d in data if d["name"].lower() != name.lower()]
    if len(remaining) == len(data):
        return False

    for new_id, d in enumerate(remaining, start=1):
        d["id"] = new_id
    _save(remaining)
    return True
