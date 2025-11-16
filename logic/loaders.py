import json
import yaml
from pathlib import Path


def load_csf_data():
    """
    Loads the trimmed CSF 2.0 JSON hierarchy.
    """
    data_path = Path(__file__).parent.parent / "data" / "csf_min.json"
    with open(data_path, "r") as f:
        return json.load(f)


def load_pfce_crosswalk():
    """
    Loads the PFCE-to-CSF crosswalk file.
    """
    data_path = Path(__file__).parent.parent / "data" / "pfce_crosswalk.yaml"
    if not data_path.exists():
        return []
    with open(data_path, "r") as f:
        return yaml.safe_load(f)


def load_constraints():
    """
    Loads institutional and governance constraints.
    """
    data_path = Path(__file__).parent.parent / "data" / "governance_constraints.yaml"
    if not data_path.exists():
        return []
    with open(data_path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    print("Testing CSF crosswalk load...")
    try:
        csf = load_csf_crosswalk()
        print("CSF entries:", len(csf))
        print("First entry:", csf[0])
    except Exception as e:
        print("CSF load failed:", e)

    print("\nTesting PFCE load...")
    try:
        pfce = load_pfce_principles()
        print("PFCE principles:", pfce)
    except Exception as e:
        print("PFCE load failed:", e)
