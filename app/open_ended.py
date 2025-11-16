import streamlit as st
from datetime import datetime
import uuid

from logic.loaders import save_open_ended_log


def render_open_ended():
    st.subheader("Open-Ended Mode")

    meta_col1, meta_col2 = st.columns(2)
    with meta_col1:
        incident_title = st.text_input("Incident Title")
        municipality = st.text_input("Municipality / Organization (optional)")
    with meta_col2:
        role = st.text_input("Your Role")
        notes = st.text_input("Notes (optional)")

    # 1. Technical Trigger
    st.header("Technical Trigger")
    tech_trigger = st.text_area(
        "Describe the event, condition, or vulnerability that triggered this decision."
    )

    # 2. Technical Decision Point
    st.header("Technical Decision Point")
    tech_decision = st.text_area(
        "What specific technical decision must be made?"
    )

    # 3. Technical Mapping (NIST CSF)
    st.header("Technical Mapping (NIST CSF 2.0)")
    csf_functions = st.multiselect(
        "Select relevant NIST CSF functions",
        ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"],
    )
    csf_rationale = st.text_area("Why are these functions relevant?")

    # 4. Ethical Trigger
    st.header("Ethical Trigger")
    ethical_trigger = st.text_area(
        "Who or what is affected by this decision, and how?"
    )

    # 5. Ethical Tension
    st.header("Ethical Tension")
    ethical_tension = st.text_area(
        "Describe the main ethical tension in this decision."
    )

    # 6. Ethical Mapping (PFCE)
    st.header("Ethical Mapping (PFCE)")
    pfce_selected = st.multiselect(
        "Select PFCE principles involved",
        ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"],
    )
    pfce_explanation = st.text_area(
        "Explain how these principles support or challenge your decision."
    )

    # 7. Institutional and Governance Constraints
    st.header("Institutional and Governance Constraints")
    constraints_text = st.text_area(
        "List any legal, political, organizational, or resource constraints that shape your options."
    )

    # 8. Decision Outcome and Ethical Implications
    st.header("Decision Outcome and Ethical Implications")
    decision = st.text_area("What decision are you inclined to make (or did you make)?")
    rationale = st.text_area(
        "Explain your ethical reasoning, including how technical context, ethical principles, and constraints shaped this choice."
    )

    if st.button("Save Decision Log"):
        log = {
            "id": str(uuid.uuid4()),
            "mode": "open-ended",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "meta": {
                "incident_title": incident_title,
                "municipality": municipality,
                "practitioner_role": role,
                "notes": notes,
            },
            "technical": {
                "trigger": {"user_input": tech_trigger},
                "decision_point": {"user_input": tech_decision},
                "nist_csf_mapping": {
                    "selected": [{"function": f} for f in csf_functions],
                    "user_rationale": csf_rationale,
                },
            },
            "ethical": {
                "trigger": {"user_input": ethical_trigger},
                "tensions": [{"description": ethical_tension}] if ethical_tension else [],
                "pfce_mapping": {
                    "selected_principles": [
                        {"principle": p, "user_explanation": pfce_explanation}
                        for p in pfce_selected
                    ]
                },
            },
            "constraints": [
                {"type": "Uncategorized", "user_description": constraints_text}
            ]
            if constraints_text
            else [],
            "decision_outcome": {
                "decision": decision,
                "is_final": False,
                "ethical_rationale": rationale,
                "unresolved_questions": "",
            },
        }

        path = save_open_ended_log(log)
        st.success(f"Decision log saved to: {path.name}")

