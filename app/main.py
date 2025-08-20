import streamlit as st
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(page_title="Municipal Ethical Cyber Decision-Support", layout="wide")

# ---------- Simple rule-based NLP helpers (no external deps) ----------
NIST_KB = {
    "ransomware": ["Identify", "Protect", "Detect", "Respond", "Recover"],
    "phishing":   ["Protect", "Detect", "Respond", "Recover"],
    "unauthorized access": ["Detect", "Respond", "Recover", "Identify"],
    "data breach": ["Identify", "Protect", "Detect", "Respond", "Recover"],
    "surveillance": ["Identify", "Protect", "Respond"],
    "ai-enabled": ["Identify", "Detect", "Respond", "Recover"]
}

ETHICAL_HINTS = {
    "privacy": ["Autonomy", "Justice", "Explicability"],
    "surveillance": ["Autonomy", "Justice", "Explicability", "Non-maleficence"],
    "ransom": ["Justice", "Non-maleficence", "Beneficence"],
    "water": ["Beneficence", "Non-maleficence", "Justice", "Explicability"],
    "health": ["Beneficence", "Non-maleficence", "Justice"],
    "email": ["Autonomy", "Explicability"],
    "outage": ["Non-maleficence", "Beneficence", "Explicability"],
    "protest": ["Justice", "Autonomy", "Explicability"],
    "equity": ["Justice"],
    "ai": ["Autonomy", "Explicability", "Non-maleficence"],
}

GOV_CONSTRAINTS = [
    "Fragmented authority / unclear decision rights",
    "Procurement did not disclose ethical/surveillance risk",
    "Limited budget / staffing",
    "No/weak incident playbooks or continuity plans",
    "Vendor opacity (limited audit of code/training data)",
    "Lack of public engagement / oversight",
    "Legacy tech / poor segmentation / patch backlog",
    "Ambiguous data sharing/retention policies"
]

NIST_ACTIONS = {
    "Identify": [
        "Confirm crown jewels & service criticality",
        "Establish incident objectives, decision authority, and escalation paths",
        "Map stakeholders and equity impacts"
    ],
    "Protect": [
        "Harden access (MFA, least privilege, network segmentation)",
        "Freeze risky changes; ensure backups are protected/offline",
        "Apply emergency configuration baselines"
    ],
    "Detect": [
        "Correlate alerts; verify indicators of compromise",
        "Expand monitoring to adjacent systems",
        "Preserve logs and evidence (chain of custody)"
    ],
    "Respond": [
        "Contain (isolate affected hosts/segments); coordinate with counsel/LE",
        "Activate comms plan; publish clear, non-speculative updates",
        "Decide on takedown/disablement with proportionality & due process"
    ],
    "Recover": [
        "Restore by criticality with integrity checks",
        "Post-incident review; address root causes & policy gaps",
        "Update playbooks; brief council/public with lessons learned"
    ],
}

PRINCIPLES = ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"]

def suggest_nist(incident_type:str, description:str):
    it = incident_type.lower()
    seed = []
  for k, v in NIST_KB.items():
    if k in it or k in description.lower():
        seed.extend(v)
