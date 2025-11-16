import streamlit as st

from logic.loaders import load_case


def render_case(case_id: str):
    case = load_case(case_id)

    st.subheader(case.get("title", case_id))
    st.caption(case.get("short_summary", ""))

    # 1. Technical Trigger
    st.header("Technical Trigger")
    st.write(case.get("technical", {}).get("trigger", "TBD"))

    # 2. Technical Decision Point
    st.header("Technical Decision Point")
    st.write(case.get("technical", {}).get("decision_point", "TBD"))

    # 3. Technical Mapping (NIST CSF)
    st.header("Technical Mapping (NIST CSF 2.0)")
    mapping = case.get("technical", {}).get("nist_csf_mapping", [])
    if mapping:
        for m in mapping:
            st.markdown(
                f"- **Function:** {m.get('function','TBD')} | "
                f"**Category:** {m.get('category','TBD')} | "
                f"**Subcategory:** {m.get('subcategory','TBD')}  \n"
                f"  _Rationale_: {m.get('rationale','TBD')}"
            )
    else:
        st.write("TBD")

    # 4. Ethical Trigger
    st.header("Ethical Trigger")
    st.write(case.get("ethical", {}).get("trigger", "TBD"))

    # 5. Ethical Tension
    st.header("Ethical Tension")
    tensions = case.get("ethical", {}).get("tensions", [])
    if tensions:
        for t in tensions:
            st.markdown(f"- {t.get('description','TBD')}")
    else:
        st.write("TBD")

    # 6. Ethical Mapping (PFCE)
    st.header("Ethical Mapping (PFCE)")
    pfce = case.get("ethical", {}).get("pfce_mapping", [])
    if pfce:
        for p in pfce:
            st.markdown(
                f"- **{p.get('principle','TBD')}** – {p.get('description','TBD')}"
            )
    else:
        st.write("TBD")

    # 7. Institutional and Governance Constraints
    st.header("Institutional and Governance Constraints")
    constraints = case.get("constraints", [])
    if constraints:
        for c in constraints:
            st.markdown(
                f"- **{c.get('type','TBD')}** – {c.get('description','TBD')}  \n"
                f"  _Effect on decision_: {c.get('effect_on_decision','TBD')}"
            )
    else:
        st.write("TBD")

    # 8. Decision Outcome and Ethical Implications
    st.header("Decision Outcome and Ethical Implications")
    outcome = case.get("decision_outcome", {})
    st.markdown(f"**Decision:** {outcome.get('decision','TBD')}")
    implications = outcome.get("ethical_implications", [])
    if implications:
        st.markdown("**Ethical Implications:**")
        for i in implications:
            st.markdown(f"- {i}")
    else:
        st.write("TBD")

