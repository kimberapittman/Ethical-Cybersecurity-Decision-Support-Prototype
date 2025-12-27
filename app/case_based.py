import streamlit as st
from logic.loaders import load_case
import html


def _safe_rerun():
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    except Exception:
        pass


def _render_bullets(value):
    """
    Render a YAML value as bullets if it's a list,
    otherwise render as plain text.
    """
    if value is None:
        st.write("TBD")
    elif isinstance(value, list):
        if not value:
            st.write("TBD")
        else:
            for item in value:
                st.markdown(f"- {item}")
    else:
        st.write(value)


PFCE_DEFINITIONS = {
    "Beneficence": (
        "Cybersecurity technologies should be used to benefit humans, "
        "promote human well-being, and make our lives better overall."
    ),
    "Non-maleficence": (
        "Cybersecurity technologies should not be used to intentionally harm humans "
        "or to make our lives worse overall."
    ),
    "Autonomy": (
        "Cybersecurity technologies should be used in ways that respect human autonomy. "
        "Humans should be able to make informed decisions for themselves about how that "
        "technology is used in their lives."
    ),
    "Justice": (
        "Cybersecurity technologies should be used to promote fairness, equality, "
        "and impartiality. They should not be used to unfairly discriminate, "
        "undermine solidarity, or prevent equal access."
    ),
    "Explicability": (
        "Cybersecurity technologies should be used in ways that are intelligible, "
        "transparent, and comprehensible, and it should be clear who is accountable "
        "and responsible for their use."
    ),
}


def _as_text(value) -> str:
    """
    Normalize YAML values that may be a string or a list into a display-safe string.
    - None -> ""
    - str -> str
    - list -> first item as str (or "" if empty)
    - other -> str(value)
    """
    if value is None:
        return ""
    if isinstance(value, list):
        return str(value[0]) if value else ""
    if isinstance(value, str):
        return value
    return str(value)


def render_case(case_id: str):
    case = load_case(case_id) or {}

    # --- normalize expected top-level sections ---
    case.setdefault("background", {})
    case.setdefault("technical", {})
    case.setdefault("ethical", {})
    case.setdefault("constraints", [])
    case.setdefault("decision_outcome", {})
    case.setdefault("at_a_glance", {})  # <-- ensure at_a_glance exists

    case["technical"].setdefault("nist_csf_mapping", [])
    case["ethical"].setdefault("tensions", [])
    case["ethical"].setdefault("pfce_mapping", [])
    case["decision_outcome"].setdefault("ethical_implications", [])

    # ==========================================================
    # RESET NAVIGATION WHEN CASE CHANGES
    # ==========================================================
    prev_case = st.session_state.get("cb_prev_case_id")

    # First time a case is loaded, just store it (no rerun)
    if prev_case is None:
        st.session_state["cb_prev_case_id"] = case_id

    # Only reset state if the user actually switched cases (no rerun)
    elif prev_case != case_id:
        st.session_state["cb_step"] = 1
        st.session_state["cb_prev_case_id"] = case_id
        st.session_state["cb_view"] = "collapsed"
        st.session_state.pop("cb_step_return", None)
        # IMPORTANT: do NOT call _safe_rerun() here

    # ==========================================================
    # VIEW STATE
    # ==========================================================
    if "cb_view" not in st.session_state:
        st.session_state["cb_view"] = "collapsed"
    view = st.session_state["cb_view"]

    # ==========================================================
    # VIEW 1: COLLAPSED CASE CARD (DEFAULT)
    # ==========================================================
    if view == "collapsed":

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        # Centered primary action (collapsed view only)
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            if st.button(
                "Open Structured Walkthrough",
                key=f"cb_open_walkthrough_{case_id}",
                use_container_width=True,
            ):
                st.session_state["cb_view"] = "walkthrough"
                st.session_state["cb_step"] = 1
                st.session_state.pop("cb_step_return", None)
                st.rerun()

        return  # IMPORTANT: stop here so walkthrough doesn't render on same run

    # ==========================================================
    # VIEW 2: WALKTHROUGH (STEP-BASED)
    # ==========================================================
    if view == "walkthrough":
        if "cb_step" not in st.session_state:
            st.session_state["cb_step"] = 1
        step = st.session_state["cb_step"]

        # --- Visual separation to match collapsed view ---
        st.markdown(
            "<hr style='margin: 12px 0 16px 0; opacity: 0.35;'>",
            unsafe_allow_html=True,
        )

        st.subheader(case.get("title", case_id))

        if case.get("short_summary"):
            st.caption(case.get("short_summary", ""))

        st.progress(step / 10.0)

        if step == 1:
            st.header("1. Technical and Operational Background")
            _render_bullets(case["background"].get("technical_operational_background"))
            st.markdown("---")

        if step == 2:
            st.header("2. Triggering Condition and Key Events")
            _render_bullets(case["background"].get("triggering_condition_key_events"))
            st.markdown("---")

        if step == 3:
            st.header("3. Decision Context")
            _render_bullets(case["technical"].get("decision_context"))
            st.markdown("---")

        if step == 4:
            st.header("4. NIST CSF Mapping")

            mapping = case["technical"].get("nist_csf_mapping", [])

            if mapping:
                for m in mapping:
                    fn = m.get("function", "TBD")

                    cats = m.get("categories", [])
                    if isinstance(cats, str):
                        cats = [cats]

                    cat_text = ", ".join(cats) if cats else "TBD"

                    st.markdown(f"- **{fn} — {cat_text}**")

                    if m.get("rationale"):
                        st.markdown(f"_Rationale_: {m.get('rationale')}")
            else:
                st.write("TBD")

            st.markdown("---")

        if step == 5:
            st.header("5. Ethical Tension")
            tensions = case["ethical"].get("tension", [])
            if tensions:
                for t in tensions:
                    st.markdown(f"- {t.get('description', 'TBD')}")
            else:
                st.write("TBD")
            st.markdown("---")

        if step == 6:
            st.header("6. PFCE Analysis")
            _render_bullets(case["ethical"].get("pfce_analysis"))
            st.markdown("---")

        if step == 7:
            st.header("7. PFCE Principle Mapping")
            pfce = case["ethical"].get("pfce_mapping", [])
            if pfce:
                for p in pfce:
                    principle = p.get("principle", "TBD")
                    definition = PFCE_DEFINITIONS.get(principle, "")
                    desc = p.get("description", "TBD")

                    if definition:
                        st.markdown(
                            f"""
                        - <span title="{html.escape(definition)}"
                            style="font-weight:700; text-decoration: underline dotted; cursor: help;">{html.escape(principle)}</span>: {html.escape(desc)}
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(f"- **{principle}** – {desc}")

            else:
                st.write("TBD")
            st.markdown("---")

        if step == 8:
            st.header("8. Institutional and Governance Constraints")
            constraints = case.get("constraints", [])
            if constraints:
                for c in constraints:
                    if isinstance(c, dict):
                        st.markdown(
                            f"- **{c.get('type','TBD')}** – {c.get('description','TBD')}"
                        )
                        if c.get("effect_on_decision"):
                            st.markdown(
                                f"  \n  _Effect on decision_: {c.get('effect_on_decision')}"
                            )
                    else:
                        st.markdown(f"- {c}")
            else:
                st.write("TBD")
            st.markdown("---")

        if step == 9:
            st.header("9. Decision")
            st.write(case["decision_outcome"].get("decision"))
            st.markdown("---")

        if step == 10:
            st.header("10. Outcomes and Implications")
            _render_bullets(case["decision_outcome"].get("outcomes_implications"))
            st.markdown("---")

        # Navigation controls (centered layout)
        col_prev, col_spacer_left, col_next, col_spacer_right, col_exit = st.columns(
            [1, 2, 1, 2, 1]
        )

        with col_prev:
            if step > 1 and st.button("◀ Previous", key=f"cb_prev_{step}_{case_id}"):
                st.session_state["cb_step"] = max(1, step - 1)
                _safe_rerun()

        with col_next:
            if step < 10:
                if st.button(
                    "Next ▶",
                    key=f"cb_next_{step}_{case_id}",
                    use_container_width=True,
                ):
                    st.session_state["cb_step"] = min(10, step + 1)
                    _safe_rerun()
            else:
                st.info("End of Case.")

        with col_exit:
            if st.button("Exit Walkthrough", key=f"cb_exit_walkthrough_{case_id}"):
                st.session_state["cb_view"] = "collapsed"
                _safe_rerun()

        return
