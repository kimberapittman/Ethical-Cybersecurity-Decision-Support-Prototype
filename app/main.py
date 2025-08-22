import streamlit as st
from datetime import datetime

# Set page layout
st.set_page_config(
    page_title="Ethical Cybersecurity Decision Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- HEADER ----
st.title("What’s Secure Isn’t Always What’s Right")
st.subheader("Designing a Decision-Support Prototype for Municipal Cybersecurity Practitioners")

# ---- ABOUT THE PROTOTYPE ----
st.markdown("""
This interactive tool is designed to demonstrate how ethical and technical frameworks can guide decision-making in complex municipal cybersecurity scenarios. The goal is to show how structured ethical reasoning can work alongside technical standards to navigate trade-offs, justify decisions, and document rationale. It is built around three illustrative case studies used in a thesis project.
""")

# ---- BACKBONE + CONTEXT ----
with st.expander("📚 Prototype Backbone & Context"):
    st.markdown("""
    - **Frameworks Used**:
        - [NIST Cybersecurity Framework (CSF)](https://www.nist.gov/cyberframework): A widely adopted technical risk management standard.
        - Principlist Framework for Cybersecurity Ethics: A normative tool emphasizing four ethical principles—Respect for Autonomy, Nonmaleficence, Beneficence, and Justice.
    - **Design Goal**: Provide structured guidance without prescribing outcomes. The tool surfaces ethical tensions and institutional constraints to help users reach morally defensible, context-aware decisions.
    """)

# ---- SCENARIO SELECTION ----
st.sidebar.header("Select a Scenario")
scenario = st.sidebar.selectbox("Choose one of the illustrative thesis cases:", [
    "2019 Baltimore Ransomware Attack",
    "San Diego Smart Streetlights",
    "Hypothetical: Workforce Monitoring in a Municipal IT Department"
])

# ---- SECTION 1: INCIDENT OVERVIEW ----
st.header("1. Incident Overview")

# Auto-filled summaries for each scenario
scenario_summaries = {
    "2019 Baltimore Ransomware Attack": """In May 2019, Baltimore’s government systems were paralyzed by a ransomware attack. The attack halted email access and disrupted real estate transactions, water billing, and more. The city refused to pay the ransom, leading to extended downtime and an estimated $18 million in recovery costs.""",
    "San Diego Smart Streetlights": """San Diego installed smart streetlights equipped with surveillance technology, initially justified for energy savings and traffic monitoring. Over time, concerns grew around lack of public input, transparency, and potential misuse of surveillance data by law enforcement.""",
    "Hypothetical: Workforce Monitoring in a Municipal IT Department": """A city IT department implements new software that quietly tracks employee activity for cybersecurity monitoring. The deployment occurs without informing staff, raising ethical concerns around consent, autonomy, and trust within a constrained institutional environment."""
}

st.markdown(f"**Scenario Summary:**\n\n{scenario_summaries[scenario]}")

# ---- SECTION 2: ETHICAL TENSIONS ----
st.header("2. Ethical Tensions")

ethical_tension = st.text_area("What are the key ethical tensions in this case?", placeholder="E.g., Autonomy vs. Security, Transparency vs. Efficiency...")

# ---- SECTION 3: NIST CSF FUNCTIONS ----
st.header("3. NIST Cybersecurity Functions")

nist_functions = st.multiselect(
    "Which NIST CSF Functions are relevant to this case?",
    ["Identify", "Protect", "Detect", "Respond", "Recover"]
)

# ---- SECTION 4: PRINCIPLIST FRAMEWORK ----
st.header("4. Principlist Framework")

principles = st.multiselect(
    "Which ethical principles apply?",
    ["Respect for Autonomy", "Nonmaleficence", "Beneficence", "Justice"]
)

# ---- SECTION 5: CONSTRAINTS ----
st.header("5. Institutional & Governance Constraints")

constraints = st.text_area("What practical constraints shape the decision?", placeholder="E.g., budget limitations, political pressure, unclear authority...")

# ---- SECTION 6: ACTION PATH ----
st.header("6. Proposed Action Path")

action_plan = st.text_area("What is your proposed course of action?", placeholder="Describe how you would proceed, balancing ethical and technical considerations...")

# ---- SECTION 7: DECISION RATIONALE ----
st.header("7. Rationale Summary")

if st.button("Generate Summary"):
    st.markdown("---")
    st.subheader("📝 Decision Summary")
    st.markdown(f"**Scenario Chosen:** {scenario}")
    st.markdown(f"**Ethical Tensions Identified:** {ethical_tension}")
    st.markdown(f"**Relevant NIST CSF Functions:** {', '.join(nist_functions)}")
    st.markdown(f"**Applied Ethical Principles:** {', '.join(principles)}")
    st.markdown(f"**Constraints Considered:** {constraints}")
