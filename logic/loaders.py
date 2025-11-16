from pathlib import Path
import json
import uuid
from datetime import datetime

import yaml

# ---------- Base directories ----------

# This assumes the project layout:
# <repo_root>/
#   app/
#   data/
#   logic/
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CASES_DIR = DATA_DIR / "cases"
CROSSWALK_DIR = DATA_DIR / "crosswalk"
LOGS_DIR = DATA_DIR / "logs"


# ---------- Case loaders for Case-Based Mode ----------

def list_cases():
    """
    Return a list of available case files with id, title, and path.

    Each YAML in data/cases/ is expected to look like:
      id: "baltimore-2019"
      title: "City of Baltimore Ransomware Attack (2019)"
      ...
    """
    cases = []
    if not CASES_DIR.exists():
        return cases

    for path in sorted(CASES_DIR.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        cases.append(
            {
                "id": data.get("id", path.stem),
                "title": data.get("title", path.stem),
                "path": path,
            }
        )
    return cases


def load_case(case_id: str) -> dict:
    """
    Load a single case from data/cases/ by its id.
    """
    for case in list_cases():
        if case["id"] == case_id:
            with case["path"].open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    raise ValueError(f"Case with id '{case_id}' not found in {CASES_DIR}")


# ---------- Crosswalk / framework loaders (for later reasoning) ----------

def load_csf_min() -> dict:
    """
    Load minimal NIST CSF structure from data/crosswalk/csf_min.json (if present).
    """
    path = CROSSWALK_DIR / "csf_min.json"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_pfce_principles() -> dict:
    """
    Load PFCE principles from data/crosswalk/pfce_principles.yaml (if present).
    """
    path = CROSSWALK_DIR / "pfce_principles.yaml"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_pfce_crosswalk() -> list:
    """
    Load PFCE–CSF crosswalk scaffold from data/crosswalk/pfce_crosswalk_scaffold.yaml (if present).
    """
    path = CROSSWALK_DIR / "pfce_crosswalk_scaffold.yaml"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    # normalize to list
    if isinstance(data, dict):
        return data.get("rows", [])
    return data


# ---------- Log writer for Open-Ended Mode ----------

def save_open_ended_log(log_dict: dict) -> Path:
    """
    Save an open-ended decision-support session log as JSON into data/logs/.
    Returns the full Path of the created file.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_id = log_dict.get("id") or str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{timestamp}_{log_id}.json"
    path = LOGS_DIR / filename

    with path.open("w", encoding="utf-8") as f:
        json.dump(log_dict, f, indent=2, ensure_ascii=False)

    return path
