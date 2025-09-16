import streamlit as st
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(page_title="Municipal Ethical Cyber Decision-Support", layout="wide", initial_sidebar_state="expanded")

# ---------- Minimal styling (cosmetic only) ----------
st.markdown("""
<style>
.listbox{background:#f9fbff;border-left:4px solid #4C8BF5;padding:10px 14px;border-radius:8px;margin:6px 0 14px;}
.section-note{color:#6b7280;font-size:0.9rem;margin:-4px 0 10px 0;}
.tight-list{margin:0.25rem 0 0 1.15rem;padding:0;}
.tight-list li{margin:6px 0;}
.sub{color:#6b7280;font-size:0.95rem;}
.badges{display:flex;flex-wrap:wrap;gap:.35rem;margin:.35rem 0 0 0;}
.badge{display:inline-block;padding:.2rem .5rem;border-radius:999px;border:1px solid #e5e7eb;font-size:.85rem}
.badge.nist{background:#eef2ff;border-color:#c7d2fe;}
.badge.principle{background:#ecfeff;border-color:#a5f3fc;}
.badge.note{background:#fef9c3;border-color:#fde68a;}
h3, h4 { margin-bottom: .4rem; }
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

# ---------- Header ----------
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
- **Purpose:** Support municipal cybersecurity practitioners in navigating complex ethical dilemmas. This tool guides users through high-stakes decisions in real time—aligning actions with technical standards, clarifying value conflicts, and documenting justifiable outcomes under institutional and governance constraints.  
- **Backbone:** This prototype draws on the NIST Cybersecurity Framework, guiding users through six core functions: **Govern, Identify, Protect, Detect, Respond, Recover**. These are integrated with Principlist ethical values—**Beneficence, Non-maleficence, Autonomy, Justice, Explicability**—to help users weigh trade-offs and make morally defensible decisions.  
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
auto_principles = suggest_principles(description)
suggested_nist = suggest_nist(incident_type, description)

# Scenario “tags”
st.markdown("<div class='badges'>"+ "".join([f"<span class='badge nist'>NIST: {f}</span>" for f in suggested_nist]) + "</div>", unsafe_allow_html=True)
st.markdown("<div class='badges'>"+ "".join([f"<span class='badge principle'>{p}</span>" for p in auto_pri_]()
