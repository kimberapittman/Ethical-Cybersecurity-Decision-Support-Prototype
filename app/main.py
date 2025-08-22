import streamlit as st

# Define the scenario summaries
scenario_summaries = {
    "Baltimore Ransomware (2019)": "In 2019, Baltimore’s local government suffered a ransomware attack that crippled municipal systems for weeks. Decision-makers faced urgent questions about paying the ransom, communicating with the public, and balancing service continuity with long-term security implications.",
    "San Diego Smart Streetlights": "San Diego implemented a smart streetlight program intended for traffic and environmental monitoring. When law enforcement began using the sensors for surveillance without clear public oversight, ethical concerns about transparency, consent, and mission creep arose.",
    "Hypothetical Workforce Monitoring Case": "A fictional city IT department considers deploying AI-based monitoring software on employee devices to detect insider threats. Ethical tensions arise around privacy, informed consent, and balancing security with employee rights."
}

# Set page configuration
st.set_page_config(
    page_title="Ethical Cybersecurity Decision Prototype",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and subtitle
st.title("What’s Secure Isn’t Always What’s Right")
st.subheader("A Decision-Support Prototype for Municipal Cybersecurity Practitioners")

# About section
st.markdown("""
### About the Prototype
This prototype demonstrates how a decision-support tool could guide municipal cybersecurity practitioners through ethically and technically complex scenarios. It is not intended to prescribe answers but to illuminate value tensions, relevant standards, and contextual constraints using structured, real-world case reconstructions. Each scenario is drawn from thesis case studies and showcases how ethical reasoning and the NIST Cybersecurity Framework can inform decision-making in high-stakes environments.
""")

# Select scenario
scenario = st.selectbox(
    "Choose a Municipal Cybersecurity Scenario",
    options=list(scenario_summaries.keys())
)

# Auto-display scenario summary
st.markdown(f"**Scenario Overview:** {scenario_summaries[scenario]}")

# Ethical Tensions section
st.markdown("### Ethical Tensions")
ethical_tensions = st.multiselect(
    "Select the relevant ethical tensions present in this scenario:",
    [
        "Privacy vs. Security",
        "Transparency vs. Confidentiality",
        "Autonomy vs. Oversight",
        "Public Trust vs. Operational Necessity",
        "Fairness vs. Efficiency",
        "Short-Term Action vs. Long-Term Risk"
    ]
)

# Institutional & Governance Constraints
st.markdown("### Institutional & Governance Constraints")
constraints = st.multiselect(
    "Which constraints affect decision-making in this case?",
    [
        "Budget limitations",
        "Legal ambiguity",
        "Time pressure",
        "Fragmented authority",
        "Public scrutiny",
        "Vendor dependence"
    ]
)

# NIST CSF Functions
st.markdown("### NIST Cybersecurity Framework (CSF) Functions")
nist_functions = st.multiselect(
    "Which NIST functions apply here?",
    ["Identify", "Protect", "Detect", "Respond", "Recover"]
)

# Ethical Principles
st.markdown("### Principlist Ethical Framework")
principles = st.multiselect(
    "Which ethical principles are most relevant?",
    ["Respect for Autonomy", "Non-Maleficence", "Beneficence", "Justice", "Explicability"]
)

# Action plan input
st.markdown("### Action Plan")
action_plan = st.text_area(
    "Describe your recommended path forward:",
    placeholder="Outline a response that balances ethical concerns and technical standards."
)

# Decision rationale generator
if st.button("Generate Decision Record"):
    st.markdown("---")
    st.markdown("## 📘 Decision Summary")
    st.markdown(f"**Scenario Chosen:** {scenario}")
    st.markdown(f"**Scenario Summary:** {scenario_summaries[scenario]}")
    st.markdown(f"**Ethical Tensions Identified:** {', '.join(ethical_tensions) if ethical_tensions else 'None selected'}")
    st.markdown(f"**Constraints Present:** {', '.join(constraints) if constraints else 'None selected'}")
    st.markdown(f"**NIST Functions Referenced:** {', '.join(nist_functions) if nist_functions else 'None selected'}")
    st.markdown(f"**Ethical Principles Applied:** {', '.join(principles) if principles else 'None selected'}")
    st.markdown("**Proposed Action Plan:**")
    st.write(action_plan if action_plan else "No action plan provided.")

# Footer
st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes – not for operational use.")
