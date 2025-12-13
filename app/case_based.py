import streamlit as st
from logic.loaders import load_case


# ----------------------------------------
# Safe rerun helper (mirrors open-ended)
# ----------------------------------------
def _safe_rerun():
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    except Exception:
        pass


# ----------------------------------------
# Case-Based Mode (step-by-step version)
# ----------------------------------------
def render_case(case_id: str):

    # Load case data
    case = load_case(case_id) or {}

    # Safely normalize expected sections
    case.setdefault("technical", {})
    case.setdefault("ethical", {})
    case.setdefault("constraints", [])
    case.setdefault("decision_outcome", {})

    case["technical"].setdefault("nist_csf_mapping", [])
    case["ethical"].setdefault("tensions", [])
    case["ethical"].setdefault("pfce_mapping", [])
    case["decision_outcome"].setdefault("ethical_implications", [])

    # ---------------------
    # Setup step navigation
    # ---------------------
    if "cb_step" not in st.session_state:
        st.session_state["cb_step"] = 1
    step = st.session_state["cb_step"]

    # ---------------------
    # Title + Summary
    # ---------------------


    st.subheader(case.get("title", case_id))
    st.caption(case.get("short_summary", ""))

    st.progress(step / 9.0)

    # ----------------------------------
    # STEP 1 — Technical Trigger
    # ----------------------------------
    if step == 1:
        st.header("1. Technical Trigger")
        st.write(case["technical"].get("trigger", "TBD"))
        st.markdown("---")

    # ----------------------------------
    # STEP 2 — Technical Decision Point
    # ----------------------------------
    if step == 2:
        st.header("2. Technical Decision Point")
        st.write(case["technical"].get("decision_point", "TBD"))
        st.markdown("---")

    # ----------------------------------
    # STEP 3 — Technical Mapping (NIST CSF)
    # ----------------------------------
    if step == 3:
        st.header("3. Technical Mapping (NIST CSF 2.0)")
        mapping = case["technical"].get("nist_csf_mapping", [])

        if mapping:
            for m in mapping:
                st.markdown(
                    f"- **Function:** {m.get('function','TBD')}  \n"
                    f"  **Category:** {m.get('category','TBD')}  \n"
                    f"  **Subcategory:** {m.get('subcategory','TBD')}  \n"
                    f"  _Rationale_: {m.get('rationale','TBD')}"
                )
        else:
            st.write("TBD")

        st.markdown("---")

    # ----------------------------------
    # STEP 4 — Ethical Trigger
    # ----------------------------------
    if step == 4:
        st.header("4. Ethical Trigger")
        st.write(case["ethical"].get("trigger", "TBD"))
        st.markdown("---")

    # ----------------------------------
    # STEP 5 — Ethical Tension
    # ----------------------------------
    if step == 5:
        st.header("5. Ethical Tension")
        tensions = case["ethical"].get("tensions", [])
        if tensions:
            for t in tensions:
                st.markdown(f"- {t.get('description','TBD')}")
        else:
            st.write("TBD")
        st.markdown("---")

    # ----------------------------------
    # STEP 6 — Ethical Mapping (PFCE)
    # ----------------------------------
    if step == 6:
        st.header("6. Ethical Mapping (PFCE)")
        pfce = case["ethical"].get("pfce_mapping", [])
        if pfce:
            for p in pfce:
                st.markdown(
                    f"- **{p.get('principle','TBD')}** – {p.get('description','TBD')}"
                )
        else:
            st.write("TBD")
        st.markdown("---")

    # ----------------------------------
    # STEP 7 — Institutional & Governance Constraints
    # ----------------------------------
    if step == 7:
        st.header("7. Institutional and Governance Constraints")
        constraints = case.get("constraints", [])
        if constraints:
            for c in constraints:
                st.markdown(
                    f"- **{c.get('type','TBD')}** – {c.get('description','TBD')}  \n"
                    f"  _Effect on decision_: {c.get('effect_on_decision','TBD')}"
                )
        else:
            st.write("TBD")
        st.markdown("---")

    # ----------------------------------
    # STEP 8 — Decision Outcome
    # ----------------------------------
    if step == 8:
        st.header("8. Decision Outcome")
        st.markdown(f"**Decision:** {case['decision_outcome'].get('decision','TBD')}")
        st.markdown("---")

    # ----------------------------------
    # STEP 9 — Ethical Implications
    # ----------------------------------
    if step == 9:
        st.header("9. Ethical Implications")
        implications = case["decision_outcome"].get("ethical_implications", [])
        if implications:
            for i in implications:
                st.markdown(f"- {i}")
        else:
            st.write("TBD")
        st.markdown("---")

    # ----------------------------------
    # Navigation Buttons
    # ----------------------------------
    col1, col2 = st.columns([1, 1])

    with col1:
        if step > 1:
            if st.button("◀ Previous"):
                st.session_state["cb_step"] = max(1, step - 1)
                _safe_rerun()

    with col2:
        if step < 9:
            if st.button("Next ▶"):
                st.session_state["cb_step"] = min(9, step + 1)
                _safe_rerun()
        else:
            st.info(
                "You've reached the end of the case. You may switch cases above or move to Open-Ended Mode."
            )
