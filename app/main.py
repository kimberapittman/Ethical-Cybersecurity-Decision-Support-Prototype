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
    nist = load_yaml_file("nist_csf.yaml")
    principlist = load_yaml_file("principlist.yaml")
    dilemmas = load_yaml_file("municipal_dilemmas.yaml")
    constraints = load_yaml_file("scenario_constraints.yaml")
    return nist, principlist, dilemmas, constraints

NIST_YAML, PRINCIPLIST_YAML, DILEMMAS_YAML, CONSTRAINTS_YAML = load_all_data()

NIST_FUNCTIONS_FROM_YAML = [f.get("name", "").strip() for f in NIST_YAML.get("functions", []) if f.get("name")]
PRINCIPLES_FROM_YAML = [p.get("name", "").strip() for p in PRINCIPLIST_YAML.get("principles", []) if p.get("name")]

STRICT_SOURCE_ONLY = True
NIST_DEF = {f.get("name"): f.get("definition", "") for f in NIST_YAML.get("functions", []) if f.get("name")}
PRINCIPLE_DEF = {p.get("name"): p.get("definition", "") for p in PRINCIPLIST_YAML.get("principles", []) if p.get("name")}

st.set_page_config(
    page_title="Municipal Cyber Ethics Decision-Support",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Minimal styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class^="css"] { font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial!important; }
:root{ --brand:#4C8BF5; --brand-2:#7aa8ff; --bg-soft:#0b1020; --text-strong:#111827; --text-muted:#6b7280; }
@media (prefers-color-scheme: dark){
:root{ --text-strong:#e5e7eb; --text-muted:#94a3b8; --card-bg:rgba(255,255,255,0.05);}
}
div[data-testid="stAppViewContainer"]{
background: radial-gradient(1200px 600px at 10% -10%, rgba(76,139,245,0.15), transparent 60%),
radial-gradient(900px 500px at 100% 0%, rgba(122,168,255,0.10), transparent 60%), var(--bg-soft);
--text-strong:#e5e7eb; --text-muted:#94a3b8; --card-bg:rgba(255,255,255,0.05);
}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02));border-right:1px solid rgba(255,255,255,0.08);backdrop-filter:blur(6px);}
section[data-testid="stSidebar"] *{color:var(--text-strong)!important;}
header[data-testid="stHeader"]{background:transparent;} footer,#MainMenu{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- NIST CSF 2.0 constants ----------
NIST_FUNCTIONS = NIST_FUNCTIONS_FROM_YAML or [
    "Govern (GV)", "Identify (ID)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"
]

ETHICAL_HINTS = {
    "privacy": ["Autonomy", "Justice", "Explicability"],
    "surveillance": ["Autonomy", "Justice", "Explicability", "Non-maleficence"],
    "ransom": ["Justice", "Non-maleficence", "Beneficence"],
    "water": ["Beneficence", "Non-maleficence", "Justice", "Explicability"],
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

scenario_summaries = {
    "Baltimore Ransomware Attack": (
        "In 2019, Baltimore’s municipal systems were crippled by a ransomware attack..."
    ),
    "San Diego Smart Streetlights and Surveillance": (
        "San Diego deployed smart streetlights to collect traffic and environmental data..."
    ),
    "Riverton AI-Enabled Threat": (
        "In the fictional city of Riverton, adversarial signals disrupted an AI-based monitoring system..."
    )
}

PRINCIPLES = PRINCIPLES_FROM_YAML or ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"]

ETHICAL_TENSIONS_BY_SCENARIO = {
    "Baltimore Ransomware Attack": [
        ("Paying ransom vs refusing payment", ["Justice", "Non-maleficence", "Beneficence"])
    ],
    "San Diego Smart Streetlights and Surveillance": [
        ("Privacy protections vs public safety claims", ["Non-maleficence", "Autonomy", "Justice"])
    ],
    "Riverton AI-Enabled Threat": [
        ("Automated control vs human oversight", ["Beneficence", "Autonomy", "Explicability"])
    ],
}

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("<h3 style='margin:0 0 .5rem 0;'>Mode</h3>", unsafe_allow_html=True)
    mode = st.radio("", ["Thesis scenarios", "Open-ended"], index=0, key="mode_selector", label_visibility="collapsed")

# ---------- MODE RESET CONTROLLER ----------
if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode
if "last_scenario" not in st.session_state:
    st.session_state.last_scenario = None
if mode != st.session_state.last_mode:
    for key in ["dl_overview", "dl_nist", "dl_principlist", "dl_tensions", "dl_constraints"]:
        st.session_state[key] = ""
    st.session_state.last_mode = mode

# ---------- Intro ----------
st.markdown("<h1 style='text-align:center;'>🛡️ Municipal Cyber Ethics Decision-Support Prototype</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;color:#4C8BF5;'>Because what's secure isn't always what's right.</h4>", unsafe_allow_html=True)
st.divider()

# ---------- 1) Scenario overview ----------
if mode == "Thesis scenarios":
    scenario = st.selectbox("Choose a Municipal Cybersecurity Scenario", list(scenario_summaries.keys()))
    description = scenario_summaries[scenario]
else:
    open_options = sorted(list(DILEMMAS_YAML.keys()))
    scenario = st.selectbox("Choose a Municipal Cybersecurity Scenario", options=open_options)
    entry = DILEMMAS_YAML.get(scenario, {}) if scenario else {}
    description = entry.get("overview", "") if entry else ""

st.markdown(f"**Scenario Overview:** {description or '—'}")
st.divider()

# ---------- 6) Decision Support Log (simplified) ----------
st.markdown("### 6) Decision Support Log")

# ---------- AUTO-FILL CONTROLLER ----------
if mode == "Thesis scenarios" and scenario:
    st.session_state["dl_overview"] = scenario_summaries.get(scenario, "")
    st.session_state["dl_nist"] = "\n".join([f"- {x}" for x in NIST_FUNCTIONS])
    st.session_state["dl_principlist"] = "\n".join([f"- {x}" for x in PRINCIPLES])
    st.session_state["dl_tensions"] = "\n".join(
        [f"- {x[0]} — Principlist: {', '.join(x[1])}" for x in ETHICAL_TENSIONS_BY_SCENARIO.get(scenario, [])]
    )
    st.session_state["dl_constraints"] = "\n".join([f"- {x}" for x in GOV_CONSTRAINTS])
elif mode == "Open-ended" and scenario:
    entry = DILEMMAS_YAML.get(scenario, {})
    st.session_state["dl_overview"] = entry.get("overview", "")
    st.session_state["dl_nist"] = "\n".join([f"- {x}" for x in entry.get("technical", [])])
    st.session_state["dl_principlist"] = "\n".join([f"- {x}" for x in PRINCIPLES])
    tensions = entry.get("ethical_tensions", [])
    formatted_t = []
    for t in tensions:
        if isinstance(t, dict):
            desc = t.get("description", "")
            tags = ", ".join(t.get("principles", []))
            formatted_t.append(f"{desc}" + (f" — Principlist: {tags}" if tags else ""))
        else:
            formatted_t.append(str(t))
    st.session_state["dl_tensions"] = "\n".join([f"- {x}" for x in formatted_t])
    st.session_state["dl_constraints"] = "\n".join([f"- {x}" for x in entry.get("constraints", [])])
st.session_state["last_scenario"] = scenario if scenario else None

# ---------- Render Log ----------
st.text_area("Scenario Overview", value=st.session_state.get("dl_overview", ""), height=110, key="dl_overview")
st.text_area("NIST CSF Functions Emphasized", value=st.session_state.get("dl_nist", ""), height=110, key="dl_nist")
st.text_area("Principlist Values Considered", value=st.session_state.get("dl_principlist", ""), height=110, key="dl_principlist")
st.text_area("Ethical Tensions", value=st.session_state.get("dl_tensions", ""), height=120, key="dl_tensions")
st.text_area("Institutional & Governance Constraints", value=st.session_state.get("dl_constraints", ""), height=120, key="dl_constraints")

st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes.")
