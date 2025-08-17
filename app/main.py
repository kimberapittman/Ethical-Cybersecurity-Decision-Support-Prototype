import streamlit as st
import os
import sys
from datetime import datetime

# ------------------------------
# Page & imports
# ------------------------------
st.set_page_config(
    page_title="Ethical Cybersecurity Decision Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Optional local imports (with safe fallbacks)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from logic.ethics import evaluate_ethics as _evaluate_ethics_external
except Exception:
    _evaluate_ethics_external = None

try:
    from logic.nist import map_nist_functions as _map_nist_functions_external
except Exception:
    _map_nist_functions_external = None

def evaluate_ethics_fallback(beneficence, non_maleficence, autonomy, justice, explicability):
    parts = []
    if beneficence.strip(): parts.append(f"- Beneficence: {beneficence.strip()}")
    if non_maleficence.strip(): parts.append(f"- Non-maleficence: {non_maleficence.strip()}")
    if autonomy.strip(): parts.append(f"- Autonomy: {autonomy.strip()}")
    if justice.strip(): parts.append(f"- Justice: {justice.strip()}")
    if explicability.strip(): parts.append(f"- Explicability: {explicability.strip()}")
    return "\n".join(parts) if parts else "No ethical notes provided."

def evaluate_ethics(*args, **kwargs):
    if _evaluate_ethics_external:
        return _evaluate_ethics_external(*args, **kwargs)
    return evaluate_ethics_fallback(*args, **kwargs)

def map_nist_functions_fallback(funcs):
    if not funcs:
        return "No NIST functions selected."
    descriptions = {
        "Identify": "asset/business context, risk appetite, governance",
        "Protect": "access control, awareness/training, data security, maintenance",
        "Detect": "anomalies/events, continuous monitoring, detection processes",
        "Respond": "analysis, mitigation, communications, improvements",
        "Recover": "restoration, improvements, communications"
    }
    return "; ".join(f"{f}: {descriptions.get(f,'')}" for f in funcs)

def map_nist_functions(funcs):
    if _map_nist_functions_external:
        return _map_nist_functions_external(funcs)
    return map_nist_functions_fallback(funcs)

# ------------------------------
# Title & About
# ------------------------------
st.title("🛡️ Ethical Cybersecurity Decision Tool")
st.markdown("#### A real-time ethical decision-support tool for municipal cybersecurity practitioners")

with st.expander("ℹ️ About this tool"):
    st.markdown("""
This tool supports **live** municipal incident response by:
- Surfacing value conflicts using **Principlism** (beneficence, non-maleficence, autonomy, justice, explicability)
- Anchoring actions to **NIST CSF** (Identify, Protect, Detect, Respond, Recover)
- Making **institutional & governance constraints** explicit (budget, staffing, procurement limits, fragmented authority, oversight gaps)
- Producing a defensible **decision log** and public-facing **explicability** summary
""")

# ------------------------------
# Scenario templates (from Chapter 3)
# ------------------------------
st.markdown("### 🧩 Scenario Template (optional)")
template = st.selectbox(
    "Pre-fill from a Chapter 3 scenario (you can still edit anything):",
    ["None", "Baltimore-like: Ransomware", "San Diego-like: Surveillance Repurposing", "Riverton-like: AI-enabled Incident"]
)

# ------------------------------
# 1) Incident Overview
# ------------------------------
st.markdown("### 🚨 1) Incident Overview")

incident_type = st.selectbox("Type of Cybersecurity Incident", [
    "Ransomware", "Data Breach", "Unauthorized Access", "Phishing Attack",
    "Surveillance Technology Repurposing", "AI-enabled Operational Disruption", "Other"
])

colA, colB = st.columns([2,1])
with colA:
    incident_description = st.text_area("Briefly describe the incident:")
with colB:
    timestamp = st.text_input("Incident time (optional)", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))

with st.expander("🧭 What are NIST CSF functions?"):
    st.markdown("""
- **Identify** – Understand risks to systems, assets, data, and capabilities  
- **Protect** – Safeguard delivery of critical services  
- **Detect** – Discover cybersecurity events  
- **Respond** – Act on detected incidents  
- **Recover** – Restore systems and services  
""")

nist_functions = st.multiselect("NIST CSF Functions in scope", [
    "Identify", "Protect", "Detect", "Respond", "Recover"
])

# ------------------------------
# 2) Stakeholders & Public Values
# ------------------------------
st.markdown("### 👥 2) Stakeholders & Public Values")
stakeholders = st.multiselect("Who is impacted?", [
    "Residents", "City Employees", "Vendors", "City Council",
    "Emergency Services", "Public Utilities", "Law Enforcement", "Media", "Other"
])
values = st.multiselect("Public values at risk", [
    "Privacy", "Transparency", "Trust", "Safety", "Equity", "Autonomy", "Accountability"
])

# ------------------------------
# 3) Institutional & Governance Constraints
# ------------------------------
st.markdown("### 🏛️ 3) Institutional & Governance Constraints")

st.caption("Select all that apply (these reflect constraints emphasized in Chapter 3).")
constraints_col1, constraints_col2, constraints_col3 = st.columns(3)
with constraints_col1:
    c_budget = st.checkbox("Constrained budget / deferred modernization")
    c_staffing = st.checkbox("Limited staffing / coverage")
    c_fragmented = st.checkbox("Fragmented authority / unclear ownership")
    c_continuity = st.checkbox("No/weak incident-specific continuity plan")
with constraints_col2:
    c_procurement = st.checkbox("Procurement opacity / general contracts")
    c_oversight = st.checkbox("Weak or absent oversight mechanisms")
    c_policy_gap = st.checkbox("No formal policy (e.g., surveillance access)")
    c_vendor_opacity = st.checkbox("Contractual opacity (limited vendor auditability)")
with constraints_col3:
    c_public_engage = st.checkbox("Limited public engagement / transparency")
    c_data_gov = st.checkbox("Unclear data governance (sharing/retention)")
    c_legal = st.checkbox("Legal/political constraints")
    c_other_note_active = st.checkbox("Other (add notes below)")

constraint_notes = st.text_area("Notes on constraints (e.g., departments affected, specific contract clauses, political context):")

# ------------------------------
# 4) Ethical Evaluation (Principlism)
# ------------------------------
st.markdown("### 🧠 4) Ethical Evaluation (Principlist Framework)")
with st.expander("What do these principles mean?"):
    st.markdown("""
- **Beneficence** – Promote well-being (e.g., restore essential services, improve safety)  
- **Non-maleficence** – Avoid harm (e.g., prevent secondary impacts, avoid unsafe mitigations)  
- **Autonomy** – Respect rights & choices (e.g., privacy, informed consent where applicable)  
- **Justice** – Fairness & equity (e.g., avoid disproportionate burdens on communities)  
- **Explicability** – Transparency & intelligibility (clear rationale, communication, auditability)
""")

beneficence = st.text_area("💡 Beneficence – What good outcomes are you prioritizing?")
non_maleficence = st.text_area("🚫 Non-maleficence – What harms are you avoiding/minimizing?")
autonomy = st.text_area("🧍 Autonomy – How are rights/choices respected (incl. privacy)?")
justice = st.text_area("⚖️ Justice – How are burdens/benefits distributed fairly?")
explicability = st.text_area("🔍 Explicability – How will the decision be communicated and made auditable?")

# ------------------------------
# 5) Principle Trade-off Matrix (quick tension scan)
# ------------------------------
st.markdown("### ⚖️ 5) Principle Trade-off Matrix")
st.caption("Rate the *pressure* each principle is under in this incident (0 = none, 10 = extreme).")
t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns(5)
with t_col1:
    t_ben = st.slider("Beneficence", 0, 10, 5)
with t_col2:
    t_non = st.slider("Non-maleficence", 0, 10, 5)
with t_col3:
    t_aut = st.slider("Autonomy", 0, 10, 5)
with t_col4:
    t_jus = st.slider("Justice", 0, 10, 5)
with t_col5:
    t_exp = st.slider("Explicability", 0, 10, 5)

tension_vector = {
    "Beneficence": t_ben,
    "Non-maleficence": t_non,
    "Autonomy": t_aut,
    "Justice": t_jus,
    "Explicability": t_exp
}

# ------------------------------
# 6) Constraints intensity (quick sliders for 3 core pressures)
# ------------------------------
st.markdown("### 🧱 6) Core Constraint Pressures")
cc1, cc2, cc3 = st.columns(3)
with cc1:
    budget_int = st.slider("💰 Budget pressure", 0, 10, 5)
with cc2:
    legal_int = st.slider("⚖️ Legal/policy pressure", 0, 10, 5)
with cc3:
    staffing_int = st.slider("👥 Staffing/ops pressure", 0, 10, 5)

# ------------------------------
# 7) Decision Options (contextual)
# ------------------------------
st.markdown("### 🧭 7) Candidate Decision Options")

def options_for_incident(inc_type):
    if inc_type == "Ransomware":
        return [
            "Refuse ransom; pursue restore/recover; communicate timeline",
            "Consider controlled negotiation for decryption key with law enforcement guidance",
            "Segment & rebuild critical services first; defer non-critical",
            "Public outage dashboard + staged restoration plan"
        ]
    if inc_type == "Surveillance Technology Repurposing":
        return [
            "Pause access; conduct rapid DPIA (Data Protection Impact Assessment)",
            "Establish interim oversight & access log review; narrow use-cases",
            "Community disclosure + council review before resumption",
            "Data minimization & retention limits; publish policy"
        ]
    if inc_type == "AI-enabled Operational Disruption":
        return [
            "Fail-safe to human control; isolate/rollback AI model",
            "Independent audit of vendor model & training data",
            "Staged service restoration with enhanced monitoring",
            "Public advisory on risks, mitigations, and timelines"
        ]
    # Generic defaults:
    return [
        "Containment & triage aligned to NIST Respond/Recover",
        "Stakeholder communication plan (Explicability)",
        "Interim governance/oversight measures",
        "Documented rationale & after-action improvements"
    ]

suggested_options = options_for_incident(incident_type)
picked_options = st.multiselect("Select one or more options to justify:", suggested_options, default=suggested_options[:2])
custom_option = st.text_input("Add a custom option (optional):")
if custom_option:
    picked_options.append(custom_option)

# ------------------------------
# 8) Ethical Tension Score (simple, explainable)
# ------------------------------
st.markdown("### 🔍 8) Ethical Tension Score (quick heuristic)")
def calculate_ethics_tension():
    constraint_score = (budget_int + legal_int + staffing_int) * 2
    values_score = len(values) * 4
    stakeholder_score = len(stakeholders) * 2
    pressure_score = sum(tension_vector.values())  # 0–50
    text_fields_empty = sum(not bool(x.strip()) for x in [
        beneficence, non_maleficence, autonomy, justice, explicability
    ]) * 4
    total = constraint_score + values_score + stakeholder_score + pressure_score + text_fields_empty
    return max(0, min(total, 100))

score = calculate_ethics_tension()
st.progress(score)
if score < 30:
    st.success("🟢 Low ethical tension – decision environment is relatively clear.")
elif score < 70:
    st.warning("🟠 Moderate ethical tension – document justification and mitigations.")
else:
    st.error("🔴 High ethical tension – revisit principle conflicts and constraints; consider additional oversight.")

# ------------------------------
# 9) Case Summary
# ------------------------------
if st.button("🧾 Generate Case Summary"):
    summary = f"""
### 📝 Case Summary
- **Incident Type:** {incident_type}
- **Incident Time:** {timestamp}
- **NIST CSF Functions:** {', '.join(nist_functions) if nist_functions else '—'}
- **Stakeholders:** {', '.join(stakeholders) if stakeholders else '—'}
- **Values at Risk:** {', '.join(values) if values else '—'}

**Institutional & Governance Constraints:**
- Budget:{' ✓' if c_budget else ''}  Staffing:{' ✓' if c_staffing else ''}  Fragmented Authority:{' ✓' if c_fragmented else ''}
- Continuity Gap:{' ✓' if c_continuity else ''}  Procurement Opacity:{' ✓' if c_procurement else ''}  Oversight Weakness:{' ✓' if c_oversight else ''}
- Policy Gap:{' ✓' if c_policy_gap else ''}  Vendor Opacity:{' ✓' if c_vendor_opacity else ''}  Public Engagement Limits:{' ✓' if c_public_engage else ''}
- Data Governance Unclear:{' ✓' if c_data_gov else ''}  Legal/Political Constraints:{' ✓' if c_legal else ''}
- Notes: {constraint_notes or '—'}
"""
    st.markdown(summary)

# ------------------------------
# 10) Justification & Public Comms
# ------------------------------
st.markdown("### ✅ 10) Justification & Public-Facing Explicability")

if st.button("📄 Confirm & Generate Justification"):
    nist_summary = map_nist_functions(nist_functions)
    ethical_summary = evaluate_ethics(
        beneficence, non_maleficence, autonomy, justice, explicability
    )

    chosen = "\n".join(f"- {o}" for o in picked_options) if picked_options else "—"

    # Public-facing paragraph (explicability)
    public_msg = (
        f"On {timestamp}, we experienced a {incident_type.lower()} affecting municipal services. "
        f"Our immediate priorities are safety, service continuity, and transparency. "
        f"We are acting under the NIST Cybersecurity Framework ({', '.join(nist_functions) if nist_functions else '—'}), "
        f"and we will provide regular updates as we implement the options listed below. "
        f"We are also documenting decisions for independent review and long-term improvements."
    )

    result = f"""
## Decision Justification Log

**Incident Type:** {incident_type}  
**Time:** {timestamp}  
**Incident Description:** {incident_description or '—'}

**NIST CSF Functions Applied:**  
{nist_summary}

**Stakeholders Impacted:** {", ".join(stakeholders) if stakeholders else '—'}  
**Public Values at Risk:** {", ".join(values) if values else '—'}

**Institutional & Governance Constraints (selected):**
- Budget:{' ✓' if c_budget else ''} | Staffing:{' ✓' if c_staffing else ''} | Fragmented Authority:{' ✓' if c_fragmented else ''}
- Continuity Gap:{' ✓' if c_continuity else ''} | Procurement Opacity:{' ✓' if c_procurement else ''} | Oversight Weakness:{' ✓' if c_oversight else ''}
- Policy Gap:{' ✓' if c_policy_gap else ''} | Vendor Opacity:{' ✓' if c_vendor_opacity else ''} | Public Engagement Limits:{' ✓' if c_public_engage else ''}
- Data Governance Unclear:{' ✓' if c_data_gov else ''} | Legal/Political Constraints:{' ✓' if c_legal else ''}
- Notes: {constraint_notes or '—'}

**Principlist Ethical Evaluation:**
{ethical_summary or '—'}

**Principle Pressure (0-10):** Beneficence={t_ben}, Non-maleficence={t_non}, Autonomy={t_aut}, Justice={t_jus}, Explicability={t_exp}

**Selected Options:**
{chosen}

**Ethical Tension Score:** {score}/100

**Public-Facing Summary (Explicability):**  
{public_msg}

— Generated by Ethical Cybersecurity Decision Tool
    """
    st.success("✅ Justification generated. See below and download if needed.")
    st.markdown(result)

    st.download_button(
        label="📄 Download Justification (.txt)",
        data=result,
        file_name=f"ethical_justification_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

# ------------------------------
# Prefill helper (applies after UI has loaded)
# ------------------------------
if template != "None" and not incident_description:
    # Light, non-binding prefills tuned to your Chapter 3 cases
    if template == "Baltimore-like: Ransomware":
        st.session_state["Incident Prefill"] = True
        st.info("Template loaded: Baltimore-like ransomware scenario (edit freely).")
        st.experimental_set_query_params(t="baltimore")
    elif template == "San Diego-like: Surveillance Repurposing":
        st.session_state["Incident Prefill"] = True
        st.info("Template loaded: San Diego-like surveillance repurposing (edit freely).")
        st.experimental_set_query_params(t="sandiego")
    elif template == "Riverton-like: AI-enabled Incident":
        st.session_state["Incident Prefill"] = True
        st.info("Template loaded: Riverton-like AI-enabled disruption (edit freely).")
        st.experimental_set_query_params(t="riverton")

# (Note: Query params can be used to drive deeper prefill behavior if desired.)
