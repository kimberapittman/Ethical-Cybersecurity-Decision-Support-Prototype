import streamlit as st
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(
    page_title="Municipal Ethical Cyber Decision-Support",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Minimal styling (no extra deps) ----------
st.markdown("""
<style>
/* App title & subtitle */
.app-hero {
  padding: 14px 16px;
  border-radius: 14px;
  background: linear-gradient(135deg, #0b4ef0 0%, #7aa2ff 100%);
  color: white;
  margin-bottom: 16px;
}
.app-hero h1 {
  font-size: 1.6rem;
  margin: 0 0 4px 0;
}
.app-hero p {
  margin: 0;
  opacity: 0.95;
}

/* Section cards */
.section-card {
  border: 1px solid #e8e8ef;
  background: #fff;
  border-radius: 14px;
  padding: 16px 18px;
  margin: 10px 0 16px 0;
  box-shadow: 0 1px 0 rgba(0,0,0,0.02);
}

/* Section titles */
.section-title {
  font-weight: 700;
  font-size: 1.05rem;
  margin-bottom: 8px;
}

/* NIST chips */
.nist-chips { margin-top: 8px; }
.chip {
  display: inline-block;
  padding: 6px 12px;
  margin: 4px 6px 0 0;
  border-radius: 999px;
  border: 1px solid #d6d6e7;
  background: #f7f7fb;
  font-size: 0.92rem;
}
.chip.active {
  border-color: #0c6cf2;
  background: #e8f0fe;
  font-weight: 600;
}
.chip .tick {
  margin-left: 6px;
  font-weight: 700;
  color: #0c6cf2;
}

/* Progress label */
.small-muted {
  font-size: 0.92rem;
  color: #666;
}

/* Download code block spacing */
.block-spacer { height: 8px; }
</style>
""", unsafe_allow_html=True)

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

# ---------- Hero ----------
st.markdown("""
<div class="app-hero">
  <h1>🛡️ Municipal Ethical Cyber Decision-Support Prototype</h1>
  <p><strong>Because what's secure isn't always what's right.</strong></p>
</div>
""", unsafe_allow_html=True)

with st.expander("About this prototype"):
    st.markdown(
        """
- **Purpose:** Support municipal cybersecurity practitioners in navigating complex ethical dilemmas. The tool is designed to guide users through high-stakes decisions in real time—clarifying value conflicts, aligning actions with technical standards, and documenting justifiable outcomes under institutional and governance constraints.
- **Backbone:** The tool draws on the NIST Cybersecurity Framework 2.0—Govern, Identify, Protect, Detect, Respond, and Recover—integrated with principlist ethical values (Beneficence, Non-maleficence, Autonomy, Justice, Explicability).
- **Context:** Built for municipal realities: limited budgets, legacy systems, fragmented authority, and public accountability.
        """
    )

# ---------- 1) Scenario overview ----------
with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">1) Scenario overview</div>', unsafe_allow_html=True)

    scenario = st.selectbox(
        "Choose a Municipal Cybersecurity Scenario",
        options=list(scenario_summaries.keys())
    )
    st.markdown(f"**Scenario Overview:** {scenario_summaries[scenario]}")

    st.markdown('</div>', unsafe_allow_html=True)

# Set incident/description from scenario
incident_type = scenario
description = scenario_summaries[scenario]
pd_defaults = dict(description="", stakeholders=[], values=[], constraints=[])

# Get suggested CSF functions now (used in Section 2)
suggested_nist = suggest_nist(incident_type, description)

# ---------- 2) NIST CSF 2.0 functions ----------
with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">2) NIST CSF 2.0 functions</div>', unsafe_allow_html=True)

    with st.expander("About the NIST CSF"):
        st.markdown("""
The **NIST Cybersecurity Framework (CSF) 2.0** is a risk-based standard that helps organizations manage and reduce cybersecurity risk.  
It is organized into six core functions:

- **Govern (GV):** Establish oversight, clarify roles, responsibilities, and decision rights.  
- **Identify (ID):** Understand assets, risks, and critical services.  
- **Protect (PR):** Safeguard systems, data, and services against threats.  
- **Detect (DE):** Monitor and discover anomalous events quickly.  
- **Respond (RS):** Contain and manage active incidents.  
- **Recover (RC):** Restore capabilities, learn, and improve resilience.  

In this prototype, the CSF provides the **technical backbone**. For each scenario, relevant CSF functions are highlighted to
show which standards and practices are most applicable; your ethical reasoning then builds on this technical foundation.
        """)

    if mode == "Thesis scenarios":
        # Read‑only chips that highlight suggested functions
        def chip(name: str, active: bool) -> str:
            base = 'chip active' if active else 'chip'
            tick = "<span class='tick'>✓</span>" if active else ""
            return f"<span class='{base}'>{name}{tick}</span>"

        chips_html = " ".join([chip(fn, fn in suggested_nist) for fn in NIST_FUNCTIONS])
        st.markdown(f"<div class='nist-chips'>{chips_html}</div>", unsafe_allow_html=True)

        # lock selection to suggested set so downstream sections work unchanged
        selected_nist = suggested_nist[:]
    else:
        st.markdown("#### Suggested functions for this scenario (editable in Open‑ended mode)")
        selected_nist = st.multiselect("", NIST_FUNCTIONS, default=suggested_nist)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- 3) Ethical evaluation (Principlist) ----------
with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">3) Ethical evaluation (Principlist)</div>', unsafe_allow_html=True)

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

    colp1, colp2 = st.columns(2)
    with colp1:
        beneficence = st.text_area("Beneficence – promote well-being", "")
        autonomy = st.text_area("Autonomy – respect rights/choice", "")
        justice = st.text_area("Justice – fairness/equity", "")
    with colp2:
        non_maleficence = st.text_area("Non‑maleficence – avoid harm", "")
        explicability = st.text_area("Explicability – transparency/accountability", "")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- 4) Institutional & governance constraints ----------
with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">4) Institutional & governance constraints</div>', unsafe_allow_html=True)

    constraints = st.multiselect(
        "Select constraints relevant to this scenario",
        GOV_CONSTRAINTS,
        default=pd_defaults.get("constraints", [])
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- 5) Ethical tension score ----------
with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">5) Ethical tension score</div>', unsafe_allow_html=True)

    score = score_tension(selected_principles, selected_nist, constraints, stakeholders, values)
    st.progress(score, text=f"Ethical/contextual tension: {score}/100")
    if score < 35:
        st.success("Low tension: document rationale and proceed.")
    elif score < 70:
        st.warning("Moderate tension: ensure proportionality, comms, and oversight are in place.")
    else:
        st.error("High tension: escalate, ensure cross‑dept decision rights, consider external ethics/LE counsel.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- 6) NIST‑aligned action plan (editable) ----------
with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">6) NIST‑aligned action plan (editable)</div>', unsafe_allow_html=True)

    plan = []
    for f in selected_nist:
        st.write(f"**{f}**")
        chosen = st.multiselect(f"Select {f} actions", NIST_ACTIONS[f], default=NIST_ACTIONS[f], key=f)
        plan.extend([f"{f}: {a}" for a in chosen])

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Communication checklist ----------
with st.expander("Public communication & accountability checklist"):
    st.checkbox("Name a responsible official and decision authority for this incident", value=True)
    st.checkbox("Publish plain‑language status, impacts, and next steps (no speculation)", value=True)
    st.checkbox("State data handling, retention, and law‑enforcement coordination terms", value=True)
    st.checkbox("Record rationale for decisions (pay/no‑pay; enable/disable tech; scope of surveillance)", value=True)
    st.checkbox("Equity statement: assess & mitigate disproportionate impact by neighborhood/group", value=True)

# ---------- 7) Generate justification ----------
with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">7) Generate justification</div>', unsafe_allow_html=True)

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
        st.markdown('<div class="block-spacer"></div>', unsafe_allow_html=True)
        st.download_button("📥 Download decision record (.md)", record, file_name="decision_record.md")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Extra inputs you had in your content (kept, presented after main flow) ----------
with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Additional quick lists</div>', unsafe_allow_html=True)

    st.markdown("**Ethical Tensions (quick list)**")
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

    st.markdown("**Institutional & Governance Constraints (quick list)**")
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

    st.markdown("**NIST Cybersecurity Framework (CSF) Functions (quick list)**")
    nist_functions = st.multiselect(
        "Which NIST functions apply here?",
        ["Identify", "Protect", "Detect", "Respond", "Recover"]
    )

    st.markdown("**Principlist Ethical Framework (quick list)**")
    principles = st.multiselect(
        "Which ethical principles are most relevant?",
        ["Respect for Autonomy", "Non-Maleficence", "Beneficence", "Justice", "Explicability"]
    )

    st.markdown("**Action Plan (quick text)**")
    action_plan = st.text_area(
        "Describe your recommended path forward:",
        placeholder="Outline a response that balances ethical concerns and technical standards."
    )

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

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes – not for operational use.")
st.caption("Prototype: for thesis demonstration (Chapter IV) — aligns case presets with your Chapter III scenarios.")
