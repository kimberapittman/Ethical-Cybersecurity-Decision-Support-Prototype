import streamlit as st
import os
import sys
# 🌐 Streamlit layout config
st.set_page_config(
    page_title="Ethical Cybersecurity Decision Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
    [theme]
primaryColor = "#0A81AB"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F7FA"
textColor = "#1E1E1E"
font = "sans serif"
)
# 📁 Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logic.ethics import evaluate_ethics
from logic.nist import map_nist_functions

# 🧭 Intro
st.title("🛡️ Ethical Cybersecurity Decision Tool")

with st.expander("ℹ️ About this tool"):
    st.markdown("""
    This tool helps municipal cybersecurity professionals navigate high-stakes ethical decisions using:
    - 🧠 Principlist ethics
    - 🔐 NIST Cybersecurity Framework (CSF)
    - ⚖️ Real-world municipal constraints  
    Built for a graduate thesis at the Center for Homeland Defense and Security.
    """)

# 📌 Incident Details
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

# 👥 Stakeholders & Values
st.markdown("### 👥 2. Stakeholders & Public Values at Risk")
stakeholders = st.multiselect("Who is impacted?", [
    "Residents", "City Employees", "Vendors", "City Council", "Media", "Others"
])
values = st.multiselect("What public values are at risk?", [
    "Privacy", "Transparency", "Trust", "Safety", "Equity", "Autonomy"
])

# ⚖️ Constraints
st.markdown("### ⚖️ 3. Constraints Assessment")
col1, col2, col3 = st.columns(3)
with col1:
    budget = st.slider("💰 Budget", 0, 10, 5)
with col2:
    legal = st.slider("⚖️ Legal", 0, 10, 5)
with col3:
    staffing = st.slider("👥 Staffing", 0, 10, 5)

additional_constraints = st.text_area("Other constraint notes or political considerations:")

# 💡 Ethics
st.markdown("### 🧠 4. Ethical Evaluation")

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

# 📝 Case Summary
if st.button("🧾 Generate Case Summary"):
    st.markdown(f"""
    ### 📝 Case Summary
    - **Incident Type:** {incident_type}
    - **NIST CSF Functions:** {', '.join(nist_functions)}
    - **Stakeholders:** {', '.join(stakeholders)}
    - **Values at Risk:** {', '.join(values)}
    - **Constraints:** Budget: {budget}/10 | Legal: {legal}/10 | Staffing: {staffing}/10
    - **Notes:** {additional_constraints}
    """)

# ✅ Justification Narrative
st.markdown("### ✅ 5. Ethical Justification")

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
    - Additional Notes: {additional_constraints}  

    **Ethical Evaluation Summary:**  
    {ethical_summary}

    ✅ This decision reflects principlist ethical reasoning, aligns with the NIST Cybersecurity Framework, and accounts for municipal constraints.
    """
    st.success("✅ Justification generated!")
    st.markdown(result)

    # Export as TXT
    st.download_button(
        label="📄 Download Justification as .txt",
        data=result,
        file_name="ethical_justification.txt",
        mime="text/plain"
    )
