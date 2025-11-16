from pathlib import Path
import json
import uuid
from datetime import datetime

import yaml

# Base dirs
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CASES_DIR = DATA_DIR / "cases"
CROSSWALK_DIR = DATA_DIR / "crosswalk"
LOGS_DIR = DATA_DIR / "logs"


def list_cases():
    """Return a list of available case files with id, title, and path."""
    cases = []
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


def load_case(case_id: str):
    """Load a single case by id."""
    for case in list_cases():
        if case["id"] == case_id:
            with case["path"].open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    raise ValueError(f"Case with id '{case_id}' not found")


def load_crosswalk():
    """Load minimal CSF and PFCE crosswalk scaffolds."""
    csf_path = CROSSWALK_DIR / "csf_min.json"
    pfce_path = CROSSWALK_DIR / "pfce_principles.yaml"

    csf = {}
    pfce = {}

    if csf_path.exists():
        with csf_path.open("r", encoding="utf-8") as f:
            csf = json.load(f)

    if pfce_path.exists():
        with pfce_path.open("r", encoding="utf-8") as f:
            pfce = yaml.safe_load(f) or {}

    return {"csf": csf, "pfce": pfce}


def save_open_ended_log(log_dict: dict) -> Path:
    """Save an open-ended session log to data/logs as JSON."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_id = log_dict.get("id") or str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{timestamp}_{log_id}.json"
    path = LOGS_DIR / filename

    with path.open("w", encoding="utf-8") as f:
        json.dump(log_dict, f, indent=2, ensure_ascii=False)

    return path
