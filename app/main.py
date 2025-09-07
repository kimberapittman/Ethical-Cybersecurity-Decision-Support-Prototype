import streamlit as st
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(page_title="Municipal Ethical Cyber Decision-Support", layout="wide", initial_sidebar_state="expanded")

# ---------- NIST CSF 2.0 constants ----------
NIST_FUNCTIONS = [
    "Identify (ID)",
    "Protect (PR)",
    "Detect (DE)",
    "Respond (RS)",
    "Recover (RC)",
]

# ---------- Simple rule-based NLP helpers (no external deps) ----------
NIST_KB = {
    "ransomware": ["Identify (ID)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"],
    "phishing":   ["Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"],
    "unauthorized access": ["Detect (DE)", "Respond (RS)", "Recover (RC)", "Identify (ID)"],
    "data breach": ["Identify (ID)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"],
    "surveillance": ["Identify (ID)", "Protect (PR)", "Respond (RS)"],
    "ai-enabled": ["Identify (ID)", "Detect (DE)", "Respond (RS)", "Recover (RC)"]
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
    "Identify (ID)": [
        "Confirm critical assets and services",
        "Establish incident objectives and scope",
        "Map stakeholders and equity impacts",
        "Inventory affected assets, data, and dependencies"
    ],
    "Protect (PR)": [
        "Harden access (MFA, least privilege, segmentation)",
        "Freeze risky changes; ensure backups are protected/offline",
        "Apply emergency configuration baselines",
        "Safeguard sensitive data"
    ],
    "Detect (DE)": [
        "Correlate alerts; verify indicators of compromise",
        "Expand monitoring to adjacent systems",
        "Preserve logs and evidence",
        "Hunt for lateral movement and persistence"
    ],
    "Respond (RS)": [
        "Contain affected hosts/segments; coordinate with counsel/LE",
        "Activate comms plan; publish clear updates",
        "Decide on takedown/disablement with proportionality",
        "Coordinate with vendors and partners"
    ],
    "Recover (RC)": [
        "Restore by criticality with integrity checks",
        "Conduct post-incident review and address root causes",
        "Update playbooks; brief council/public with lessons learned",
        "Track residual risk and follow-up actions"
    ],
}

# ---------- Scenario summaries ----------
scenario_summaries = {
    "Baltimore Ransomware Attack": (
        "In 2019, Baltimore’s municipal systems were crippled by a ransomware attack that locked staff out of essential services. "
        "Cybersecurity practitioners had to guide the city’s response under pressure, weighing whether to recommend paying the ransom or pursuing recovery, each carrying severe consequences."
    ),
    "San Diego Smart Streetlights and Surveillance": (
        "San Diego deployed smart streetlights to collect traffic and environmental data, but the system was later repurposed for police surveillance without public consent. "
        "Cybersecurity practitioners faced ethical trade-offs around enabling law enforcement access versus safeguarding transparency, privacy, and community trust."
    ),
    "Riverton AI-Enabled Threat": (
        "In the fictional city of Riverton, adversarial signals disrupted an AI-based monitoring system at a water treatment facility, threatening public safety. "
        "Cybersecurity practitioners had to decide whether to disable the AI system or attempt risky live retraining, balancing technical reliability, continuity of service, and public trust."
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

# ---------- Ethical tensions mapped to Principlist (NEW) ----------
ETHICAL_TENSIONS_BY_SCENARIO = {
    "Baltimore Ransomware Attack": [
        ("Pay ransom vs. refuse to pay",
         "Restoring services quickly versus avoiding rewarding criminal behavior.",
         ["Beneficence", "Justice", "Non-maleficence"]),
        ("Transparency vs. operational confidentiality",
         "Clear public comms versus withholding sensitive details that could worsen harm.",
         ["Explicability", "Non-maleficence"]),
        ("Speed of restoration vs. integrity/forensics",
         "Rapid service return versus thorough integrity checks and evidence preservation.",
         ["Beneficence", "Explicability", "Non-maleficence"])
    ],
    "San Diego Smart Streetlights and Surveillance": [
        ("Public safety investigations vs. privacy",
         "Using sensor data for investigations versus limiting secondary use without consent.",
         ["Beneficence", "Autonomy", "Justice"]),
        ("Expediency vs. democratic oversight",
         "Operational efficiency versus robust public process and accountable governance.",
         ["Justice", "Explicability", "Autonomy"]),
        ("Data retention/repurposing vs. minimization",
         "Retaining/repurposing data for broader uses versus collecting the minimum necessary.",
         ["Non-maleficence", "Autonomy", "Explicability"])
    ],
    "Riverton AI-Enabled Threat": [
        ("Automated stabilization vs. human control",
         "Fast AI-driven control versus explainable, human-led decisions.",
         ["Beneficence", "Autonomy", "Explicability"]),
        ("Hot-fix now vs. rigorous retraining",
         "Immediate mitigation versus building long-term reliability and assurance.",
         ["Non-maleficence", "Beneficence", "Explicability"]),
        ("Vendor opacity vs. public accountability",
         "Proprietary constraints versus documentation and transparent review.",
         ["Explicability", "Justice"])
    ],
}

# ---------- Sidebar ----------
st.sidebar.header("Options")
mode = st.sidebar.radio("Mode", ["Thesis scenarios", "Open-ended"])

# ---------- Intro ----------
st.markdown(
    """
    <div style='text-align: center;'>
        <h1>🛡️ Municipal Ethical Cyber Decision-Support Prototype</h1>
        <h4 style='color:#4C8BF5;'>Because what's secure isn't always what's right.</h4>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("About this prototype"):
    st.markdown(
        """
- **Purpose:** Support municipal cybersecurity practitioners in navigating complex ethical dilemmas. This tool is designed to guide users through high-stakes decisions in real time - aligning actions with technical standards, clarifying value conflicts, and documenting justifiable outcomes under institutional and governance constraints.  
- **Backbone:** This prototype draws on the NIST Cybersecurity Framework functions (ID/PR/DE/RS/RC) integrated with Principlist ethical values—Beneficence, Non-maleficence, Autonomy, Justice, and Explicability—so practitioners can weigh trade-offs and make defensible decisions.  
- **Context:** Built for municipal realities: limited budgets, fragmented authority, vendor opacity, and high public accountability. 
        """
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
The **NIST Cybersecurity Framework (CSF) 2.0** provides the technical backbone for this prototype.
We focus on five operational functions:

- **Identify (ID):** Understand assets, risks, and critical services.  
- **Protect (PR):** Safeguard systems, data, and services against threats.  
- **Detect (DE):** Monitor and discover anomalous events quickly.  
- **Respond (RS):** Contain and manage active incidents and communications.  
- **Recover (RC):** Restore capabilities and improve resilience post-incident.  
    """)

# Suggested functions
suggested_nist = suggest_nist(incident_type, description)

# Per-scenario “how it applies” notes
def scenario_csfs_explanations(incident_text: str) -> dict:
    t = incident_text.lower()
    notes = {
        "Identify (ID)": "Confirm critical services, impacted assets, and risk to residents for this scenario.",
        "Protect (PR)": "Harden access, backups, and sensitive data paths most relevant here.",
        "Detect (DE)": "Tighten monitoring for IOCs and adjacent systems implicated in this scenario.",
        "Respond (RS)": "Contain, coordinate comms/counsel, and execute proportional response steps.",
        "Recover (RC)": "Restore by criticality, verify integrity, and capture lessons learned."
    }
    if "ransom" in t:
        notes["Protect (PR)"] = "Ensure offline/immutable backups; least-privilege clean-up to prevent re-encryption."
        notes["Respond (RS)"] = "Isolate infected hosts, evaluate ransom stance, coordinate comms and legal."
        notes["Recover (RC)"] = "Prioritize restoration of city services; validate from clean backups."
    if "surveillance" in t or "streetlight" in t:
        notes["Identify (ID)"] = "Map data types, retention, and groups most affected by repurposing."
        notes["Protect (PR)"] = "Enforce access controls and data minimization for sensitive footage/metadata."
        notes["Respond (RS)"] = "Adjust usage, pause feeds if needed, and publish transparent updates."
    if "ai" in t or "water" in t:
        notes["Identify (ID)"] = "Assess critical dependencies and AI decision points in the water system."
        notes["Detect (DE)"] = "Watch for model drift/adversarial behavior; expand telemetry at interfaces."
        notes["Respond (RS)"] = "Decide on disable vs. retrain; ensure safety-first rollback options."
        notes["Recover (RC)"] = "Validate safe operations before full return; document model/controls changes."
    return notes

scenario_tips = scenario_csfs_explanations(description)

# ---- Scenario-specific technical highlights (list; replaces 6 accordions)
st.markdown("#### Scenario-specific technical highlights")
if mode == "Thesis scenarios":
    selected_nist = suggested_nist[:]
    for fn in NIST_FUNCTIONS:
        mark = "✓ " if fn in suggested_nist else ""
        tip = scenario_tips.get(fn, "—")
        st.markdown(f"- **{fn}** {mark} — {tip}")
else:
    selected_nist = []
    cols_fn = st.columns(3)
    for i, fn in enumerate(NIST_FUNCTIONS):
        with cols_fn[i % 3]:
            checked = st.checkbox(fn, value=(fn in suggested_nist), key=f"fn_{fn}")
            if checked:
                selected_nist.append(fn)
            st.caption(scenario_tips.get(fn, "—"))

# ---------- 3) Ethical Evaluation (Principlist) ----------
st.markdown("### 3) Ethical Evaluation (Principlist)")
with st.expander("About the Principlist Framework"):
    st.markdown("""
The **Principlist Framework** balances:  
**Beneficence** (promote well-being), **Non-maleficence** (avoid harm),  
**Autonomy** (respect rights/choice), **Justice** (fairness/equity), and  
**Explicability** (transparency/accountability).
    """)

# --- Ethical tensions in this scenario (now with Principlist tags)
st.markdown("#### Ethical tensions in this scenario")
tensions = ETHICAL_TENSIONS_BY_SCENARIO.get(scenario, [])
if tensions:
    for label, expl, tags in tensions:
        tag_badges = " ".join([f"<span style='display:inline-block;margin:0 4px 4px 0;padding:2px 8px;border-radius:12px;border:1px solid #4C8BF5;color:#1E3A8A;background:#EAF2FF;font-size:0.8rem'>{t}</span>" for t in tags])
        st.markdown(f"- **{label}** — {expl}<br/>{tag_badges}", unsafe_allow_html=True)
else:
    st.info("No predefined tensions for this scenario.")

# Auto-suggested principles (kept internal for scoring; chips removed per your request)
auto_principles = suggest_principles(description)
selected_principles = auto_principles[:] if mode == "Thesis scenarios" else st.multiselect("", PRINCIPLES, default=auto_principles, label_visibility="collapsed")

# ---------- 3a) NIST × Principlist Matrix ----------
st.markdown("### 3a) NIST × Principlist Matrix")
with st.expander("What is this matrix?"):
    st.markdown("""
This matrix integrates **technical** (NIST CSF) and **ethical** (Principlist) reasoning.  
- **Rows = NIST functions (ID/PR/DE/RS/RC)**  
- **Columns = Principlist principles**  
- **Cells = relevance** of a principle to a function in this case.
    """)

use_weights = st.toggle("Use 0–5 weighting instead of checkboxes", value=False, key="mx_use_weights")

PREHIGHLIGHT = {
    "Baltimore Ransomware Attack": [
        ("Respond (RS)", "Justice"),
        ("Protect (PR)", "Non-maleficence"),
        ("Recover (RC)", "Beneficence"),
        ("Identify (ID)", "Justice"),
    ],
    "San Diego Smart Streetlights and Surveillance": [
        ("Identify (ID)", "Autonomy"),
        ("Protect (PR)", "Non-maleficence"),
        ("Respond (RS)", "Justice"),
    ],
    "Riverton AI-Enabled Threat": [
        ("Detect (DE)", "Non-maleficence"),
        ("Respond (RS)", "Beneficence"),
        ("Respond (RS)", "Explicability"),
        ("Identify (ID)", "Beneficence"),
        ("Recover (RC)", "Justice"),
    ],
}

st.write("")
cols = st.columns([1.1] + [1]*len(PRINCIPLES))
with cols[0]:
    st.markdown("**Function \\ Principle**")
for i, p in enumerate(PRINCIPLES, start=1):
    with cols[i]:
        st.markdown(f"**{p}**")

matrix_state = {}
pre = set(PREHIGHLIGHT.get(scenario, []))
for fn in NIST_FUNCTIONS:
    row_cols = st.columns([1.1] + [1]*len(PRINCIPLES))
    with row_cols[0]:
        st.markdown(f"**{fn}**")
    for j, p in enumerate(PRINCIPLES, start=1):
        key = f"mx_{fn}_{p}"
        default_marked = (fn, p) in pre if mode == "Thesis scenarios" else False
        with row_cols[j]:
            if use_weights:
                default_val = 3 if default_marked else 0
                val = st.slider(" ", 0, 5, value=default_val, key=key, label_visibility="collapsed")
                matrix_state[(fn, p)] = val
            else:
                mark = st.checkbox(" ", value=default_marked, key=key, label_visibility="collapsed")
                matrix_state[(fn, p)] = 1 if mark else 0

st.markdown("##### Matrix summary")
fn_totals = {fn: sum(matrix_state[(fn, p)] for p in PRINCIPLES) for fn in NIST_FUNCTIONS}
pr_totals = {p: sum(matrix_state[(fn, p)] for fn in NIST_FUNCTIONS) for p in PRINCIPLES}
colA, colB = st.columns(2)
with colA:
    st.markdown("**Totals by NIST function**")
    for fn in NIST_FUNCTIONS:
        denom = (5*len(PRINCIPLES) if use_weights else len(PRINCIPLES))
        st.progress(min(int((fn_totals[fn] / denom) * 100), 100), text=f"{fn}: {fn_totals[fn]}")
with colB:
    st.markdown("**Totals by Ethical principle**")
    for p in PRINCIPLES:
        denom = (5*len(NIST_FUNCTIONS) if use_weights else len(NIST_FUNCTIONS))
        st.progress(min(int((pr_totals[p] / denom) * 100), 100), text=f"{p}: {pr_totals[p]}")

st.session_state["nist_principle_matrix"] = matrix_state
st.session_state["nist_totals_by_function"] = fn_totals
st.session_state["principle_totals"] = pr_totals

# ---------- 4) Institutional & Governance Constraints ----------
st.markdown("### 4) Institutional & Governance Constraints")
constraints = st.multiselect("Select constraints relevant to this scenario", GOV_CONSTRAINTS, default=pd_defaults.get("constraints", []))

# ---------- 5) Ethical Tension Score ----------
st.markdown("### 5) Ethical Tension Score")
if 'stakeholders' not in locals(): stakeholders = []
if 'values' not in locals(): values = []
selected_principles_for_score = list({*selected_principles}) if isinstance(selected_principles, list) else auto_principles
score = score_tension(selected_principles_for_score, selected_nist, constraints, stakeholders, values)
st.progress(score, text=f"Ethical/contextual tension: {score}/100")
if score < 35:
    st.success("Low tension: document rationale and proceed.")
elif score < 70:
    st.warning("Moderate tension: ensure proportionality and oversight.")
else:
    st.error("High tension: escalate and seek external counsel.")

# ---------- Footer ----------
st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes – not for operational use.")
