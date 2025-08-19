import streamlit as st
from datetime import datetime

# --------------------------- #
# Page & App Meta
# --------------------------- #
st.set_page_config(
    page_title="Ethical Cybersecurity Decision Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🛡️ Ethical Cybersecurity Decision Tool")
st.caption("Real‑time, context‑sensitive support for municipal cybersecurity decision‑making")

# --------------------------- #
# Lightweight knowledge base (rule-based)
# --------------------------- #

NIST_FUNCTIONS = ["Identify", "Protect", "Detect", "Respond", "Recover"]

# NIST CSF 2.0 quick map: common municipal actions → functions (simplified)
NIST_PLAYBOOK = {
    "Disable affected services": ["Respond", "Protect"],
    "Isolate compromised segment/VLAN": ["Respond", "Protect", "Identify"],
    "Apply emergency patch/workaround": ["Protect", "Respond"],
    "Restore from backups": ["Recover", "Respond"],
    "Notify law enforcement": ["Respond", "Identify"],
    "Public comms (press/FAQ/status)": ["Respond", "Recover"],
    "Increase monitoring (EDR/SIEM rules)": ["Detect", "Respond"],
    "Access controls / least privilege update": ["Protect", "Identify"],
    "Conduct privacy impact assessment (PIA)": ["Identify", "Protect"],
    "Tabletop/after‑action review": ["Recover", "Identify"]
}

# Principlist prompts shown to user
PRINCIPLES = [
    ("Beneficence", "Promote public well‑being and service continuity."),
    ("Non‑maleficence", "Avoid or minimize harm to people/systems."),
    ("Autonomy", "Respect individuals’ rights and informed choices."),
    ("Justice", "Distribute burdens/benefits fairly; avoid disparate impact."),
    ("Explicability", "Be transparent, understandable, and accountable.")
]

# Institutional/governance constraint buckets used in your thesis
CONSTRAINT_BUCKETS = [
    "Limited budget/funding",
    "Staffing shortages",
    "Fragmented authority (inter‑dept)",
    "Vendor/contractual limits",
    "Legal/policy constraints",
    "Political/public pressure",
    "Legacy/technical debt"
]

# Keyword heuristics to auto-suggest fields based on incident text
KEYWORDS = {
    "ransomware": {
        "nist": ["Identify", "Protect", "Detect", "Respond", "Recover"],
        "values": ["Trust", "Transparency", "Safety", "Equity", "Autonomy"],
        "stakeholders": ["Residents", "City Employees", "Vendors", "City Council", "Media"],
        "constraints": ["Limited budget/funding", "Staffing shortages", "Legacy/technical debt", "Political/public pressure"]
    },
    "email outage": {
        "nist": ["Detect", "Respond", "Recover"],
        "values": ["Transparency", "Trust"],
        "stakeholders": ["City Employees", "Residents"],
        "constraints": ["Staffing shortages", "Legacy/technical debt"]
    },
    "surveillance": {
        "nist": ["Identify", "Protect", "Respond"],
        "values": ["Privacy", "Transparency", "Autonomy", "Equity", "Trust"],
        "stakeholders": ["Residents", "City Council", "Media"],
        "constraints": ["Legal/policy constraints", "Fragmented authority (inter‑dept)", "Political/public pressure", "Vendor/contractual limits"]
    },
    "streetlight": {
        "nist": ["Identify", "Protect", "Respond"],
        "values": ["Privacy", "Transparency", "Trust", "Equity", "Autonomy"],
        "stakeholders": ["Residents", "City Council", "Vendors", "Media"],
        "constraints": ["Vendor/contractual limits", "Fragmented authority (inter‑dept)", "Legal/policy constraints"]
    },
    "water treatment": {
        "nist": ["Identify", "Protect", "Detect", "Respond", "Recover"],
        "values": ["Safety", "Trust", "Transparency", "Equity"],
        "stakeholders": ["Residents", "City Employees", "City Council"],
        "constraints": ["Vendor/contractual limits", "Legal/policy constraints", "Staffing shortages", "Legacy/technical debt"]
    },
    "ai": {
        "nist": ["Identify", "Protect", "Detect", "Respond", "Recover"],
        "values": ["Explicability", "Autonomy", "Safety", "Trust", "Equity", "Transparency"],
        "stakeholders": ["Residents", "City Council", "Vendors", "Media"],
        "constraints": ["Vendor/contractual limits", "Legal/policy constraints", "Fragmented authority (inter‑dept)"]
    }
}

def suggest_from_description(text: str):
    """Return auto-suggestions for NIST, values, stakeholders, and constraints based on simple keywords."""
    text_lc = (text or "").lower()
    nist, values, stakeholders, constraints = set(), set(), set(), set()
    for key, payload in KEYWORDS.items():
        if key in text_lc:
            nist.update(payload["nist"])
            values.update(payload["values"])
            stakeholders.update(payload["stakeholders"])
            constraints.update(payload["constraints"])
    return sorted(nist), sorted(values), sorted(stakeholders), sorted(constraints)

# Value cluster quick-tags (from your lit review) to detect ethical tensions
VALUE_CLASH_RULES = [
    ("Privacy ↔ Transparency", ["surveillance", "camera", "footage", "open data"]),
    ("Safety/Beneficence ↔ Autonomy", ["forced", "mandate", "automated", "shutdown", "block"]),
    ("Justice/Equity ↔ Security", ["over-policing", "biased", "minority", "disparate", "equity"]),
    ("Non‑maleficence ↔ Beneficence", ["ransomware", "outage", "service disruption"]),
    ("Explicability ↔ Speed", ["black box", "opaque", "ai", "autonomous"])
]

def infer_tensions(text: str):
    tensions = []
    tlc = (text or "").lower()
    for label, terms in VALUE_CLASH_RULES:
        if any(t in tlc for t in terms):
            tensions.append(label)
    return sorted(set(tensions))

# --------------------------- #
# Sidebar: Modes & Presets
# --------------------------- #
st.sidebar.header("Modes & Presets")

mode = st.sidebar.radio("Mode", ["Rapid Triage", "Deliberate Review"], index=0)

preset = st.sidebar.selectbox(
    "Load preset (optional)",
    [
        "— None —",
        "2019 Baltimore (ransomware)",
        "2016 San Diego (smart streetlights)",
        "Riverton hypothetical (AI-ICS)"
    ],
    index=0
)

# Seed fields from presets
incident_type = "Other"
incident_description_seed = ""
if preset == "2019 Baltimore (ransomware)":
    incident_type = "Ransomware"
    incident_description_seed = (
        "City systems encrypted (RobbinHood). Email offline, billing disrupted, property transactions delayed. "
        "Considering ransom refusal; balancing service restoration, public trust, and law enforcement guidance."
    )
elif preset == "2016 San Diego (smart streetlights)":
    incident_type = "Unauthorized Access"
    incident_description_seed = (
        "City IoT streetlight sensors repurposed for police investigations without prior transparency or policy. "
        "Public backlash on privacy, equity, and democratic oversight; governance gaps across departments."
    )
elif preset == "Riverton hypothetical (AI-ICS)":
    incident_type = "Unauthorized Access"
    incident_description_seed = (
        "AI-based monitoring on water treatment initiated automated countermeasures, disrupting water distribution. "
        "Possible adversarial ML via vendor update; need to decide whether to disable AI or retrain under pressure."
    )

# --------------------------- #
# 1) Incident Overview
# --------------------------- #
st.subheader("🚨 1) Incident Overview")
colA, colB = st.columns([1,2])
with colA:
    incident_type = st.selectbox(
        "Type of cybersecurity incident",
        ["Phishing Attack", "Ransomware", "Unauthorized Access", "Data Breach", "Other"],
        index=(["Phishing Attack","Ransomware","Unauthorized Access","Data Breach","Other"].index(incident_type)
               if incident_type in ["Phishing Attack","Ransomware","Unauthorized Access","Data Breach","Other"] else 4)
    )
with colB:
    incident_description = st.text_area(
        "Briefly describe the incident",
        value=incident_description_seed,
        placeholder="What happened, what’s impacted, immediate constraints..."
    )

with st.expander("🧭 NIST CSF 2.0 refresher"):
    st.markdown(
        "- **Identify** – Understand risks to systems, assets, data, and capabilities.\n"
        "- **Protect** – Implement safeguards to ensure service delivery.\n"
        "- **Detect** – Discover cybersecurity events quickly.\n"
        "- **Respond** – Take action regarding a detected event.\n"
        "- **Recover** – Restore capabilities and services."
    )

# Auto-suggest based on description
auto_nist, auto_values, auto_stakeholders, auto_constraints = suggest_from_description(incident_description)
auto_tensions = infer_tensions(incident_description)

st.markdown("### ⚙️ Auto‑suggestions (from incident description)")
c1, c2, c3 = st.columns(3)
with c1:
    nist_functions = st.multiselect("Suggested NIST functions", NIST_FUNCTIONS, default=auto_nist)
with c2:
    stakeholders = st.multiselect("Suggested stakeholders", ["Residents","City Employees","Vendors","City Council","Media","Others"], default=auto_stakeholders)
with c3:
    values = st.multiselect("Suggested public values at risk", ["Privacy","Transparency","Trust","Safety","Equity","Autonomy","Explicability"], default=auto_values)

# --------------------------- #
# 2) Constraints (Institutional & Governance)
# --------------------------- #
st.subheader("⚖️ 2) Institutional & Governance Constraints")
colC, colD, colE = st.columns(3)
with colC:
    budget = st.slider("Budget pressure", 0, 10, 5)
with colD:
    legal = st.slider("Legal/policy complexity", 0, 10, 5)
with colE:
    staffing = st.slider("Staffing capacity", 0, 10, 5)

constraints_selected = st.multiselect("Constraints identified", CONSTRAINT_BUCKETS, default=auto_constraints)
additional_constraints = st.text_area("Other notes (e.g., fractured authority, vendor limits, public pressure)")

# --------------------------- #
# 3) Ethical Evaluation (Principlist)
# --------------------------- #
st.subheader("🧠 3) Ethical Evaluation (Principlist Framework)")
with st.expander("Quick meanings of the five principles"):
    for name, desc in PRINCIPLES:
        st.markdown(f"- **{name}** — {desc}")

# Show auto-detected tensions up top (user can override below)
if auto_tensions:
    st.caption("Auto‑detected value tensions (from description): " + " • ".join(auto_tensions))

beneficence = st.text_area("💡 Beneficence – how does your action promote public well‑being?")
non_maleficence = st.text_area("🚫 Non‑maleficence – how does it reduce or prevent harm?")
autonomy = st.text_area("🧍 Autonomy – how are rights/choices respected?")
justice = st.text_area("⚖️ Justice – how are benefits/burdens distributed fairly?")
explicability = st.text_area("🔍 Explicability – how will you explain/justify this decision?")

# --------------------------- #
# 4) Rapid Triage vs Deliberate Review
# --------------------------- #
st.subheader("🧩 4) Select Actions & Map to NIST")
st.caption("Choose immediate actions (triage) and/or medium‑term steps (deliberate). The tool maps to NIST CSF functions.")

colF, colG = st.columns(2)
with colF:
    st.markdown("**Rapid Triage (first 60–90 mins)**")
    triage_actions = st.multiselect(
        "Pick relevant immediate actions",
        list(NIST_PLAYBOOK.keys()),
        default=[
            "Disable affected services" if incident_type in ["Ransomware","Unauthorized Access"] else "",
            "Isolate compromised segment/VLAN",
            "Notify law enforcement",
            "Public comms (press/FAQ/status)"
        ]
    )
with colG:
    st.markdown("**Deliberate Review (stabilization + early recovery)**")
    deliberate_actions = st.multiselect(
        "Pick follow‑on actions",
        list(NIST_PLAYBOOK.keys()),
        default=[
            "Restore from backups" if incident_type in ["Ransomware","Data Breach","Unauthorized Access"] else "",
            "Increase monitoring (EDR/SIEM rules)",
            "Access controls / least privilege update",
            "Conduct privacy impact assessment (PIA)",
            "Tabletop/after‑action review"
        ]
    )

def map_actions_to_nist(actions):
    out = []
    for a in actions:
        funcs = NIST_PLAYBOOK.get(a, [])
        if funcs:
            out.append(f"- {a} → " + ", ".join(funcs))
    return "\n".join(out)

triage_map = map_actions_to_nist(triage_actions)
deliberate_map = map_actions_to_nist(deliberate_actions)

# --------------------------- #
# 5) Ethical Tension Score (simple heuristic)
# --------------------------- #
def ethical_tension_score():
    constraint_score = (budget + legal + staffing) * 2
    values_score = len(values) * 5
    stakeholders_score = len(stakeholders) * 3
    empty_ethics_fields = sum(not bool(field.strip()) for field in [beneficence, non_maleficence, autonomy, justice, explicability])
    ethics_penalty = empty_ethics_fields * 5
    total = constraint_score + values_score + stakeholders_score + ethics_penalty
    return min(total, 100)

st.subheader("📈 5) Ethical Tension Score")
score = ethical_tension_score()
st.progress(score)
if score < 30:
    st.success("🟢 Low ethical tension – decision environment is relatively clear.")
elif score < 70:
    st.warning("🟠 Moderate ethical tension – document rationale carefully and validate with peers.")
else:
    st.error("🔴 High ethical tension – pause if feasible, widen consultation, and record trade‑offs explicitly.")

# --------------------------- #
# 6) Case Summary & Justification
# --------------------------- #
st.subheader("🧾 6) Generate Case Summary & Justification")

def summarize_ethics():
    lines = []
    for name, _desc in PRINCIPLES:
        val = {
            "Beneficence": beneficence,
            "Non‑maleficence": non_maleficence,
            "Autonomy": autonomy,
            "Justice": justice,
            "Explicability": explicability
        }.get(name, "")
        if val.strip():
            lines.append(f"- **{name}**: {val.strip()}")
    return "\n".join(lines) if lines else "_(No principlist notes entered)_"

if st.button("🧠 Create Justification"):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    nist_applied = ", ".join(nist_functions) if nist_functions else "—"
    stakeholders_str = ", ".join(stakeholders) if stakeholders else "—"
    values_str = ", ".join(values) if values else "—"
    constraints_str = ", ".join(constraints_selected) if constraints_selected else "—"
    tensions_str = " • ".join(auto_tensions) if auto_tensions else "—"

    triage_block = triage_map if triage_map else "—"
    deliberate_block = deliberate_map if deliberate_map else "—"

    ethical_block = summarize_ethics()

    result = f"""# Ethical Decision Justification
Generated: {timestamp}

## Incident
- **Type:** {incident_type}
- **Description:** {incident_description.strip() or "—"}
- **Auto‑detected value tensions:** {tensions_str}

## NIST CSF 2.0 Functions Applied
- {nist_applied}

## Stakeholders & Public Values
- **Stakeholders:** {stakeholders_str}
- **Values at Risk:** {values_str}

## Institutional & Governance Constraints
- {constraints_str}
- **Sliders:** Budget={budget}/10 | Legal/Policy={legal}/10 | Staffing={staffing}/10
- **Notes:** {additional_constraints.strip() or "—"}

## Ethical Evaluation (Principlist)
{ethical_block}

## Actions Chosen & NIST Mapping
**Rapid Triage**
{triage_block}

**Deliberate Review**
{deliberate_block}

## Ethical Tension Score
- **Score:** {score}/100
- **Interpretation:** {"Low" if score<30 else "Moderate" if score<70 else "High"}

_(This justification integrates principlist reasoning with NIST CSF guidance while documenting institutional and governance constraints consistent with municipal practice.)_
"""
    st.success("✅ Justification generated below.")
    st.markdown(result)

    st.download_button(
        label="📄 Download Justification (.txt)",
        data=result,
        file_name="ethical_justification.txt",
        mime="text/plain"
    )

# --------------------------- #
# 7) About / Method note
# --------------------------- #
with st.expander("ℹ️ About this tool & method note"):
    st.markdown("""
This tool uses a **principlist ethics lens** (beneficence, non‑maleficence, autonomy, justice, explicability),
ties choices to **NIST CSF 2.0** functions, and surfaces **institutional/governance constraints** commonly found in
municipal contexts (budget, staffing, fragmented authority, vendor/legal limits, political pressure, and technical debt).

Auto‑suggestions are **rule‑based** to stay fast and offline-ready. They are prompts—not prescriptions.  
For high‑tension scores, widen consultation and document trade‑offs explicitly.
""")
