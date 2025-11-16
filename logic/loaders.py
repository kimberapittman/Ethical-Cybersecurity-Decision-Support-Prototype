from pathlib import Path
import json
import yaml

# ---------- Base paths ----------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"


# ---------- Internal helpers ----------

def _load_yaml(filename: str):
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_json(filename: str):
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Public loader functions ----------

def load_csf_data():
    """
    Load the minimized NIST CSF 2.0 reference data (csf_min.json).
    """
    return _load_json("csf_min.json")


def load_pfce_crosswalk():
    """
    Load the PFCE × NIST CSF crosswalk scaffold (pfce_crosswalk_scaffold.yaml).
    """
    return _load_yaml("pfce_crosswalk_scaffold.yaml")


def load_pfce_definitions():
    """
    Load PFCE principle definitions (pfce_principles.yaml).
    Returns the 'principles' mapping.
    """
    data = _load_yaml("pfce_principles.yaml")
    return data.get("principles", data)


def load_constraints():
    """
    Load institutional and governance constraints (scenario_constraints.yaml).
    """
    return _load_yaml("scenario_constraints.yaml")


def load_municipal_dilemmas():
    """
    Load case / dilemma metadata (municipal_dilemmas.yaml).
    """
    return _load_yaml("municipal_dilemmas.yaml")


# ---------- Standalone test runner ----------

if __name__ == "__main__":
    print("Working directory:", BASE_DIR)
    print("Data directory   :", DATA_DIR)

    # Test CSF data
    try:
        csf = load_csf_data()
        print(f"\n[OK] csf_min.json loaded. Type: {type(csf)}, length: {len(csf)}")
        if isinstance(csf, dict):
            print("     Keys:", list(csf.keys())[:5])
        elif isinstance(csf, list) and csf:
            print("     First entry sample:", csf[0])
    except Exception as e:
        print("\n[ERROR] Failed to load csf_min.json:", e)

    # Test PFCE crosswalk
    try:
        crosswalk = load_pfce_crosswalk()
        print(f"\n[OK] pfce_crosswalk_scaffold.yaml loaded. Entries: {len(crosswalk)}")
        if crosswalk:
            print("     First entry:", crosswalk[0])
    except Exception as e:
        print("\n[ERROR] Failed to load pfce_crosswalk_scaffold.yaml:", e)

    # Test PFCE definitions
    try:
        pfce_defs = load_pfce_definitions()
        print(f"\n[OK] pfce_principles.yaml loaded. Principles: {list(pfce_defs.keys())}")
    except Exception as e:
        print("\n[ERROR] Failed to load pfce_principles.yaml:", e)

    # Test constraints
    try:
        constraints = load_constraints()
        print(f"\n[OK] scenario_constraints.yaml loaded. Entries: {len(constraints)}")
    except Exception as e:
        print("\n[ERROR] Failed to load scenario_constraints.yaml:", e)

    # Test municipal dilemmas
    try:
        dilemmas = load_municipal_dilemmas()
        print(f"\n[OK] municipal_dilemmas.yaml loaded. Entries: {len(dilemmas)}")
    except Exception as e:
        print("\n[ERROR] Failed to load municipal_dilemmas.yaml:", e)
