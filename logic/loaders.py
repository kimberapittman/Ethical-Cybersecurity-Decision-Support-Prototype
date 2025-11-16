from pathlib import Path
import json
import yaml


# Base directory for the project (repo root)
BASE_DIR = Path(__file__).resolve().parents[1]


def _load_yaml(rel_path: str, default=None):
    """
    Helper to safely load a YAML file relative to the repo root.
    Returns `default` (or [] if default is None) if the file is missing.
    """
    path = BASE_DIR / rel_path
    if not path.exists():
        return [] if default is None else default
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_csf_data():
    """
    Load the compact NIST CSF 2.0 JSON (csf_min.json).
    """
    path = BASE_DIR / "data" / "csf_min.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_pfce_crosswalk():
    """
    Load the PFCE–CSF crosswalk scaffold YAML.
    """
    return _load_yaml("data/pfce_crosswalk_scaffold.yaml", default=[])


def load_pfce_principles():
    """
    Load the PFCE principles (beneficence, non-maleficence, autonomy, justice, explicability).
    """
    return _load_yaml("data/pfce_principles.yaml", default=[])


def load_constraints():
    """
    Load institutional / governance or scenario constraints.

    Note: if `scenario_constraints.yaml` does not exist, this will safely
    return an empty list so the app still loads.
    """
    return _load_yaml("data/scenario_constraints.yaml", default=[])


def load_municipal_dilemmas():
    """
    Optional: load pre-defined municipal dilemmas (case-based mode).
    Safe if the YAML is missing – returns [].
    """
    return _load_yaml("data/municipal_dilemmas.yaml", default=[])
