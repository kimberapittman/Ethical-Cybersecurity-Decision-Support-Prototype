import streamlit as st
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(page_title="Municipal Ethical Cyber Decision-Support", layout="wide", initial_sidebar_state="expanded")

# ---------- Minimal styling for list emphasis & readability (NEW, cosmetic only) ----------
st.markdown("""
<style>
.listbox{background:#f9fbff;border-left:4px solid #4C8BF5;padding:10px 14px;border-radius:8px;margin:6px 0 14px;}
.section-note{color:#6b7280;font-size:0.9rem;margin:-4px 0 10px 0;}
.tight-list{margin:0.25rem 0 0 1.15rem;padding:0;}
.tight-list li{margin:6px 0;}
.sub{color:#6b7280;font-size:0.95rem;}
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
        "Affirm decision rights, RACI, and escalation paths",
        "Activate risk governance: convene cross-dept incident steering group",
        "Ensure policies for privacy, surveillance use, and AI are applied only with due process",
        "Require procurement/vendor transparency (SBOMs, data handling, model cards)",
        "Coordinate with oversight bodies and document rationale",
        "Mandate equity impact check and mitigations",
    ],
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

# ---------- ETHICAL TENSIONS mapped to Principlist ----------
ETHICAL_TENSIONS_BY_SCENARIO = {
    "Baltimore Ransomware Attack": [
        ("Paying ransom vs. refusing payment (service restoration speed vs. long-term harm/precedent)", ["Justice", "Non-maleficence", "Beneficence"]),
        ("Public transparency vs. operational confidentiality during recovery", ["Explicability", "Non-maleficence"]),
        ("Prioritizing restoration by critical services vs. equal treatment across departments", ["Justice", "Beneficence"]),
    ],
    "San Diego Smart Streetlights and Surveillance": [
        ("Secondary use of data for policing vs. original civic purpose", ["Autonomy", "Justice", "Explicability"]),
        ("Privacy protections vs. public safety claims for surveillance expansion", ["Non-maleficence", "Autonomy", "Justice"]),
        ("Vendor opacity and procurement gaps vs. public accountability", ["Explicability", "Justice"]),
    ],
    "Riverton AI-Enabled Threat": [
        ("Automated control for quick stabilization vs. human oversight and explainability", ["Beneficence", "Autonomy", "Explicability"]),
        ("Hot-fix retraining now vs. rigorous assurance before redeploy", ["Non-maleficence", "Beneficence", "Explicability"]),
        ("Proprietary constraints vs. documentation and external review", ["Explicability", "Justice"]),
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
- **Backbone:** This prototype draws on the NIST Cybersecurity Framework, guiding users through six core functions: Govern, Identity, Protect, Detect, Respond, and Recover. These are integrated with Principlist ethical values: Beneficence, Non-maleficence, Autonomy, Justice, and Explicability - to help ussers weigh trade-offs and make morally  defensible decisions.  
- **Context:** Designed specifically for municipal use, the prototype accounts for real-world constraints like limited budgets, fragmented authority, and vendor opacity. It supports ethical decision-making within these practical and political realities. 
        """
    )

st.divider()

# ---------- 1) Scenario overview ----------
scenario = st.selectbox("Choose a Municipal Cybersecurity Scenario", options=list(scenario_summaries.keys()))
st.markdown("### 1) Scenario Overview")
st.markdown(f"**Scenario Overview:** {scenario_summaries[scenario]}")

incident_type = scenario
description = scenario_summaries[scenario]
pd_defaults = dict(description="", stakeholders=[], values=[], constraints=[])

st.divider()

# ---------- 2) Technical Evaluation (NIST CSF) ----------
st.markdown("### 2) Technical Evaluation (NIST CSF)")
with st.expander("About the NIST CSF"):
    st.markdown("""
The **NIST Cybersecurity Framework (CSF) 2.0** is a risk-based framework created by the 
National Institute of Standards and Technology to help organizations manage and reduce 
cybersecurity risks. It is organized into six core functions, which together provide a 
comprehensive approach to managing cyber risk:

- **Govern (GV):** Establish and communicate organizational context, roles, policies, and oversight for managing cybersecurity risk.  
- **Identify (ID):** Develop an organizational understanding of systems, people, assets, data, and capabilities to manage risk.  
- **Protect (PR):** Develop and implement safeguards to ensure delivery of critical services.  
- **Detect (DE):** Develop and implement activities to identify the occurrence of a cybersecurity event.  
- **Respond (RS):** Take appropriate action regarding a detected cybersecurity incident.  
- **Recover (RC):** Maintain plans for resilience and restore capabilities impaired by incidents.  

In this prototype, the CSF provides the **technical backbone**.  
Relevant CSF functions are highlighted for each scenario, and notes explain how they 
apply in that specific situation—ensuring that ethical reasoning (via the Principlist 
Framework) is grounded in recognized technical standards.
    """)

# Suggested functions
suggested_nist = suggest_nist(incident_type, description)

# Per-scenario “how it applies” notes
def scenario_csfs_explanations(incident_text: str) -> dict:
    t = incident_text.lower()
    notes = {
        "Govern (GV)": "Clarify decision rights, escalation, and documentation duties for this scenario.",
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
        notes["Govern (GV)"] = "Ensure policy/oversight and due process around repurposing technology."
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

# ---- NEW BULLET LIST STYLE (mirrors ethical tensions section) ----
st.markdown("#### Technical considerations in this scenario")
st.caption("What the NIST CSF suggests focusing on for this case.")
if mode == "Thesis scenarios":
    selected_nist = suggested_nist[:]
    # Build clean <ul><li> list for readability
    items = []
    for fn in NIST_FUNCTIONS:
        mark = " ✓" if fn in suggested_nist else ""
        tip = scenario_tips.get(fn, "—")
        items.append(f"<li><b>{fn}</b>{mark} — {tip}</li>")
    st.markdown(f"<div class='listbox'><ul class='tight-list'>{''.join(items)}</ul></div>", unsafe_allow_html=True)
else:
    selected_nist = []
    cols_fn = st.columns(3)
    for i, fn in enumerate(NIST_FUNCTIONS):
        with cols_fn[i % 3]:
            checked = st.checkbox(fn, value=(fn in suggested_nist), key=f"fn_{fn}")
            if checked:
                selected_nist.append(fn)
            st.caption(scenario_tips.get(fn, "—"))

st.divider()

# ---------- 3) Ethical Evaluation (Principlist) ----------
st.markdown("### 3) Ethical Evaluation (Principlist)")
with st.expander("About the Principlist Framework"):
    st.markdown("""
The **Principlist Framework for Cybersecurity Ethics** is a practical approach to ethical 
reasoning that balances multiple values when making decisions under pressure. It is 
organized into five core principles, which together provide a comprehensive approach 
to identifying, weighing, and justifying ethical trade-offs:

- **Beneficence:** Promote public well-being and the delivery of essential services.  
- **Non-maleficence:** Avoid foreseeable harm from actions taken or omitted (e.g., over-collection, rash shutdowns).  
- **Autonomy:** Respect legal rights, due process, and meaningful choice for affected people.  
- **Justice:** Distribute burdens and benefits fairly; avoid disproportionate impact on specific communities.  
- **Explicability:** Ensure transparency, accountability, and the ability to explain decisions and system behavior.  

In this prototype, the Principlist Framework provides the **ethical backbone**.  
Relevant principles are highlighted for each scenario, making value tensions explicit 
so that technical standards (via the NIST CSF) are always considered in light of 
ethical reasoning.
    """)

# Auto-suggested principles for internal logic (no chips shown)
auto_principles = suggest_principles(description)
if mode == "Thesis scenarios":
    selected_principles = auto_principles[:]
else:
    selected_principles = st.multiselect("Select relevant ethical principles (optional)", PRINCIPLES, default=auto_principles)

# ---------- Ethical tensions in this scenario (UPDATED to show Principlist terms) ----------
st.markdown("#### Ethical tensions in this scenario")
st.caption("Key value trade-offs in this case framed in Principlist terms.")
tensions = ETHICAL_TENSIONS_BY_SCENARIO.get(scenario, [])
if tensions:
    items = []
    for label, tags in tensions:
        tag_str = ", ".join(tags) if tags else "—"
        items.append(f"<li>{label}<div class='sub'>Principlist lens: <i>{tag_str}</i></div></li>")
    st.markdown(f"<div class='listbox'><ul class='tight-list'>{''.join(items)}</ul></div>", unsafe_allow_html=True)
else:
    st.info("No predefined ethical tensions for this scenario.")

st.divider()

# ---------- 4) Decision-Support Matrix ----------
st.markdown("### 4) Decision-Support Matrix")
with st.expander("What is this matrix?"):
    st.markdown("""
This matrix is a **decision-support tool** that combines the NIST Cybersecurity Framework (technical standards) 
with the Principlist Framework (ethical reasoning). It highlights where **technical actions and ethical principles intersect** in a given scenario.  

- **Rows** = NIST CSF functions, representing the *technical steps and responsibilities*.  
- **Columns** = Principlist ethical principles, representing the *moral values at stake*.  
- **Cells** = Points of overlap where a technical function raises or impacts a specific ethical concern.  

By mapping these intersections, the matrix helps practitioners:  
- Identify **where value conflicts emerge** in technical actions.  
- Ensure **ethical reasoning is embedded in technical decisions**.  
- Create a **structured, transparent record** of why certain actions were prioritized.  
    """)
use_weights = st.toggle("Use 0–5 weighting instead of checkboxes", value=False, key="mx_use_weights")

PREHIGHLIGHT = {
    "Baltimore Ransomware Attack": [
        ("Respond (RS)", "Justice"),
        ("Protect (PR)", "Non-maleficence"),
        ("Recover (RC)", "Beneficence"),
        ("Govern (GV)", "Explicability"),
        ("Identify (ID)", "Justice"),
    ],
    "San Diego Smart Streetlights and Surveillance": [
        ("Govern (GV)", "Autonomy"),
        ("Govern (GV)", "Justice"),
        ("Govern (GV)", "Explicability"),
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
        ("Govern (GV)", "Explicability"),
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
        st.progress(min(int((fn_totals[fn] / (5*len(PRINCIPLES) if use_weights else len(PRINCIPLES))) * 100), 100),
                    text=f"{fn}: {fn_totals[fn]}")
with colB:
    st.markdown("**Totals by Ethical principle**")
    for p in PRINCIPLES:
        st.progress(min(int((pr_totals[p] / (5*len(NIST_FUNCTIONS) if use_weights else len(NIST_FUNCTIONS))) * 100), 100),
                    text=f"{p}: {pr_totals[p]}")

st.session_state["nist_principle_matrix"] = matrix_state
st.session_state["nist_totals_by_function"] = fn_totals
st.session_state["principle_totals"] = pr_totals

st.divider()

# ---------- 4) Institutional & Governance Constraints ----------
st.markdown("### 4) Institutional & Governance Constraints")
constraints = st.multiselect("Select constraints relevant to this scenario", GOV_CONSTRAINTS, default=pd_defaults.get("constraints", []))

st.divider()

# ---------- 5) Ethical Tension Score ----------
st.markdown("### 5) Ethical Tension Score")
if 'stakeholders' not in locals(): stakeholders = []
if 'values' not in locals(): values = []
score = score_tension(selected_principles, selected_nist, constraints, stakeholders, values)
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
