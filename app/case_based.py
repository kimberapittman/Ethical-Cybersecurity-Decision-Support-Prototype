import streamlit as st
from logic.loaders import load_case


def _safe_rerun():
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    except Exception:
        pass


def render_case(case_id: str):
    case = load_case(case_id) or {}

    # --- normalize expected top-level sections ---
    case.setdefault("background", {})
    case.setdefault("technical", {})
    case.setdefault("ethical", {})
    case.setdefault("constraints", [])
    case.setdefault("decision_outcome", {})

    case["technical"].setdefault("nist_csf_mapping", [])
    case["ethical"].setdefault("tensions", [])
    case["ethical"].setdefault("pfce_mapping", [])
    case["decision_outcome"].setdefault("ethical_implications", [])

    # --- step navigation ---
    if "cb_step" not in st.session_state:
        st.session_state["cb_step"] = 1
    step = st.session_state["cb_step"]

    # --- Title + Summary ---
    st.markdown(
        "<h2 style='text-align: center; margin-top: 0.25rem;'>Case-Based Mode</h2>",
        unsafe_allow_html=True,
    )
    st.subheader(case.get("title", case_id))
    st.caption(case.get("short_summary", ""))

    st.progress(step / 9.0)

    # -----------------------------
    # STEP 1 — Technical / Operational Background
    # -----------------------------
    if step == 1:
        st.header("1. Technical and Operational Background")
        st.write(case["background"].get("technical_operational_background", "TBD"))
        st.markdown("---")

    # -----------------------------
    # STEP 2 — Triggering Condition & Key Events
    # -----------------------------
    if step == 2:
        st.header("2. Triggering Condition and Key Events")
        st.write(case["background"].get("triggering_condition_key_events", "TBD"))
        st.markdown("---")

    # -----------------------------
    # STEP 3 — Decision Context & NIST CSF Mapping
    # -----------------------------
    if step == 3:
        st.header("3. Decision Context & NIST CSF Mapping")
        st.markdown("**Decision Context**")
        st.write(case["technical"].get("decision_context", "TBD"))

        st.markdown("**NIST CSF Mapping**")
        mapping = case["technical"].get("nist_csf_mapping", [])
        if mapping:
            for m in mapping:
                st.markdown(f"- **Function:** {m.get('function', 'TBD')}")
                cats = m.get("categories", [])
                if cats:
                    st.markdown("  - **Categories:**")
                    for c in cats:
                        st.markdown(f"    - {c}")
                else:
                    st.markdown("  - **Categories:** TBD")
                st.markdown(f"  _Rationale_: {m.get('rationale', 'TBD')}")
        else:
            st.write("TBD")

        st.markdown("---")

    # -----------------------------
    # STEP 4 — PFCE Analysis
    # -----------------------------
    if step == 4:
        st.header("4. PFCE Analysis")
        st.write(case["ethical"].get("pfce_analysis", "TBD"))
        st.markdown("---")

    # -----------------------------
    # STEP 5 — Ethical Tension
    # -----------------------------
    if step == 5:
        st.header("5. Ethical Tension")
        tensions = case["ethical"].get("tensions", [])
        if tensions:
            for t in tensions:
                st.markdown(f"- {t.get('description', 'TBD')}")
        else:
            st.write("TBD")
        st.markdown("---")

    # -----------------------------
    # STEP 6 — PFCE Principle Mapping
    # -----------------------------
    if step == 6:
        st.header("6. PFCE Principle Mapping")
        pfce = case["ethical"].get("pfce_mapping", [])
        if pfce:
            for p in pfce:
                st.markdown(f"- **{p.get('principle','TBD')}** – {p.get('description','TBD')}")
        else:
            st.write("TBD")
        st.markdown("---")

    # -----------------------------
    # STEP 7 — Institutional & Governance Constraints
    # -----------------------------
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

    # -----------------------------
    # STEP 8 — Decision
    # -----------------------------
    if step == 8:
        st.header("8. Decision")
        st.write(case["decision_outcome"].get("decision", "TBD"))
        st.markdown("---")

    # -----------------------------
    # STEP 9 — Outcomes & Implications
    # -----------------------------
    if step == 9:
        st.header("9. Outcomes and Implications")
        st.write(case["decision_outcome"].get("outcomes_implications", "TBD"))

        implications = case["decision_outcome"].get("ethical_implications", [])
        if implications:
            st.markdown("**Ethical Implications:**")
            for i in implications:
                st.markdown(f"- {i}")

        st.markdown("---")

    # --- navigation ---
    col1, col2 = st.columns([1, 1])
    with col1:
        if step > 1 and st.button("◀ Previous", key=f"cb_prev_{step}"):
            st.session_state["cb_step"] = max(1, step - 1)
            _safe_rerun()

    with col2:
        if step < 9:
            if st.button("Next ▶", key=f"cb_next_{step}"):
                st.session_state["cb_step"] = min(9, step + 1)
                _safe_rerun()
        else:
            st.info("End of case. Switch cases above or move to Open-Ended Mode.")
