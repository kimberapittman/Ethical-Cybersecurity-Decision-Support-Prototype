import streamlit as st
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(page_title="Municipal Ethical Cyber Decision-Support", layout="wide")

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
scenario_summaries = {
    "Ransomware on Baltimore city servers": 
        "In 2019, Baltimore experienced a ransomware attack that locked staff out of critical systems. "
        "The city refused to pay the ransom, resulting in prolonged disruptions and $18M in recovery costs.",
    "San Diego smart streetlights and surveillance": 
        "San Diego installed smart streetlights for traffic and environmental data, but later repurposed them "
        "for police surveillance without public consent, raising ethical concerns about transparency, trust, and misuse.",
    "Hypothetical insider threat involving IT admin": 
        "An internal IT administrator is suspected of accessing confidential employee communications without a warrant. "
        "Officials must weigh internal oversight, privacy rights, and breach mitigation."
}

PRINCIPLES = ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"]

def suggest_nist(incident_type: str, description: str):
    it = incident_type.lower()
    seed = []
    for k, v in NIST_KB.items():
        if k in it or k in description.lower():
            seed.extend(v)
    if not seed:
        seed = NIST_FUNCTIONS[:]  # default to all six, in CSF 2.0 order
    # dedupe preserving order
    seen, ordered = set(), []
    for x in seed:
        if x not in seen:
            ordered.append(x); seen.add(x)
    return ordered
# Set page configuration
st.set_page_config(
    page_title="Ethical Cybersecurity Decision Prototype",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
# Title and subtitle
st.title("What’s Secure Isn’t Always What’s Right")
st.subheader("A Decision-Support Prototype for Municipal Cybersecurity Practitioners")

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
# About section
st.markdown("""
### About the Prototype
This prototype demonstrates how a decision-support tool could guide municipal cybersecurity practitioners through ethically and technically complex scenarios. It is not intended to prescribe answers but to illuminate value tensions, relevant standards, and contextual constraints using structured, real-world case reconstructions. Each scenario is drawn from thesis case studies and showcases how ethical reasoning and the NIST Cybersecurity Framework can inform decision-making in high-stakes environments.
""")

def score_tension(selected_principles, selected_nist, constraints, stakeholders, values):
    base = 10
    base += 5 * len(selected_principles)
    base += 3 * len(selected_nist)
    base += 6 * len(constraints)
    base += 3 * len(stakeholders)
    base += 4 * len(values)
    return min(base, 100)
# Select scenario
scenario = st.selectbox(
    "Choose a Municipal Cybersecurity Scenario",
    options=list(scenario_summaries.keys())
)

# ---------- Sidebar: mode, scope, presets ----------
st.sidebar.header("Mode & Presets")
mode = st.sidebar.radio("Mode", ["Quick triage (2–3 min)", "Full deliberation (8–12 min)"])
scope = st.sidebar.radio("Scope", ["Thesis scenarios only", "Open-ended"])
# Auto-display scenario summary
st.markdown(f"**Scenario Overview:** {scenario_summaries[scenario]}")

preset = st.sidebar.selectbox(
    "Load a preset (optional)",
# Ethical Tensions section
st.markdown("### Ethical Tensions")
ethical_tensions = st.multiselect(
    "Select the relevant ethical tensions present in this scenario:",
    [
        "— None —",
        "Baltimore-style: Ransomware on core city services",
        "San Diego-style: Tech repurposed for surveillance",
        "Riverton-style: AI-enabled incident on critical infra"
        "Privacy vs. Security",
        "Transparency vs. Confidentiality",
        "Autonomy vs. Oversight",
        "Public Trust vs. Operational Necessity",
        "Fairness vs. Efficiency",
        "Short-Term Action vs. Long-Term Risk"
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
st.caption("A structured tool for making ethical, justifiable decisions in municipal cybersecurity.")

with st.expander("About this prototype"):
    st.markdown(
        """
- **Purpose:** Support municipal cybersecurity practitioners in navigating complex ethical dilemmas by integrating NIST CSF 2.0 functions with principlist ethical reasoning. The tool is designed to guide users through high-stakes decisions in real time—clarifying value conflicts, aligning actions with institutional priorities, and documenting justifiable outcomes under practical constraints.
- **Backbone:** The tool draws on the NIST Cybersecurity Framework 2.0, guiding users through six core functions: Govern, Identify, Protect, Detect, Respond, and Recover. These are integrated with principlist ethical values—Beneficence, Non-maleficence, Autonomy, Justice, and Explicability—to help users weigh trade-offs and make morally defensible decisions.
- **Context:** Designed specifically for municipal use, the tool accounts for real-world constraints like limited budgets, outdated systems, fragmented authority, and opaque procurement. It supports ethical decision-making within these practical and political realities.
        """
    )

# ---------- 1) Incident Overview ----------
st.markdown("### 1) Incident overview")
colA, colB = st.columns([1.2, 2])

if preset != "— None —":
    pd = preset_data[preset]
else:
    pd = dict(incident_type="", description="", stakeholders=[], values=[], constraints=[])

THESIS_INCIDENTS = [
    "Ransomware on core city services",
    "Technology repurposing / Surveillance use",
    "AI-enabled incident on critical infrastructure",
    "Other (specify)"
]
OPEN_INCIDENTS = [
    "Ransomware",
    "Phishing / Business Email Compromise",
    "Unauthorized access",
    "Data breach",
    "Technology repurposing / Surveillance use",
    "AI-enabled incident on critical infrastructure",
    "Operational outage / ICS disruption",
    "Website defacement / DDoS",
    "Insider misuse / data exfiltration",
    "Third-party/vendor compromise",
    "Other (specify)"
]
incident_options = THESIS_INCIDENTS if scope == "Thesis scenarios only" else OPEN_INCIDENTS

with colA:
    default_option = incident_options[0]
    preset_incident = pd.get("incident_type", "")
    if preset_incident:
        lower = preset_incident.lower()
        if "ransom" in lower:
            default_option = incident_options[0] if scope == "Thesis scenarios only" else "Ransomware"
        elif "surveil" in lower:
            default_option = "Technology repurposing / Surveillance use"
        elif "ai" in lower or "water" in lower:
            default_option = "AI-enabled incident on critical infrastructure"
        else:
            default_option = "Other (specify)"
    selected_index = incident_options.index(default_option) if default_option in incident_options else 0
    incident_choice = st.selectbox("Incident type", incident_options, index=selected_index)

    if incident_choice == "Other (specify)":
        incident_type = st.text_input("Specify incident type", value=(preset_incident if default_option == "Other (specify)" else ""))
    else:
        incident_type = incident_choice

    description = st.text_area("Brief description", pd.get("description", ""), height=110)

with colB:
    st.write("")  # keep layout balance

# ---------- 2) Stakeholders, values, constraints ----------
st.markdown("### 2) Stakeholders, values, and constraints")
col1, col2, col3 = st.columns(3)
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
with col3:
    constraints = st.multiselect(
        "Institutional & governance constraints",
        GOV_CONSTRAINTS,
        default=pd.get("constraints", [])
    )

# ---------- 3) Suggested NIST CSF 2.0 functions (moved here) ----------
st.markdown("### 3) Suggested NIST CSF 2.0 functions (editable)")
suggested_nist = suggest_nist(incident_type, description)
selected_nist = st.multiselect("", NIST_FUNCTIONS, default=suggested_nist)

# ---------- 4) Ethical evaluation (Principlist) ----------
st.markdown("### 4) Ethical evaluation (Principlist)")
auto_principles = suggest_principles(description + " " + " ".join(values))
selected_principles = st.multiselect("Suggested principles (editable)", PRINCIPLES, default=auto_principles)

if mode.startswith("Quick"):
    st.info("Quick triage mode: we’ll generate short principle prompts for rapid documentation.")
    for b in quick_ethics_blurbs(selected_principles, description):
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
        ethics_summary = "\n".join(quick_ethics_blurbs(selected_principles, description))
    else:
        ethics_summary = "\n".join([
            f"Beneficence: {beneficence or '—'}",
            f"Non-maleficence: {non_maleficence or '—'}",
            f"Autonomy: {autonomy or '—'}",
            f"Justice: {justice or '—'}",
            f"Explicability: {explicability or '—'}"
        ])

    record = f"""# Municipal Cyber Decision Record
Timestamp: {timestamp}

## Incident
Type: {incident_type or '—'}
Description: {description or '—'}

## Frameworks
NIST CSF 2.0: {", ".join(selected_nist)}
Principlist: {", ".join(selected_principles)}

## Context
Stakeholders: {", ".join(stakeholders) or '—'}
Public values at risk: {", ".join(values) or '—'}
Constraints: {", ".join(constraints) or '—'}
Ethical/context tension score: {score}/100
# Institutional & Governance Constraints
st.markdown("### Institutional & Governance Constraints")
constraints = st.multiselect(
    "Which constraints affect decision-making in this case?",
    [
        "Budget limitations",
        "Legal ambiguity",
        "Time pressure",
        "Fragmented authority",
        "Public scrutiny",
        "Vendor dependence"
    ]
)

## Action plan (NIST‑aligned)
- """ + "\n- ".join(plan) + f"""
# NIST CSF Functions
st.markdown("### NIST Cybersecurity Framework (CSF) Functions")
nist_functions = st.multiselect(
    "Which NIST functions apply here?",
    ["Identify", "Protect", "Detect", "Respond", "Recover"]
)

## Ethical rationale
{ethics_summary}
# Ethical Principles
st.markdown("### Principlist Ethical Framework")
principles = st.multiselect(
    "Which ethical principles are most relevant?",
    ["Respect for Autonomy", "Non-Maleficence", "Beneficence", "Justice", "Explicability"]
)

## Notes
This decision reflects principlist ethical reasoning and NIST CSF 2.0 practices (GV/ID/PR/DE/RS/RC), applied within municipal governance constraints.
"""
    st.code(record, language="markdown")
    st.download_button("📥 Download decision record (.md)", record, file_name="decision_record.md")
# Action plan input
st.markdown("### Action Plan")
action_plan = st.text_area(
    "Describe your recommended path forward:",
    placeholder="Outline a response that balances ethical concerns and technical standards."
)

# ---------- Footer ----------
st.caption("Prototype: for thesis demonstration (Chapter IV) — aligns case presets with your Chapter III scenarios.")
# Decision rationale generator
if st.button("Generate Decision Record"):
    st.markdown("---")
    st.markdown("## 📘 Decision Summary")
    st.markdown(f"**Scenario Chosen:** {scenario}")
    st.markdown(f"**Scenario Summary:** {scenario_summaries[scenario]}")
    st.markdown(f"**Ethical Tensions Identified:** {', '.join(ethical_tensions) if ethical_tensions else 'None selected'}")
    st.markdown(f"**Constraints Present:** {', '.join(constraints) if constraints else 'None selected'}")
    st.markdown(f"**NIST Functions Referenced:** {', '.join(nist_functions) if nist_functions else 'None selected'}")
    st.markdown(f"**Ethical Principles Applied:** {', '.join(principles) if principles else 'None selected'}")
    st.markdown("**Proposed Action Plan:**")
    st.write(action_plan if action_plan else "No action plan provided.")

# Footer
st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes – not for operational use.")
