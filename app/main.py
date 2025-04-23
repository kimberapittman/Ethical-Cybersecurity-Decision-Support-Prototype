import streamlit as st
import os  # 👈 add this if not already imported

st.write("🔍 Current working directory:", os.getcwd())  # 👈 DEBUG LINE

import streamlit as st
from logic.ethics import evaluate_ethics
from logic.nist import map_nist_functions

st.set_page_config(page_title="Ethical Cybersecurity Decision Tool", layout="wide")
st.title("🛡️ Ethical Decision-Support Tool for Municipal Cybersecurity")

st.header("1. Incident Overview")
incident_type = st.selectbox("Select the type of cybersecurity incident:", [
    "Phishing Attack", "Ransomware", "Unauthorized Access", "Data Breach", "Other"
])
nist_functions = st.multiselect("Select NIST CSF functions involved:", [
    "Identify", "Protect", "Detect", "Respond", "Recover"
])
incident_description = st.text_area("Describe the incident briefly:")

st.header("2. Stakeholders & Public Values at Risk")
stakeholders = st.multiselect("Who is impacted?", [
    "Residents", "City Employees", "Vendors", "City Council", "Media", "Others"
])
values = st.multiselect("What public values are at risk?", [
    "Privacy", "Transparency", "Trust", "Safety", "Equity", "Autonomy"
])

st.header("3. Constraints Assessment")
budget = st.slider("Budget Constraint", 0, 10, 5)
legal = st.slider("Legal/Regulatory Constraint", 0, 10, 5)
staffing = st.slider("Staffing Constraint", 0, 10, 5)
additional_constraints = st.text_area("Additional notes on constraints:")

st.header("4. Ethical Evaluation (Principlist Framework)")
beneficence = st.text_area("Beneficence – How does this action promote good?")
non_maleficence = st.text_area("Non-maleficence – How does it avoid harm?")
autonomy = st.text_area("Autonomy – Are rights and choices respected?")
justice = st.text_area("Justice – Are burdens and benefits fairly distributed?")
explicability = st.text_area("Explicability – Can the decision be clearly explained?")

st.header("5. Generate Ethical Justification")

if st.button("Generate Justification Narrative"):
    ethical_summary = evaluate_ethics(beneficence, non_maleficence, autonomy, justice, explicability)
    nist_summary = map_nist_functions(nist_functions)

    result = f"""
    ## Justification Narrative

    **Incident Type:** {incident_type}  
    **NIST CSF Functions:** {nist_summary}  
    **Description:** {incident_description}  

    **Stakeholders Impacted:** {", ".join(stakeholders)}  
    **Public Values at Risk:** {", ".join(values)}  

    **Constraints:**  
    - Budget: {budget}/10  
    - Legal: {legal}/10  
    - Staffing: {staffing}/10  
    - Notes: {additional_constraints}  

    **Ethical Evaluation:**  
    {ethical_summary}

    ✅ This decision reflects principlist ethical reasoning, aligns with NIST CSF, and considers real-world municipal constraints.
    """
    st.markdown(result)
