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
    if not case_id:
        st.error("No case selected.")
        return

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

    # --- view state defaults ---
    if "cb_view" not in st.session_state:
        st.session_state["cb_view"] = "collapsed"  # collapsed | walkthrough | narrative
    if "cb_step" not in st.session_state:
        st.session_state["cb_step"] = 1

    # --- reset when case changes (defensive; main.py also resets) ---
    prev_case = st.session_state.get("cb_prev_case_id")
    if prev_case != case_id:
        st.session_state["cb_prev_case_id"] = case_id
        st.session_state["cb_step"] = 1
        st.session_state["cb_view"] = "collapsed"
        # no rerun needed; current render will continue in collapsed view

    view = st.session_state["cb_view"]

        # ----------------------------------------------------------
        # At-a-Glance (decision-relevant summary)
        # ----------------------------------------------------------
        atag = case.get("at_a_glance", {}) or {}

        decision_context = atag.get("decision_context", "TBD")
        technical_framing = atag.get("technical_framing", "TBD")
        ethical_tension = atag.get("ethical_tension", "TBD")
        constraints = atag.get("constraints", []) or []

        def _trim(text: str, limit: int = 220) -> str:
            if not text:
                return "TBD"
            return text[:limit] + ("…" if len(text) > limit else "")

        st.markdown(
            f"""
<div class="listbox">
  <div style="font-weight:700; margin-bottom:6px;">At a glance</div>
  <ul class="tight-list">
    <li><span class="sub">Decision context:</span> {_trim(decision_context)}</li>
    <li><span class="sub">Technical framing (NIST CSF 2.0):</span> {_trim(technical_framing)}</li>
    <li><span class="sub">Ethical tension (PFCE):</span> {_trim(ethical_tension)}</li>
    <li><span class="sub">Institutional and governance constraints:</span> {len(constraints)}</li>
  </ul>
</div>
            """,
            unsafe_allow_html=True,
        )


        col1, col2 = st.columns(2)
        with col1:
            if st.button("Open structured walkthrough", key=f"cb_open_walkthrough_{case_id}"):
                st.session_state["cb_view"] = "walkthrough"
                st.session_state["cb_step"] = 1
                _safe_rerun()
        with col2:
            if st.button("View full narrative", key=f"cb_view_narrative_{case_id}"):
                st.session_state["cb_view"] = "narrative"
                _safe_rerun()

        return

    # ==========================================================
    # VIEW 2: WALKTHROUGH (6 STEPS)
    # ==========================================================
    if view == "walkthrough":
        if st.button("← Back to collapsed view", key=f"cb_back_collapsed_from_walk_{case_id}"):
            st.session_state["cb_view"] = "collapsed"
            _safe_rerun()

        st.subheader(case.get("title", case_id))
        st.caption("Structured walkthrough (6 steps).")

        step = int(st.session_state.get("cb_step", 1))
        step = max(1, min(6, step))
        st.session_state["cb_step"] = step

        st.progress(step / 6.0)

        # STEP 1 — Background (compressed)
        if step == 1:
            st.header("1. Background")
            st.markdown("**Technical and operational background**")
            st.write(case["background"].get("technical_operational_background", "TBD"))
            st.markdown("**Triggering condition and key events**")
            st.write(case["background"].get("triggering_condition_key_events", "TBD"))

        # STEP 2 — Decision context + CSF
        elif step == 2:
            st.header("2. Decision Context and CSF Framing")
            st.markdown("**Decision context**")
            st.write(case["technical"].get("decision_context", "TBD"))

            st.markdown("**NIST CSF mapping**")
            mapping = case["technical"].get("nist_csf_mapping", [])
            if mapping:
                for m in mapping:
                    st.markdown(f"- **Function:** {m.get('function', 'TBD')}")
                    cats = m.get("categories", [])
                    if cats:
                        st.markdown("  - **Categories:**")
                        for c in cats:
                            st.markdown(f"    - {c}")
                    st.markdown(f"  _Rationale_: {m.get('rationale', 'TBD')}")
            else:
                st.write("TBD")

        # STEP 3 — Ethical significance + tension
        elif step == 3:
            st.header("3. Ethical Significance and Tension")
            st.markdown("**PFCE analysis (ethical significance)**")
            st.write(case["ethical"].get("pfce_analysis", "TBD"))

            st.markdown("**Ethical tension(s)**")
            tensions = case["ethical"].get("tensions", [])
            if tensions:
                for t in tensions:
                    st.markdown(f"- {t.get('description', 'TBD')}")
            else:
                st.write("TBD")

        # STEP 4 — PFCE principle mapping
        elif step == 4:
            st.header("4. PFCE Principle Mapping")
            pfce = case["ethical"].get("pfce_mapping", [])
            if pfce:
                for p in pfce:
                    st.markdown(f"- **{p.get('principle','TBD')}** – {p.get('description','TBD')}")
            else:
                st.write("TBD")

        # STEP 5 — Constraints
        elif step == 5:
            st.header("5. Institutional and Governance Constraints")
            constraints = case.get("constraints", [])
            if constraints:
                for c in constraints:
                    st.markdown(
                        f"- **{c.get('type','TBD')}** – {c.get('description','TBD')}  \n"
                        f"  _Effect on decision_: {c.get('effect_on_decision','TBD')}"
                    )
            else:
                st.write("TBD")

        # STEP 6 — Outcome + implications
        elif step == 6:
            st.header("6. Decision Outcome and Implications")
            st.markdown("**Decision**")
            st.write(case["decision_outcome"].get("decision", "TBD"))

            st.markdown("**Outcomes and implications**")
            st.write(case["decision_outcome"].get("outcomes_implications", "TBD"))

            implications = case["decision_outcome"].get("ethical_implications", [])
            if implications:
                st.markdown("**Ethical implications:**")
                for i in implications:
                    st.markdown(f"- {i}")

        st.markdown("---")

        # navigation
        col1, col2 = st.columns([1, 1])
        with col1:
            if step > 1 and st.button("◀ Previous", key=f"cb_prev_{case_id}_{step}"):
                st.session_state["cb_step"] = step - 1
                _safe_rerun()
        with col2:
            if step < 6:
                if st.button("Next ▶", key=f"cb_next_{case_id}_{step}"):
                    st.session_state["cb_step"] = step + 1
                    _safe_rerun()
            else:
                st.info("End of walkthrough. Return to collapsed view or open the full narrative.")

        return

    # ==========================================================
    # VIEW 3: FULL NARRATIVE (EXPANDERS)
    # ==========================================================
    if view == "narrative":
        if st.button("← Back to collapsed view", key=f"cb_back_collapsed_from_narr_{case_id}"):
            st.session_state["cb_view"] = "collapsed"
            _safe_rerun()

        st.subheader(case.get("title", case_id))
        st.caption("Full narrative (expand sections as needed).")

        with st.expander("Technical and operational background", expanded=False):
            st.write(case["background"].get("technical_operational_background", "TBD"))

        with st.expander("Triggering condition and key events", expanded=False):
            st.write(case["background"].get("triggering_condition_key_events", "TBD"))

        with st.expander("Decision context and CSF mapping", expanded=False):
            st.markdown("**Decision context**")
            st.write(case["technical"].get("decision_context", "TBD"))

            st.markdown("**NIST CSF mapping**")
            mapping = case["technical"].get("nist_csf_mapping", [])
            if mapping:
                for m in mapping:
                    st.markdown(f"- **Function:** {m.get('function', 'TBD')}")
                    cats = m.get("categories", [])
                    if cats:
                        st.markdown("  - **Categories:**")
                        for c in cats:
                            st.markdown(f"    - {c}")
                    st.markdown(f"  _Rationale_: {m.get('rationale', 'TBD')}")
            else:
                st.write("TBD")

        with st.expander("PFCE analysis, tensions, and principle mapping", expanded=False):
            st.markdown("**PFCE analysis**")
            st.write(case["ethical"].get("pfce_analysis", "TBD"))

            st.markdown("**Ethical tension(s)**")
            tensions = case["ethical"].get("tensions", [])
            if tensions:
                for t in tensions:
                    st.markdown(f"- {t.get('description', 'TBD')}")
            else:
                st.write("TBD")

            st.markdown("**PFCE principle mapping**")
            pfce = case["ethical"].get("pfce_mapping", [])
            if pfce:
                for p in pfce:
                    st.markdown(f"- **{p.get('principle','TBD')}** – {p.get('description','TBD')}")
            else:
                st.write("TBD")

        with st.expander("Institutional and governance constraints", expanded=False):
            constraints = case.get("constraints", [])
            if constraints:
                for c in constraints:
                    st.markdown(
                        f"- **{c.get('type','TBD')}** – {c.get('description','TBD')}  \n"
                        f"  _Effect on decision_: {c.get('effect_on_decision','TBD')}"
                    )
            else:
                st.write("TBD")

        with st.expander("Decision outcome and implications", expanded=False):
            st.markdown("**Decision**")
            st.write(case["decision_outcome"].get("decision", "TBD"))

            st.markdown("**Outcomes and implications**")
            st.write(case["decision_outcome"].get("outcomes_implications", "TBD"))

            implications = case["decision_outcome"].get("ethical_implications", [])
            if implications:
                st.markdown("**Ethical implications:**")
                for i in implications:
                    st.markdown(f"- {i}")

        return
