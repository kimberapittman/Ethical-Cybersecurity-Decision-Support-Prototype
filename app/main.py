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

# ---------- Sidebar (kept only Scope; removed Mode + Presets) ----------
st.sidebar.header("Options")
scope = st.sidebar.radio("Scope", ["Thesis scenarios", "Open-ended"])

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

# ---------- 1) Scenario overview ----------
scenario = st.selectbox(
    "Choose a Municipal Cybersecurity Scenario",
    options=list(scenario_summaries.keys())
)
st.markdown(f"### 1) Scenario Overview")
st.markdown(f"**Scenario Overview:** {scenario_summaries[scenario]}")

# Derive incident and description without presets
incident_type = scenario
description = scenario_summaries[scenario]
pd_defaults = dict(description="", stakeholders=[], values=[], constraints=[])

# ---------- 2) Suggested NIST CSF 2.0 functions (editable) ----------
st.markdown("### 2) Suggested NIST CSF 2.0 functions (editable)")
suggested_nist = suggest_nist(incident_type, description)
selected_nist = st.multiselect("", NIST_FUNCTIONS, default=suggested_nist)

# ---------- 3) Ethical evaluation (Principlist) ----------
st.markdown("### 3) Ethical evaluation (Principlist)")

# Stakeholders & values (kept with ethical evaluation so values can drive suggestions)
col_sv1, col_sv2 = st.columns(2)
with col_sv1:
    stakeholders = st.multiselect(
        "Stakeholders affected",
        [
            "Residents", "City Employees", "Vendors", "City Council", "Mayor’s Office",
            "Public Utilities Board", "Police Department", "Civil Rights Groups", "Media", "Courts/Recorders"
        ],
        default=pd_defaults.get("stakeholders", [])
    )
with col_sv2:
    values = st.multiselect(
        "Public values at risk",
        ["Privacy", "Transparency", "Trust", "Safety", "Equity", "Autonomy"],
        default=pd_defaults.get("values", [])
    )

auto_principles = suggest_principles(description + " " + " ".join(values))
selected_principles = st.multiselect("Suggested principles (editable)", PRINCIPLES, default=auto_principles)

# Full deliberation inputs
colp1, colp2 = st.columns(2)
with colp1:
    beneficence = st.text_area("Beneficence – promote well-being", "")
    autonomy = st.text_area("Autonomy – respect rights/choice", "")
    justice = st.text_area("Justice – fairness/equity", "")
with colp2:
    non_maleficence = st.text_area("Non‑maleficence – avoid harm", "")
    explicability = st.text_area("Explicability – transparency/accountability", "")

# ---------- 4) Institutional & governance constraints ----------
st.markdown("### 4) Institutional & governance constraints")
constraints = st.multiselect(
    "Select constraints relevant to this scenario",
    GOV_CONSTRAINTS,
    default=pd_defaults.get("constraints", [])
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

## Action plan (NIST‑aligned)
- """ + "\n- ".join(plan) + f"""

## Ethical rationale
{ethics_summary}

## Notes
This decision reflects principlist ethical reasoning and NIST CSF 2.0 practices (GV/ID/PR/DE/RS/RC), applied within municipal governance constraints.
"""
    st.code(record, language="markdown")
    st.download_button("📥 Download decision record (.md)", record, file_name="decision_record.md")

# ---------- Extra inputs you had in your content (kept, presented after main flow) ----------
st.markdown("### Ethical Tensions (quick list)")
ethical_tensions = st.multiselect(
    "Select the relevant ethical tensions present in this scenario:",
    [
        "Privacy vs. Security",
        "Transparency vs. Confidentiality",
        "Autonomy vs. Oversight",
        "Public Trust vs. Operational Necessity",
        "Fairness vs. Efficiency",
        "Short-Term Action vs. Long-Term Risk"
    ]
)

st.markdown("### Institutional & Governance Constraints (quick list)")
constraints_quick = st.multiselect(
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

st.markdown("### NIST Cybersecurity Framework (CSF) Functions (quick list)")
nist_functions = st.multiselect(
    "Which NIST functions apply here?",
    ["Identify", "Protect", "Detect", "Respond", "Recover"]
)

st.markdown("### Principlist Ethical Framework (quick list)")
principles = st.multiselect(
    "Which ethical principles are most relevant?",
    ["Respect for Autonomy", "Non-Maleficence", "Beneficence", "Justice", "Explicability"]
)

st.markdown("### Action Plan (quick text)")
action_plan = st.text_area(
    "Describe your recommended path forward:",
    placeholder="Outline a response that balances ethical concerns and technical standards."
)

# A second summary button you had at the bottom (kept intact)
if st.button("Generate Decision Record"):
    st.markdown("---")
    st.markdown("## 📘 Decision Summary")
    st.markdown(f"**Scenario Chosen:** {scenario}")
    st.markdown(f"**Scenario Summary:** {scenario_summaries[scenario]}")
    st.markdown(f"**Ethical Tensions Identified:** {', '.join(ethical_tensions) if ethical_tensions else 'None selected'}")
    st.markdown(f"**Constraints Present:** {', '.join(constraints_quick) if constraints_quick else 'None selected'}")
    st.markdown(f"**NIST Functions Referenced:** {', '.join(nist_functions) if nist_functions else 'None selected'}")
    st.markdown(f"**Ethical Principles Applied:** {', '.join(principles) if principles else 'None selected'}")
    st.markdown("**Proposed Action Plan:**")
    st.write(action_plan if action_plan else "No action plan provided.")

# ---------- Footer ----------
st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes – not for operational use.")
st.caption("Prototype: for thesis demonstration (Chapter IV) — aligns case presets with your Chapter III scenarios.")

st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes – not for operational use.")
