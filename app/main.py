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
# Include GV (governance) as an overarching function for most incidents
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

# ---------- NIST CSF 2.0 action examples (now includes GOVERN) ----------
NIST_ACTIONS = {
    "Govern (GV)": [
        "Affirm decision rights, RACI, and escalation paths (counsel, CIO/CISO, utilities, council)",
        "Activate risk governance: convene cross‑dept incident steering group",
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

# ---------- Prioritization helpers for NIST (new) ----------
FUNCTION_EXPLANATIONS = {
    "Govern (GV)": "Clarify decision rights, policies, and public accountability for this scenario.",
    "Identify (ID)": "Confirm critical services, assets, and dependencies implicated here.",
    "Protect (PR)": "Harden access, safeguard data, and freeze risky changes relevant to this case.",
    "Detect (DE)": "Monitor for anomalies and confirm indicators tied to this scenario.",
    "Respond (RS)": "Contain the impact and coordinate communications and mitigation.",
    "Recover (RC)": "Restore services by criticality and capture lessons learned."
}

KEYWORD_TO_FUNCTIONS = [
    (["ransom", "encrypt", "extortion"], ["Govern (GV)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"]),
    (["phish", "email", "bec"], ["Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"]),
    (["surveil", "streetlight", "sensor", "repurpose"], ["Govern (GV)", "Identify (ID)", "Protect (PR)", "Respond (RS)"]),
    (["ai", "model", "ml", "automation"], ["Govern (GV)", "Detect (DE)", "Respond (RS)", "Recover (RC)", "Identify (ID)"]),
    (["water", "scada", "ics", "utility"], ["Identify (ID)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)", "Govern (GV)"]),
    (["breach", "exfil", "leak"], ["Identify (ID)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"]),
]

def prioritize_functions(text: str):
    t = (text or "").lower()
    ordered, seen = [], set()
    for keys, funcs in KEYWORD_TO_FUNCTIONS:
        if any(k in t for k in keys):
            for f in funcs:
                if f not in seen:
                    ordered.append(f); seen.add(f)
    for f in NIST_FUNCTIONS:
        if f not in seen:
            ordered.append(f); seen.add(f)
    return ordered

def suggest_nist(incident_type: str, description: str):
    it = (incident_type or "").lower()
    seed = []
    for k, v in NIST_KB.items():
        if k in it or k in (description or "").lower():
            seed.extend(v)
    if not seed:
        seed = NIST_FUNCTIONS[:]  # default to all six, in CSF 2.0 order
    seen, ordered = set(), []
    for x in seed:
        if x not in seen:
            ordered.append(x); seen.add(x)
    return ordered

def suggest_principles(description: str):
    hits = []
    text = (description or "").lower()
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

def quick_ethics_blurbs(principles, ctx):
    blurbs = []
    for p in PRINCIPLES:
        if p in principles:
            if p == "Beneficence":
                blurbs.append("Beneficence: Prioritize restoring essential services and public well-being.")
            if p == "Non-maleficence":
                blurbs.append("Non-maleficence: Avoid foreseeable harms from containment, disclosure, or automation side-effects.")
            if p == "Autonomy":
                blurbs.append("Autonomy: Respect rights, choice, and due process—minimize unnecessary surveillance or coercive measures.")
            if p == "Justice":
                blurbs.append("Justice: Distribute burdens/benefits fairly; prevent disproportionate impact on specific neighborhoods or groups.")
            if p == "Explicability":
                blurbs.append("Explicability: Communicate decisions and rationales clearly, with auditable records.")
    return blurbs

def score_tension(selected_principles, selected_nist, constraints, stakeholders, values):
    base = 10
    base += 5 * len(selected_principles)
    base += 3 * len(selected_nist)
    base += 6 * len(constraints)
    base += 3 * len(stakeholders)
    base += 4 * len(values)
    return min(base, 100)

# ---------- Sidebar: mode & scope (unchanged content) ----------
st.sidebar.header("Mode & Presets")
mode = st.sidebar.radio("Mode", ["Quick triage (2–3 min)", "Full deliberation (8–12 min)"])
scope = st.sidebar.radio("Scope", ["Thesis scenarios only", "Open-ended"])
preset = st.sidebar.selectbox(
    "Load a preset (optional)",
    [
        "— None —",
        "Baltimore-style: Ransomware on core city services",
        "San Diego-style: Tech repurposed for surveillance",
        "Riverton-style: AI-enabled incident on critical infra"
    ]
)

preset_data = {
    "Baltimore-style: Ransomware on core city services": dict(
        incident_type="Ransomware",
        description="City servers encrypted; email and payment portals offline; pressure to pay ransom vs. restore from backups.",
        stakeholders=["Residents", "City Employees", "City Council", "Courts/Recorders"],
        values=["Safety", "Trust", "Transparency", "Equity", "Autonomy"],
        constraints=[
            "Legacy tech / poor segmentation / patch backlog",
            "Limited budget / staffing",
            "No/weak incident playbooks or continuity plans"
        ]
    ),
    "San Diego-style: Tech repurposed for surveillance": dict(
        incident_type="Technology repurposing / Surveillance use",
        description="Sensor-enabled streetlights used by police for investigations without prior public process; policy and equity concerns.",
        stakeholders=["Residents", "City Council", "Media", "Civil Rights Groups"],
        values=["Privacy", "Transparency", "Trust", "Equity", "Autonomy"],
        constraints=[
            "Procurement did not disclose ethical/surveillance risk",
            "Lack of public engagement / oversight",
            "Ambiguous data sharing/retention policies",
            "Fragmented authority / unclear decision rights"
        ]
    ),
    "Riverton-style: AI-enabled incident on critical infra": dict(
        incident_type="AI-enabled intrusion on water treatment network",
        description="AI monitor auto-acted on adversarial signal, disrupting water distribution; choice between disabling AI or retraining live.",
        stakeholders=["Residents", "Public Utilities Board", "Vendors", "Mayor’s Office"],
        values=["Safety", "Trust", "Transparency", "Equity", "Autonomy"],
        constraints=[
            "Vendor opacity (limited audit of code/training data)",
            "Fragmented authority / unclear decision rights",
            "No/weak incident playbooks or continuity plans"
        ]
    )
}

# ---------- Intro ----------
st.title("🛡️ Municipal Ethical Cyber Decision-Support (Prototype)")
st.markdown("**Because what's secure isn't always what's right.**")

with st.expander("About this prototype"):
    st.markdown(
        """
- **Purpose:** Support municipal cybersecurity practitioners in navigating complex ethical dilemmas. The tool is designed to guide users through high-stakes decisions in real time—clarifying value conflicts, aligning actions with institutional priorities, and documenting justifiable outcomes under practical constraints.
- **Backbone:** The tool draws on the NIST Cybersecurity Framework 2.0, guiding users through six core functions: Govern, Identify, Protect, Detect, Respond, and Recover. These are integrated with principlist ethical values—Beneficence, Non-maleficence, Autonomy, Justice, and Explicability—to help users weigh trade-offs and make morally defensible decisions.
- **Context:** Designed specifically for municipal use, the tool accounts for real-world constraints like limited budgets, outdated systems, fragmented authority, and opaque procurement. It supports ethical decision-making within these practical and political realities.
        """
    )

# =======================================================================
# 1) SCENARIO OVERVIEW
# =======================================================================
scenario = st.selectbox(
    "1) Choose a Municipal Cybersecurity Scenario",
    options=list(scenario_summaries.keys())
)
st.markdown(f"**Scenario Overview:** {scenario_summaries[scenario]}")

# Prepare preset data
if preset != "— None —":
    pd = preset_data[preset]
else:
    pd = dict(incident_type="", description="", stakeholders=[], values=[], constraints=[])

# Use scenario text as the context/description for downstream suggestions
context_text = scenario_summaries[scenario]

# =======================================================================
# 2) NIST CSF 2.0 FUNCTIONS (prioritized + editable)
# =======================================================================
st.markdown("### 2) NIST CSF 2.0 functions for this scenario")

# Prioritize based on scenario text (still shows all six; preselects top)
prioritized = prioritize_functions(context_text)
default_selection = prioritized[:4] if len(prioritized) >= 4 else prioritized

selected_nist = st.multiselect(
    "Technical functions most implicated right now (edit as needed):",
    NIST_FUNCTIONS,
    default=default_selection
)

# One-line explanations for all functions (selected vs. unselected bullets)
with st.container():
    for f in NIST_FUNCTIONS:
        bullet = "•" if f in selected_nist else "◦"
        why = FUNCTION_EXPLANATIONS.get(f, "")
        st.markdown(f"{bullet} **{f}** — {why}")

# =======================================================================
# 3) ETHICAL EVALUATION (Principlist) + Stakeholders & Values
# =======================================================================
st.markdown("### 3) Ethical evaluation (Principlist)")

# Place stakeholders & values here since they inform the ethics step
col1, col2 = st.columns(2)
with col1:
    stakeholders = st.multiselect(
        "Stakeholders affected",
        [
            "Residents", "City Employees", "Vendors", "City Council", "Mayor’s Office",
            "Public Utilities Board", "Police Department", "Civil Rights Groups", "Media", "Courts/Recorders"
        ],
        default=pd.get("stakeholders", [])
    )
with col2:
    values = st.multiselect(
        "Public values at risk",
        ["Privacy", "Transparency", "Trust", "Safety", "Equity", "Autonomy"],
        default=pd.get("values", [])
    )

auto_principles = suggest_principles(context_text + " " + " ".join(values))
selected_principles = st.multiselect("Suggested principles (editable)", PRINCIPLES, default=auto_principles)

if mode.startswith("Quick"):
    st.info("Quick triage mode: we’ll generate short principle prompts for rapid documentation.")
    for b in quick_ethics_blurbs(selected_principles, context_text):
        st.write("• " + b)
else:
    colp1, colp2 = st.columns(2)
    with colp1:
        beneficence = st.text_area("Beneficence – promote well-being", "")
        autonomy = st.text_area("Autonomy – respect rights/choice", "")
        justice = st.text_area("Justice – fairness/equity", "")
    with colp2:
        non_maleficence = st.text_area("Non‑maleficence – avoid harm", "")
        explicability = st.text_area("Explicability – transparency/accountability", "")

# =======================================================================
# 4) INSTITUTIONAL & GOVERNANCE CONSTRAINTS
# =======================================================================
st.markdown("### 4) Institutional & governance constraints")
constraints = st.multiselect(
    "Which constraints affect decision-making in this case?",
    GOV_CONSTRAINTS,
    default=pd.get("constraints", [])
)

# ---------- 5) Ethical tension score ----------
st.markdown("### 5) Ethical tension score")
score = score_tension(selected_principles, selected_nist, constraints, stakeholders, values)
st.progress(score, text=f"Ethical/contextual tension: {score}/100")

if score < 35:
    st.success("Low tension: document rationale and proceed.")
elif score < 70:
    st.warning("Moderate tension: ensure proportionality, comms, and oversight are in place.")
else:
    st.error("High tension: escalate, ensure cross‑dept decision rights, consider external ethics/LE counsel.")

# ---------- 6) NIST‑aligned action plan (editable) ----------
st.markdown("### 6) NIST‑aligned action plan (editable)")
plan = []
for f in selected_nist:
    st.write(f"**{f}**")
    chosen = st.multiselect(f"Select {f} actions", NIST_ACTIONS[f], default=NIST_ACTIONS[f], key=f)
    plan.extend([f"{f}: {a}" for a in chosen])

# ---------- Communication checklist ----------
with st.expander("Public communication & accountability checklist"):
    st.checkbox("Name a responsible official and decision authority for this incident", value=True)
    st.checkbox("Publish plain‑language status, impacts, and next steps (no speculation)", value=True)
    st.checkbox("State data handling, retention, and law‑enforcement coordination terms", value=True)
    st.checkbox("Record rationale for decisions (pay/no‑pay; enable/disable tech; scope of surveillance)", value=True)
    st.checkbox("Equity statement: assess & mitigate disproportionate impact by neighborhood/group", value=True)

# ---------- 7) Generate justification ----------
st.markdown("### 7) Generate justification")
if st.button("Create decision record"):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    if mode.startswith("Quick"):
        ethics_summary = "\n".join(quick_ethics_blurbs(selected_principles, context_text))
    else:
        ethics_summary = "\n".join([
            f"Beneficence: {locals().get('beneficence', '') or '—'}",
            f"Non-maleficence: {locals().get('non_maleficence', '') or '—'}",
            f"Autonomy: {locals().get('autonomy', '') or '—'}",
            f"Justice: {locals().get('justice', '') or '—'}",
            f"Explicability: {locals().get('explicability', '') or '—'}"
        ])

    record = f"""# Municipal Cyber Decision Record
Timestamp: {timestamp}

## Incident
Scenario: {scenario}
Summary: {scenario_summaries[scenario]}

## Frameworks
NIST CSF 2.0: {", ".join(selected_nist)}
Principlist: {", ".join(selected_principles)}

## Context
Stakeholders: {", ".join(stakeholders) or '—'}
Public values at risk: {", ".join(values) or '—'}
Constraints: {", ".join(constraints) or '—'}
Ethical/context tension score: {score}/100

## Action plan (NIST‑aligned)
- """ + "\n- ".join(plan) + f"""

## Ethical rationale
{ethics_summary}

## Notes
This decision reflects principlist ethical reasoning and NIST CSF 2.0 practices (GV/ID/PR/DE/RS/RC), applied within municipal governance constraints.
"""
    st.code(record, language="markdown")
    st.download_button("📥 Download decision record (.md)", record, file_name="decision_record.md")

# ---------- Footer ----------
st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes – not for operational use.")
st.caption("Prototype: for thesis demonstration (Chapter IV) — aligns case presets with your Chapter III scenarios.")
