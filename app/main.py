import streamlit as st
from datetime import datetime
# --- put at the top with other imports ---
import base64
import streamlit.components.v1 as components

# --- NEW: YAML + Path imports and loaders ---
from pathlib import Path
import yaml

# --- NEW: PDF helpers ---
from io import BytesIO
try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False

# Point to your repo’s /data folder (assuming this file is in /app)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@st.cache_data
def load_yaml_file(filename: str):
    path = DATA_DIR / filename
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

@st.cache_data
def load_all_data():
    nist = load_yaml_file("nist_csf.yaml")              # { meta, functions: [{name, definition, illustrative_actions}] }
    principlist = load_yaml_file("principlist.yaml")    # { meta, principles: [{name, definition, illustrative_examples}] }
    dilemmas = load_yaml_file("municipal_dilemmas.yaml")# { <scenario>: {overview, technical, ethical_tensions: [...] } }
    # --- NEW: load thesis constraints ---
    constraints = load_yaml_file("scenario_constraints.yaml")  # supports several shapes; handled below
    return nist, principlist, dilemmas, constraints

NIST_YAML, PRINCIPLIST_YAML, DILEMMAS_YAML, CONSTRAINTS_YAML = load_all_data()

# Derive names from YAML if present; fall back to your constants later
NIST_FUNCTIONS_FROM_YAML = [f.get("name", "").strip() for f in NIST_YAML.get("functions", []) if f.get("name")]
PRINCIPLES_FROM_YAML = [p.get("name", "").strip() for p in PRINCIPLIST_YAML.get("principles", []) if p.get("name")]

# --- STRICT (source-only) switch ---
STRICT_SOURCE_ONLY = True

# Canonical definition maps from YAML (used in strict mode)
NIST_DEF = {f.get("name"): f.get("definition", "") for f in NIST_YAML.get("functions", []) if f.get("name")}
PRINCIPLE_DEF = {p.get("name"): p.get("definition", "") for p in PRINCIPLIST_YAML.get("principles", []) if p.get("name")}

# ---------- Page config ----------
st.set_page_config(
    page_title="Municipal Cyber Ethics Decision-Support",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Minimal styling for list emphasis & readability (NEW, cosmetic only) ----------
st.markdown("""
<style>
/* === Font (Inter) + base tokens === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class^="css"] {
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji"!important;
}

/* tokens */
:root{
  --brand: #4C8BF5;
  --brand-2: #7aa8ff;
  --bg-soft: #0b1020;   /* deep navy feel in dark */
  --text-strong: #111827;
  --text-muted: #6b7280;
  --card-bg: #f9fbff;
  --card-border: var(--brand);
}
@media (prefers-color-scheme: dark){
  :root{
    --text-strong: #e5e7eb;
    --text-muted: #94a3b8;
    --card-bg: rgba(255,255,255,0.05);
  }
}

/* App background (feels “app-like”, not a form) */
div[data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 600px at 10% -10%, rgba(76,139,245,0.15), transparent 60%),
              radial-gradient(900px 500px at 100% 0%, rgba(122,168,255,0.10), transparent 60%),
              var(--bg-soft);

  /* Force light-on-dark tokens for text visibility */
  --text-strong: #e5e7eb;
  --text-muted: #94a3b8;
  --card-bg: rgba(255,255,255,0.05);
}

/* Sidebar polish */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  border-right: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(6px);
}
section[data-testid="stSidebar"] *{
  color: var(--text-strong) !important;
}

/* Header: subtle glass bar */
.block-container > div:first-child{
  backdrop-filter: blur(6px);
  border-radius: 14px;
  padding: 8px 14px;
  border: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
}

/* “Cards” used in sections 2,3,5 (glassmorphism) */
.listbox{
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
  border-left: 4px solid var(--brand);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 10px 24px rgba(0,0,0,0.25);
  padding: 12px 14px;
  border-radius: 14px;
  margin: 8px 0 16px;
}
.listbox, .listbox *{ color: var(--text-strong) !important; }
.tight-list{ margin: 0.25rem 0 0 1.15rem; padding: 0; }
.tight-list li{ margin: 6px 0; }
.tight-list li::marker{ color: var(--text-muted); }

/* Section captions / helper text */
.section-note, .sub{ color: var(--text-muted) !important; }

/* Buttons: rounded, gradient, micro-interaction */
.stButton > button{
  border: 0;
  padding: 0.7rem 1rem;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: white !important;
  box-shadow: 0 10px 20px rgba(76,139,245,0.35);
  transition: transform .06s ease, box-shadow .15s ease, filter .15s ease;
}
.stButton > button:hover{
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(76,139,245,0.45);
  filter: brightness(1.05);
}
.stButton > button:active{ transform: translateY(0); }

/* Inputs: cleaner fields, dark-aware */
input, textarea, select, .stTextInput input, .stTextArea textarea{
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  color: var(--text-strong) !important;
  border-radius: 10px !important;
}
label, .stRadio, .stSelectbox, .stMultiSelect, .stExpander{
  color: var(--text-strong) !important;
}

/* Expander headers: pill look */
details > summary{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 12px;
  padding: 10px 12px;
  color: var(--text-strong);
}

/* Checkbox / radio accent color */
input[type="checkbox"], input[type="radio"]{ accent-color: var(--brand); }

/* Hide default Streamlit chrome if you want an ultra-clean look */
header[data-testid="stHeader"]{ background: transparent; }
footer, #MainMenu{ visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------- NIST CSF 2.0 constants ----------
# If YAML present, prefer its function names; otherwise use your original list
NIST_FUNCTIONS = NIST_FUNCTIONS_FROM_YAML or [
    "Govern (GV)",
    "Identify (ID)",
    "Protect (PR)",
    "Detect (DE)",
    "Respond (RS)",
    "Recover (RC)",
]

# ---------- Simple rule-based NLP helpers (no external deps) ----------
# (Kept for compatibility, but bypassed in strict mode)
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

# If YAML has principles, prefer it; else use your original list
PRINCIPLES = PRINCIPLES_FROM_YAML or ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"]

def suggest_nist(incident_type: str, description: str):
    # Heuristic function kept for compatibility; not used in strict mode
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
    # Heuristic function kept for compatibility; not used in strict mode
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
with st.sidebar:
    st.markdown("<h3 style='margin:0 0 0.5rem 0; font-weight:700;'>Mode</h3>", unsafe_allow_html=True)
    mode = st.radio(
        label="",
        options=["Thesis scenarios", "Open-ended"],
        index=0,
        key="mode_selector",                 # explicit key avoids collisions
        label_visibility="collapsed",
    )
# --- Mode reset so cached text fields clear when switching modes ---
if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode

if mode != st.session_state.last_mode:
    for k in ["dl_overview", "dl_nist", "dl_principlist", "dl_tensions", "dl_constraints"]:
        st.session_state[k] = ""
    st.session_state.last_mode = mode
    
# ---------- Intro ----------
st.markdown(
    """
    <div style='text-align: center;'>
        <h1>🛡️ Municipal Cyber Ethics Decision-Support Prototype</h1>
        <h4 style='color:#4C8BF5;'>Because what's secure isn't always what's right.</h4>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("About this prototype"):
    st.markdown(
        """
- **Purpose:** Support municipal cybersecurity practitioners in navigating complex ethical dilemmas. This tool guides users through high-stakes decisions in real time by bringing ethical principles and technical standards into dialogue, clarifying value conflicts, and documenting the reasoning process for transparency and accountability within institutional and governance constraints.  
- **Backbone:** This prototype draws on the NIST Cybersecurity Framework to guide users through six core functions—Govern, Identify, Protect, Detect, Respond, and Recover—while concurrently referencing the Principlist ethical values of Beneficence, Non-maleficence, Autonomy, Justice, and Explicability. By examining these frameworks in parallel, the prototype helps users reflect on ethical and technical guidance in the context of municipal constraints and generate a transparent record of the considerations that informed their decisions.  
- **Context:** Designed specifically for municipal use, the prototype accounts for real-world constraints like limited budgets, fragmented authority, and vendor opacity. It supports ethical decision-making within these practical and political realities while ensuring accountability for how decisions are reached.
        """
    )

st.divider()

# ---------- Appendix at bottom of sidebar ----------
st.sidebar.markdown("---")  # divider for clarity
with st.sidebar.expander("📚 Appendix: Framework Sources"):
    st.markdown("""
**National Institute of Standards and Technology.**  
*The NIST Cybersecurity Framework (CSF) 2.0.*  
National Institute of Standards and Technology, 2024.  
[https://doi.org/10.6028/NIST.CSWP.29](https://doi.org/10.6028/NIST.CSWP.29)  

**Formosa, Paul, Michael Wilson, and Deborah Richards.**  
"A Principlist Framework for Cybersecurity Ethics."  
*Computers & Security* 109 (2021): 1–15.  
[https://doi.org/10.1016/j.cose.2021.102382](https://doi.org/10.1016/j.cose.2021.102382)  
    """)

# ---------- 1) Scenario overview ----------
if mode == "Thesis scenarios":
    scenario = st.selectbox("Choose a Municipal Cybersecurity Scenario", options=list(scenario_summaries.keys()))
    st.markdown("### 1) Scenario Overview")
    st.markdown(f"**Scenario Overview:** {scenario_summaries[scenario]}")
    incident_type = scenario
    description = scenario_summaries[scenario]
else:
    # Open-ended mode pulls from YAML dilemmas
    open_options = sorted(list(DILEMMAS_YAML.keys()))
    if not open_options:
        st.warning("No open-ended dilemmas found in data/municipal_dilemmas.yaml.")
        open_options = []
    scenario = st.selectbox("Choose a Municipal Cybersecurity Scenario", options=open_options)
    st.markdown("### 1) Scenario Overview")
    if scenario:
        entry = DILEMMAS_YAML.get(scenario, {})
        description = entry.get("overview", "—")
        st.markdown(f"**Scenario Overview:** {description}")
        incident_type = scenario
    else:
        description = ""
        incident_type = ""

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

# Suggested functions — strict = YAML only (no heuristics)
if mode == "Open-ended" and scenario:
    entry = DILEMMAS_YAML.get(scenario, {})
    yaml_funcs = entry.get("technical", [])
    suggested_nist = yaml_funcs[:] if STRICT_SOURCE_ONLY else (yaml_funcs[:] or suggest_nist(incident_type, description))
else:
    # Thesis scenarios: use canonical NIST list (strict) instead of heuristic suggestions
    suggested_nist = NIST_FUNCTIONS[:] if STRICT_SOURCE_ONLY else suggest_nist(incident_type, description)

# Per-scenario “how it applies” notes — strict uses canonical NIST definitions
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

# In strict mode, display canonical definitions from YAML as the “tips”
if STRICT_SOURCE_ONLY and NIST_DEF:
    scenario_tips = {fn: NIST_DEF.get(fn, "—") for fn in NIST_FUNCTIONS}
else:
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

# Auto-suggested principles for internal logic (strict = canonical list only)
if STRICT_SOURCE_ONLY:
    auto_principles = PRINCIPLES[:]  # all canonical principles
else:
    auto_principles = suggest_principles(description)

if mode == "Thesis scenarios":
    selected_principles = auto_principles[:]
else:
    selected_principles = st.multiselect("Select relevant ethical principles (optional)", PRINCIPLES, default=auto_principles)

# ---------- Ethical tensions in this scenario (UPDATED to show Principlist terms) ----------
st.markdown("#### Ethical tensions in this scenario")
st.caption("Key value trade-offs in this case framed in Principlist terms.")
if mode == "Open-ended" and scenario:
    entry = DILEMMAS_YAML.get(scenario, {})
    tensions = entry.get("ethical_tensions", [])
    if tensions:
        items = []
        for t in tensions:
            label = t.get("description", "—")
            tags = t.get("principles", [])
            tag_str = ", ".join(tags) if tags else "—"
            items.append(f"<li>{label}<div class='sub'>Principlist lens: <i>{tag_str}</i></div></li>")
        st.markdown(f"<div class='listbox'><ul class='tight-list'>{''.join(items)}</ul></div>", unsafe_allow_html=True)
    else:
        st.info("No predefined ethical tensions for this scenario.")
else:
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
with st.expander("What this matrix does"):
    st.markdown("""
The matrix is designed to help practitioners **consider technical and ethical dimensions together** when making high-stakes cybersecurity decisions.  

- **Rows = NIST CSF functions** — the technical steps needed to manage the incident.  
- **Columns = Principlist ethical principles** — the values that should guide how those steps are carried out.  
- **Cells = points of integration** — reminders to ensure that each technical action is considered in light of relevant ethical principles.  

This approach does not assume conflict between technical and ethical concerns. Instead, it ensures **completeness of reasoning**, so that municipal practitioners act in ways that are both technically sound and ethically defensible under real-world constraints.  
    """)

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
            mark = st.checkbox(" ", value=default_marked, key=key, label_visibility="collapsed")
            matrix_state[(fn, p)] = 1 if mark else 0

st.divider()

# ---------- 5) Institutional & Governance Constraints ----------
st.markdown("### 5) Institutional & Governance Constraints")
with st.expander("About Institutional & Governance Constraints"):
    st.markdown("""
Cybersecurity professionals in municipalities often face **institutional and governance constraints** that limit their options for action.  
These include unclear decision rights, procurement opacity, tight budgets, limited oversight, and outdated technology.  
Documenting these constraints makes explicit the practical limits within which professionals must operate, ensuring that technical and ethical reasoning remains grounded in real-world conditions.
    """)

# --- NEW: helper to read constraints for a thesis scenario from scenario_constraints.yaml
def _get_thesis_constraints(scn: str):
    d = CONSTRAINTS_YAML or {}
    entry = None
    if isinstance(d.get("scenarios"), dict):
        entry = d["scenarios"].get(scn)
    if entry is None:
        entry = d.get(scn)

    if entry is None:
        return []

    if isinstance(entry, list):
        return entry
    if isinstance(entry, dict):
        if isinstance(entry.get("constraints"), list):
            return entry["constraints"]
        if isinstance(entry.get("items"), list):
            return entry["items"]
    return []

if mode == "Thesis scenarios":
    thesis_constraints = _get_thesis_constraints(scenario)
    if thesis_constraints:
        st.markdown(f"<div class='listbox'><ul class='tight-list'>{''.join([f'<li>{c}</li>' for c in thesis_constraints])}</ul></div>", unsafe_allow_html=True)
    else:
        st.info("No predefined constraints found for this scenario.")
    final_constraints = thesis_constraints
else:
    # Open-ended keeps the editable multiselect
    constraints = st.multiselect("Select constraints relevant to this scenario", GOV_CONSTRAINTS, default=pd_defaults.get("constraints", []))
    final_constraints = constraints

st.divider()

# ---------- 6) Decision Support Log (auto-filled & PDF export) ----------
st.markdown("### 6) Decision Support Log")
with st.expander("What this section is for"):
    st.markdown("""
This log **auto-populates** from your analysis above (scenario, NIST functions, Principlist values, ethical tensions, and constraints),
and lets you export a timestamped PDF for records and transparency.
    """)

# --- Build helpful defaults from previous sections ---
# ✅ AUTO-FILL CONTROLLER
if mode == "Thesis scenarios" and scenario:
    tensions_lines = []
    for t in ETHICAL_TENSIONS_BY_SCENARIO.get(scenario, []):
        tensions_lines.append(f"{t[0]} — Principlist: {', '.join(t[1])}")
    constraints_list = _get_thesis_constraints(scenario)
    st.session_state["dl_overview"] = scenario_summaries.get(scenario, "")
    st.session_state["dl_nist"] = "\n".join([f"- {f}" for f in NIST_FUNCTIONS])
    st.session_state["dl_principlist"] = "\n".join([f"- {p}" for p in PRINCIPLES])
    st.session_state["dl_tensions"] = "\n".join([f"- {t}" for t in tensions_lines])
    st.session_state["dl_constraints"] = "\n".join([f"- {c}" for c in constraints_list])
elif mode == "Open-ended" and scenario:
    entry = DILEMMAS_YAML.get(scenario, {})
    tensions = entry.get("ethical_tensions", [])
    tensions_lines = []
    for t in tensions:
        label = t.get("description", "")
        tags = ", ".join(t.get("principles", []))
        tensions_lines.append(f"{label}" + (f" — Principlist: {tags}" if tags else ""))
    st.session_state["dl_overview"] = entry.get("overview", "")
    st.session_state["dl_nist"] = "\n".join([f"- {f}" for f in entry.get("technical", [])])
    st.session_state["dl_principlist"] = "\n".join([f"- {p}" for p in PRINCIPLES])
    st.session_state["dl_tensions"] = "\n".join([f"- {t}" for t in tensions_lines])
    st.session_state["dl_constraints"] = "\n".join([f"- {c}" for c in entry.get("constraints", [])])

def _fmt_bullets(items):
    return "\n".join([f"- {x}" for x in items]) if items else "—"

def _normalize_tensions_to_lines(t):
    out = []
    if not t:
        return out
    # thesis: [(label, [principles])] | open-ended: [{"description", "principles"}]
    for item in t:
        if isinstance(item, (tuple, list)):
            label = item[0]
            tags = ", ".join(item[1]) if len(item) > 1 and isinstance(item[1], list) else ""
            out.append(f"{label}" + (f" — Principlist: {tags}" if tags else ""))
        elif isinstance(item, dict):
            lab = item.get("description", "")
            tags = ", ".join(item.get("principles", []))
            out.append(f"{lab}" + (f" — Principlist: {tags}" if tags else ""))
        else:
            out.append(str(item))
    return out

_default_risks = (
    "Potential operational disruption; reputational impact; equity concerns for affected groups; "
    "vendor and legal dependencies; residual risk if mitigations are delayed."
)

_default_mitigations = (
    "Enforce least privilege and change freeze where applicable; communicate clearly with stakeholders; "
    "document rationale and oversight; stage rollbacks; monitor outcomes; schedule post-incident review."
)

# Keep a normalized view of tensions for display/PDF
norm_tensions = _normalize_tensions_to_lines(tensions)

# Use final_constraints (set above) for both modes
constraints_list = final_constraints or []

# --- User-editable but pre-populated fields ---
colA, colB = st.columns(2)
with colA:
    pass
with colB:
    # Date/time is auto in PDF; show it here read-only for clarity
    st.text_input("Date & time (auto)", value=datetime.now().strftime("%Y-%m-%d %H:%M"), disabled=True)

st.markdown("##### Auto-filled context (edit if needed)")
st.text_area("Scenario Overview", value=(description or "—"), height=110, key="dl_overview")

st.text_area(
    "NIST CSF Functions Emphasized",
    value=_fmt_bullets(selected_nist or []),
    height=110,
    key="dl_nist"
)

st.text_area(
    "Principlist Values Considered",
    value=_fmt_bullets(selected_principles or []),
    height=110,
    key="dl_principlist"
)

st.text_area(
    "Ethical Tensions (auto from above)",
    value=_fmt_bullets(norm_tensions),
    height=120,
    key="dl_tensions"
)

st.text_area(
    "Institutional & Governance Constraints (auto from above)",
    value=_fmt_bullets(constraints_list),
    height=120,
    key="dl_constraints"
)

st.markdown("##### Decision fields")
risks = st.text_area("Key Risks", value=_default_risks, height=120)
mitigations = st.text_area("Mitigations / Safeguards", value=_default_mitigations, height=120)
stakeholders = st.text_area("Key Stakeholders (optional)", value="", height=90)
notes = st.text_area("Additional Notes (optional)", value="", height=90)

# --- PDF generator (uses ReportLab imports defined earlier) ---
def generate_pdf():
    if not REPORTLAB_OK:
        st.error("PDF engine not available. Add `reportlab` to your requirements.txt to enable PDF export.")
        return None

    from io import BytesIO
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="H1", fontSize=16, leading=20, spaceAfter=10, textColor=colors.HexColor("#1f2937")))
    styles.add(ParagraphStyle(name="H2", fontSize=13, leading=16, spaceBefore=8, spaceAfter=6, textColor=colors.HexColor("#111827")))
    styles.add(ParagraphStyle(name="Body", fontSize=10.5, leading=14))
    story = []

    # Header / meta
    story.append(Paragraph("Municipal Ethical Cyber Decision Log", styles["H1"]))
    meta_table = Table(
        [
            ["Scenario", scenario],
            ["Date/Time", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ],
        colWidths=[110, 380],
        hAlign="LEFT",
    )
    meta_table.setStyle(TableStyle([
        ("FONT", (0,0), (-1,-1), "Helvetica", 9.5),
        ("TEXTCOLOR", (0,0), (0,-1), colors.grey),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Overview
    story.append(Paragraph("Scenario Overview", styles["H2"]))
    story.append(Paragraph(st.session_state.get("dl_overview","—").replace("\n","<br/>"), styles["Body"]))
    story.append(Spacer(1, 6))

    # NIST & Principlist
    story.append(Paragraph("NIST CSF Functions Emphasized", styles["H2"]))
    nist_lines = [x.strip("- ").strip() for x in st.session_state.get("dl_nist","").splitlines() if x.strip()]
    story.append(ListFlowable([ListItem(Paragraph(x, styles["Body"])) for x in nist_lines] or [ListItem(Paragraph("—", styles["Body"]))], bulletType="bullet", leftIndent=18))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Principlist Values Considered", styles["H2"]))
    pr_lines = [x.strip("- ").strip() for x in st.session_state.get("dl_principlist","").splitlines() if x.strip()]
    story.append(ListFlowable([ListItem(Paragraph(x, styles["Body"])) for x in pr_lines] or [ListItem(Paragraph("—", styles["Body"]))], bulletType="bullet", leftIndent=18))
    story.append(Spacer(1, 6))

    # Ethical tensions
    story.append(Paragraph("Ethical Tensions", styles["H2"]))
    ten_lines = [x.strip("- ").strip() for x in st.session_state.get("dl_tensions","").splitlines() if x.strip()]
    story.append(ListFlowable([ListItem(Paragraph(x, styles["Body"])) for x in ten_lines] or [ListItem(Paragraph("—", styles["Body"]))], bulletType="bullet", leftIndent=18))
    story.append(Spacer(1, 6))

    # Constraints
    story.append(Paragraph("Institutional & Governance Constraints", styles["H2"]))
    con_lines = [x.strip("- ").strip() for x in st.session_state.get("dl_constraints","").splitlines() if x.strip()]
    story.append(ListFlowable([ListItem(Paragraph(x, styles["Body"])) for x in con_lines] or [ListItem(Paragraph("—", styles["Body"]))], bulletType="bullet", leftIndent=18))
    story.append(Spacer(1, 10))

    # Decision-related fields (no decision maker / title)
    story.append(Paragraph("Key Risks", styles["H2"]))
    story.append(Paragraph((risks or "—").replace("\n","<br/>"), styles["Body"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Mitigations / Safeguards", styles["H2"]))
    story.append(Paragraph((mitigations or "—").replace("\n","<br/>"), styles["Body"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Stakeholders", styles["H2"]))
    story.append(Paragraph((stakeholders or "—").replace("\n","<br/>"), styles["Body"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Additional Notes", styles["H2"]))
    story.append(Paragraph((notes or "—").replace("\n","<br/>"), styles["Body"]))

    doc.build(story)
    buf.seek(0)
    return buf

# Export
if st.button("📄 Generate PDF Decision-Support Log"):
    pdf_buf = generate_pdf()
    if pdf_buf:
        filename = f"decision_log_{scenario.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

        # 1) Normal Streamlit download button (fallback / accessible)
        st.download_button("Download PDF", data=pdf_buf, file_name=filename, mime="application/pdf")

        # 2) Auto-trigger download via a hidden anchor
        b64 = base64.b64encode(pdf_buf.getvalue()).decode("utf-8")
        components.html(
            f"""
            <a id="autodl" href="data:application/pdf;base64,{b64}" download="{filename}"></a>
            <script>
              const a = document.getElementById('autodl');
              if (a) a.click();
            </script>
            """,
            height=0,
        )

# ---------- Footer ----------
st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes.")
