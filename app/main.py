import streamlit as st
import os
import sys

# Set page layout
st.set_page_config(
    page_title="Ethical Cybersecurity Decision Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logic.ethics import evaluate_ethics
from logic.nist import map_nist_functions

# CHDS logo (hosted externally)
st.image("https://i.imgur.com/1R7nuZ2.jpeg", use_container_width=True)
st.caption("Center for Homeland Defense and Security")

# Title and real-time use subtitle
st.title("🛡️ Ethical Cybersecurity Decision Tool")
st.markdown("#### A real-time ethical decision-support tool for municipal cybersecurity professionals")

# Updated about section to emphasize live decision-making
with st.expander("ℹ️ About this tool"):
    st.markdown("""
    This tool is designed to assist **real-time ethical decision-making** during municipal cybersecurity incidents.

    It helps professionals:
    - Assess stakeholder and public value impacts
    - Reflect on ethical principles under time pressure
    - Align actions with NIST CSF standards
    - Justify decisions transparently and defensibly

    Built to support municipal IT leaders **during live response**, not just after-action review.
    """)

# 1. Incident Overview
st.markdown("### 🚨 1. Incident Overview")
incident_type = st.selectbox("Type of Cybersecurity Incident", [
    "Phishing Attack", "Ransomware", "Unauthorized Access", "Data Breach", "Other"
])

with st.expander("🧭 What are NIST CSF functions?"):
    st.markdown("""
- **Identify** – Understand risks to systems, assets, data.
- **Protect** – Safeguard delivery of critical services.
- **Detect** – Discover cybersecurity events.
- **Respond** – Act on detected incidents.
- **Recover** – Restore systems and services.
""")

nist_functions = st.multiselect("NIST CSF Functions Involved", [
    "Identify", "Protect", "Detect", "Respond", "Recover"
])
incident_description = st.text_area("Briefly describe the incident:")

# 2. Stakeholders and Values
st.markdown("### 👥 2. Stakeholders & Public Values at Risk")
stakeholders = st.multiselect("Who is impacted?", [
    "Residents", "City Employees", "Vendors", "City Council", "Media", "Others"
])
values = st.multiselect("What public values are at risk?", [
    "Privacy", "Transparency", "Trust", "Safety", "Equity", "Autonomy"
])

# 3. Constraints
st.markdown("### ⚖️ 3. Constraints Assessment")
col1, col2, col3 = st.columns(3)
with col1:
    budget = st.slider("💰 Budget", 0, 10, 5)
with col2:
    legal = st.slider("⚖️ Legal", 0, 10, 5)
with col3:
    staffing = st.slider("👥 Staffing", 0, 10, 5)

additional_constraints = st.text_area("Other constraint notes or political considerations:")

# 4. Ethical Evaluation
st.markdown("### 🧠 4. Ethical Evaluation (Principlist Framework)")
with st.expander("🧭 What do these principles mean?"):
    st.markdown("""
- **Beneficence** – Promote well-being and good outcomes.  
- **Non-maleficence** – Avoid harm.  
- **Autonomy** – Respect individual rights and choices.  
- **Justice** – Ensure fairness and equity.  
- **Explicability** – Be transparent and accountable.
""")

beneficence = st.text_area("💡 Beneficence – How does this action promote good?")
non_maleficence = st.text_area("🚫 Non-maleficence – How does it avoid harm?")
autonomy = st.text_area("🧍 Autonomy – Are rights and choices respected?")
justice = st.text_area("⚖️ Justice – Are burdens/benefits fairly distributed?")
explicability = st.text_area("🔍 Explicability – Can the decision be clearly explained?")

# 5. Ethical Tension Score
def calculate_ethics_tension():
    constraint_score = (budget + legal + staffing) * 2
    values_score = len(values) * 5
    stakeholder_score = len(stakeholders) * 3
    empty_ethics_fields = sum(not bool(field.strip()) for field in [
        beneficence, non_maleficence, autonomy, justice, explicability])
    ethics_penalty = empty_ethics_fields * 5
    total_score = constraint_score + values_score + stakeholder_score + ethics_penalty
    return min(total_score, 100)

st.markdown("### 🔍 5. Ethical Tension Score")
score = calculate_ethics_tension()
st.progress(score)

if score < 30:
    st.success("🟢 Low ethical tension – decision environment is relatively clear.")
elif score < 70:
    st.warning("🟠 Moderate ethical tension – consider documenting your justification carefully.")
else:
    st.error("🔴 High ethical tension – review stakeholder impacts and public values closely.")

# 6. Case Summary
if st.button("🧾 Generate Case Summary"):
    summary = f"""
    ### 📝 Case Summary
    - **Incident Type:** {incident_type}
    - **NIST CSF Functions:** {', '.join(nist_functions)}
    - **Stakeholders:** {', '.join(stakeholders)}
    - **Values at Risk:** {', '.join(values)}
    - **Constraints:** Budget: {budget}/10 | Legal: {legal}/10 | Staffing: {staffing}/10
    - **Notes:** {additional_constraints}
    """
    st.markdown(summary)

# 7. Justification Narrative with real-time intent
st.markdown("### ✅ 6. Ethical Justification")

if st.button("📄 Confirm & Justify Action"):
    ethical_summary = evaluate_ethics(
        beneficence, non_maleficence, autonomy, justice, explicability
    )
    nist_summary = map_nist_functions(nist_functions)

    result = f"""
    ## Justification Narrative

    **Incident Type:** {incident_type}  
    **NIST CSF Functions Applied:** {nist_summary}  
    **Incident Description:** {incident_description}  

    **Stakeholders Impacted:** {", ".join(stakeholders)}  
    **Public Values at Risk:** {", ".join(values)}  

    **Constraints Considered:**  
    - Budget: {budget}/10  
    - Legal: {legal}/10  
    - Staffing: {staffing}/10  
    - Notes: {additional_constraints}  

    **Ethical Evaluation Summary:**  
    {ethical_summary}

    ✅ This decision reflects principlist ethical reasoning, aligns with the NIST Cybersecurity Framework, and accounts for institutional constraints common in municipal environments.
    """
    st.success("✅ Justification generated!")
    st.markdown(result)

    st.download_button(
        label="📄 Download Justification as .txt",
        data=result,
        file_name="ethical_justification.txt",
        mime="text/plain"
    )
