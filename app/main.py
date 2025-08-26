import streamlit as st
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(page_title="Municipal Ethical Cyber Decision-Support", layout="wide", initial_sidebar_state="expanded")

# ---------- NIST CSF 2.0 constants ----------
NIST_FUNCTIONS = [
    "Govern (GV)",
    "Identify (ID)",
    "Protect (PR)",
    "Detect (DE)",
    "Respond (RS)",
    "Recover (RC)",
]

# ---------- Simple rule-based NLP helpers (no external deps) ----------
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

# ---------- Scenario summaries ----------
scenario_summaries = {
    "Baltimore Ransomware Attack": (
        "In 2019, Baltimore experienced a ransomware attack that locked staff out of critical systems. "
        "The city refused to pay the ransom, resulting in prolonged disruptions and $18M in recovery costs."
    ),
    "San Diego Smart Streetlights and Surveillance": (
        "San Diego installed smart streetlights for traffic and environmental data, but later repurposed them "
        "for police surveillance without public consent, raising ethical concerns about transparency, trust, and misuse."
    ),
    "Riverton AI-Enabled Threat": (
        "In the fictional city of Riverton, adversarial signals disrupted an AI monitoring system at a water treatment facility, interrupting water distribution and threatening public safety. "
        "Officials faced a difficult choice between disabling the AI system or attempting live retraining, raising concerns about trust, continuity of service, and long-term reliability."
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
        seed = NIST_FUNCTIONS[:]
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
st.markdown(
    "<h3 style='text-align: center; color: #4C8BF5;'>Because what's secure isn't always what's right.</h3>",
    unsafe_allow_html=True
)

# ---------- 1) Scenario overview ----------
scenario = st.selectbox("Choose a Municipal Cybersecurity Scenario", options=list(scenario_summaries.keys()))
st.markdown("### 1) Scenario Overview")
st.markdown(f"**Scenario Overview:** {scenario_summaries[scenario]}")

incident_type = scenario
description = scenario_summaries[scenario]
pd_defaults = dict(description="", stakeholders=[], values=[], constraints=[])

# ---------- 2) Technical Evaluation (NIST CSF) ----------
st.markdown("### 2) Technical Evaluation (NIST CSF)")
with st.expander("About the NIST CSF"):
    st.markdown("""
The **NIST Cybersecurity Framework (CSF) 2.0** is a risk-based framework by NIST to help organizations manage 
cybersecurity risks. It has six core functions: Govern, Identify, Protect, Detect, Respond, and Recover.
This prototype uses them as the **technical backbone** so ethical reasoning is always grounded in technical standards.
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
col_sv1, col_sv2 = st.columns(2)
with col_sv1:
    stakeholders = st.multiselect("Stakeholders affected", [
        "Residents", "City Employees", "Vendors", "City Council", "Mayor’s Office",
        "Public Utilities Board", "Police Department", "Civil Rights Groups", "Media", "Courts/Recorders"
    ], default=pd_defaults.get("stakeholders", []))
with col_sv2:
    values = st.multiselect("Public values at risk", ["Privacy", "Transparency", "Trust", "Safety", "Equity", "Autonomy"],
        default=pd_defaults.get("values", []))
auto_principles = suggest_principles(description + " " + " ".join(values))
selected_principles = st.multiselect("Suggested principles (editable)", PRINCIPLES, default=auto_principles)

# ---------- 4) Institutional & governance constraints ----------
st.markdown("### 4) Institutional & governance constraints")
constraints = st.multiselect("Select constraints relevant to this scenario", GOV_CONSTRAINTS, default=pd_defaults.get("constraints", []))

# ---------- 5) Ethical tension score ----------
st.markdown("### 5) Ethical tension score")
score = score_tension(selected_principles, selected_nist, constraints, stakeholders, values)
st.progress(score, text=f"Ethical/contextual tension: {score}/100")
if score < 35:
    st.success("Low tension: document rationale and proceed.")
elif score < 70:
    st.warning("Moderate tension: ensure proportionality, comms, and oversight are in place.")
else:
    st.error("High tension: escalate, ensure cross-dept decision rights, consider external ethics/LE counsel.")

# ---------- Footer ----------
st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes – not for operational use.")
