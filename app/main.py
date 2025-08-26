import streamlit as st
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(page_title="Municipal Ethical Cyber Decision-Support Prototype", layout="wide", initial_sidebar_state="expanded")

# ---------- NIST CSF 2.0 constants ----------
NIST_FUNCTIONS = [
    "Govern (GV)",
    "Identify (ID)",
    "Protect (PR)",
    "Detect (DE)",
    "Respond (RS)",
    "Recover (RC)",
]

# ---------- Simple rule-based NLP helpers ----------
NIST_KB = {
    "ransomware": ["Govern (GV)", "Identify (ID)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"],
    "phishing":   ["Govern (GV)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"],
    "unauthorized access": ["Govern (GV)", "Detect (DE)", "Respond (RS)", "Recover (RC)", "Identify (ID)"],
    "data breach": ["Govern (GV)", "Identify (ID)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"],
    "surveillance": ["Govern (GV)", "Identify (ID)", "Protect (PR)", "Respond (RS)"],
    "ai-enabled": ["Govern (GV)", "Identify (ID)", "Detect (DE)", "Respond (RS)", "Recover (RC)"]
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
    "ai": ["Autonomy", "Explicability", "Non-maleficence"]
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

# ---------- NIST CSF 2.0 action examples ----------
NIST_ACTIONS = {
    "Govern (GV)": [
        "Affirm decision rights, RACI, and escalation paths (counsel, CIO/CISO, utilities, council)",
        "Activate risk governance: convene cross-dept incident steering group",
        "Ensure policies for privacy, surveillance use, and AI are applied/waived only with due process",
        "Require procurement/vendor transparency (SBOMs, data handling, model cards)",
        "Coordinate with oversight bodies (council, civil rights, public records) and document rationale",
        "Mandate equity impact check and document mitigations",
    ],
    "Identify (ID)": [
        "Confirm crown jewels & service criticality",
        "Establish incident objectives and scope",
        "Map stakeholders and equity impacts",
        "Inventory affected assets, data, and dependencies"
    ],
    "Protect (PR)": [
        "Harden access (MFA, least privilege, network segmentation)",
        "Freeze risky changes; ensure backups are protected/offline",
        "Apply emergency configuration baselines",
        "Safeguard sensitive data (masking, minimum necessary use)"
    ],
    "Detect (DE)": [
        "Correlate alerts; verify indicators of compromise",
        "Expand monitoring to adjacent systems",
        "Preserve logs and evidence (chain of custody)",
        "Hunt for lateral movement and persistence"
    ],
    "Respond (RS)": [
        "Contain (isolate affected hosts/segments); coordinate with counsel/LE",
        "Activate comms plan; publish clear, non-speculative updates",
        "Decide on takedown/disablement with proportionality & due process",
        "Coordinate with vendors and external partners"
    ],
    "Recover (RC)": [
        "Restore by criticality with integrity checks",
        "Post-incident review; address root causes & policy gaps",
        "Update playbooks; brief council/public with lessons learned",
        "Track residual risk and follow-up actions"
    ],
}

# ---------- Scenario summaries ----------
scenario_summaries = {
    "Baltimore Ransomware Attack": (
        "In 2019, Baltimore experienced a ransomware attack that locked staff out of critical systems. "
        "Essential services, including email and payment portals, were disrupted. "
        "City leaders faced a dilemma: whether to pay the ransom to quickly restore operations or refuse payment and risk prolonged disruption."
    ),
    "San Diego Smart Streetlights and Surveillance": (
        "San Diego deployed smart streetlights for traffic and environmental monitoring. "
        "Later, law enforcement repurposed the system for surveillance without public consent. "
        "City officials faced a dilemma: whether to continue supporting police use of the system or restrict it to its original civic purpose."
    ),
    "Riverton AI-Enabled Threat": (
        "In the fictional city of Riverton, adversarial signals disrupted an AI monitoring system at a water treatment facility, interrupting water distribution and threatening public safety. "
        "Officials faced a dilemma: whether to disable the AI system and revert to manual oversight or attempt risky live retraining to restore trust in automation."
    )
}

PRINCIPLES = ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"]

def suggest_nist(incident_type: str, description: str):
    it = incident_type.lower()
    seed = []
    for k, v in NIST_KB.items():
        if k in it or k in description.lower():
            seed.extend(v)
    if not seed:
        seed = NIST_FUNCTIONS[:]  # default to all six
    seen, ordered = set(), []
    for x in seed:
        if x not in seen:
            ordered.append(x); seen.add(x)
    return ordered

def suggest_principles(description: str):
    hits = []
    text = description.lower()
    for k, plist in ETHICAL_HINTS.items():
        if k in text:
            hits.extend(plist)
    if not hits:
        hits = PRINCIPLES[:]
    seen, ordered = set(), []
    for p in hits:
        if p not in seen:
            ordered.append(p); seen.add(p)
    return ordered

def score_tension(selected_principles, selected_nist, constraints, stakeholders, values):
    base = 10
    base += 5 * len(selected_principles)
    base += 3 * len(selected_nist)
    base += 6 * len(constraints)
    base += 3 * len(stakeholders)
    base += 4 * len(values)
    return min(base, 100)

# ---------- Sidebar ----------
st.sidebar.header("Options")
mode = st.sidebar.radio("Mode", ["Thesis scenarios", "Open-ended"])

# ---------- Intro ----------
st.title("🛡️ Municipal Ethical Cyber Decision-Support Prototype")
st.markdown("<h3 style='color:gray;'>Because what's secure isn't always what's right.</h3>", unsafe_allow_html=True)

with st.expander("About this prototype"):
    st.markdown(
        """
- **Purpose:** Support municipal cybersecurity practitioners in navigating complex ethical dilemmas.  
- **Backbone:** Draws on the NIST Cybersecurity Framework 2.0 + principlist ethical values.  
- **Context:** Designed for municipal realities: limited budgets, legacy tech, fragmented authority, and political constraints.  
        """
    )

# ---------- 1) Scenario overview ----------
scenario = st.selectbox("Choose a Municipal Cybersecurity Scenario", options=list(scenario_summaries.keys()))
st.markdown("### 1) Scenario Overview")
st.markdown(f"**Scenario Overview:** {scenario_summaries[scenario]}")

incident_type = scenario
description = scenario_summaries[scenario]
pd_defaults = dict(description="", stakeholders=[], values=[], constraints=[])

# ---------- 2) Technical Evaluation ----------
st.markdown("### 2) Technical Evaluation (NIST CSF)")
with st.expander("About the NIST CSF"):
    st.markdown("""
The **NIST Cybersecurity Framework (CSF) 2.0** provides six core functions to guide cybersecurity risk management:  
Govern, Identify, Protect, Detect, Respond, and Recover.  
In this prototype, relevant functions are highlighted to show which technical standards apply to each scenario.  
    """)

suggested_nist = suggest_nist(incident_type, description)
if mode == "Thesis scenarios":
    def chip(name: str, active: bool) -> str:
        if active:
            return f"<span style='padding:4px 10px;margin:3px;border-radius:12px;border:1px solid #0c6cf2;background:#e8f0fe;'>{name} ✓</span>"
        else:
            return f"<span style='padding:4px 10px;margin:3px;border-radius:12px;border:1px solid #ccc;background:#f7f7f7;opacity:0.7'>{name}</span>"
    chips_html = " ".join([chip(fn, fn in suggested_nist) for fn in NIST_FUNCTIONS])
    st.markdown(chips_html, unsafe_allow_html=True)
    selected_nist = suggested_nist[:]
else:
    selected_nist = st.multiselect("", NIST_FUNCTIONS, default=suggested_nist)

# ---------- 3) Ethical Evaluation ----------
st.markdown("### 3) Ethical Evaluation (Principlist Framework)")
col1, col2 = st.columns(2)
with col1:
    stakeholders = st.multiselect("Stakeholders affected", ["Residents","City Employees","Vendors","City Council","Mayor’s Office","Utilities Board","Police","Civil Rights Groups","Media","Courts"], default=pd_defaults.get("stakeholders", []))
with col2:
    values = st.multiselect("Public values at risk", ["Privacy","Transparency","Trust","Safety","Equity","Autonomy"], default=pd_defaults.get("values", []))

auto_principles = suggest_principles(description + " " + " ".join(values))
selected_principles = st.multiselect("Suggested principles", PRINCIPLES, default=auto_principles)

colp1, colp2 = st.columns(2)
with colp1:
    beneficence = st.text_area("Beneficence – promote well-being", "")
    autonomy = st.text_area("Autonomy – respect rights/choice", "")
    justice = st.text_area("Justice – fairness/equity", "")
with colp2:
    non_maleficence = st.text_area("Non-maleficence – avoid harm", "")
    explicability = st.text_area("Explicability – transparency/accountability", "")

# ---------- 4) Institutional & Governance Constraints ----------
st.markdown("### 4) Institutional & Governance Constraints")
constraints = st.multiselect("Select constraints", GOV_CONSTRAINTS, default=pd_defaults.get("constraints", []))

# ---------- 5) Ethical Tension Score ----------
st.markdown("### 5) Ethical Tension Score")
score = score_tension(selected_principles, selected_nist, constraints, stakeholders, values)
st.progress(score, text=f"Tension score: {score}/100")
