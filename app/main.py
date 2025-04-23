import streamlit as st
import os
import sys

# ✅ MUST be the first Streamlit command
st.set_page_config(page_title="Ethical Cybersecurity Decision Tool", layout="wide")

# ✅ Ensure logic/ is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Import logic modules
from logic.ethics import evaluate_ethics
from logic.nist import map_nist_functions

# App title
st.title("🛡️ Ethical Decision-Support Tool for Municipal Cybersecurity")

# 1. Incident Overview
st.header("1. Incident Overview")
incident_type = st.selectbox("Select the type of cybersecurity incident:", [
    "Phishing Attack", "Ransomware", "Unauthorized Access", "Data Breach", "Other"
])

# ✅ Enhanced NIST CSF explanation
st.markdown("**Select the NIST Cybersecurity Framework (CSF) functions involved:**")
with st.expander("🧭 What do these functions mean?"):
    st.markdown("""
- **Identify**: Understand the organization to manage cybersecurity risk.
- **Protect**: Safeguard critical infrastructure services.
- **Detect**: Discover cybersecurity events in a timely manner.
- **Respond**: Take action once an event is detected.
- **Recover**: Restore capabilities or services impaired due to an incident.
""")

nist_functions = st.multiselect("Choose relevant NIST CSF functions:", [
    "Identify", "Protect", "Detect", "Respond", "Recover"
])
incident_description = st.text_area("Describe the incident briefly:")

# 2. Stakeholder and Value Mapping
st.header("2. Stakeholders & Public Values at Risk")
stakeholders = st.multiselect("Who is impacted?", [
    "Residents", "City Employees", "Vendors", "City Council", "Media", "Others"
])
values = st.multiselect("What public values are at risk?", [
    "Privacy", "Transparency", "Trust", "Safety", "Equity", "Autonomy"
])

# 3. Constraints Assessment
st.header("3. Constraints Assessment")
budget = st.slider("Budget Constraint", 0, 10, 5)
legal = st.slider("Legal/Regulatory Constraint", 0, 10, 5)
staffing = st.slider("Staffing Constraint", 0, 10, 5)
additional_constraints = st.text_area("Additional notes on constraints:")

# 4. Ethical Evaluation (with explanation)
st.header("4. Ethical Evaluation (Principlist Framework)")
with st.expander("🧭 What do these principles mean?"):
    st.markdown("""
These ethical principles are adapted from biomedical ethics and applied to cybersecurity decision-making:

- **Beneficence** – Promote public good. Ask: *Who benefits from this action?*
- **Non-maleficence** – Avoid causing harm. Ask: *Who could be negatively impacted?*
- **Autonomy** – Respect individuals' rights. Ask: *Are we respecting informed choice and consent?*
- **Justice** – Ensure fairness. Ask: *Are burdens and benefits distributed equitably?*
- **Explicability** – Ensure transparency. Ask: *Can we clearly explain this decision to the public?*
""")

beneficence = st.text_area("Beneficence – How does this action promote good?")
non_maleficence = st.text_area("Non-maleficence – How does it avoid harm?")
autonomy = st.text_area("Autonomy – Are rights and choices respected?")
justice = st.text_area("Justice – Are burdens and benefits fairly distributed?")
explicability = st.text_area("Explicability – Can the decision be clearly explained?")

# 5. Generate Ethical Justification
st.header("5. Generate Ethical Justification")

if st.button("Generate Justification Narrative"):
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
    st.markdown(result)
