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
    if prev_case != case_id:
        st.session_state["cb_step"] = 1
        st.session_state["cb_prev_case_id"] = case_id
        st.session_state["cb_view"] = "collapsed"
        _safe_rerun()

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
        st.subheader(case.get("title", case_id))
        if case.get("short_summary"):
            st.caption(case.get("short_summary", ""))

        # ----------------------------------------------------------
        # At-a-glance should pull from YAML: case["at_a_glance"]
        # with fallback to existing fields if needed
        # ----------------------------------------------------------
        glance = case.get("at_a_glance", {}) or {}

        decision_context = glance.get("decision_context") or case["technical"].get("decision_context", "")

        technical_framing = glance.get("technical_framing", "")
        ethical_tension = glance.get("ethical_tension", "")

        # Constraints for At-a-glance:
        # Prefer YAML at_a_glance.constraints if present, otherwise fall back to case.constraints
        constraints = glance.get("constraints")
        if constraints is None:
            constraints = case.get("constraints", [])

        # If technical_framing wasn't provided in at_a_glance, derive a compact line from mapping (existing behavior)
        if not technical_framing:
            mapping = case["technical"].get("nist_csf_mapping", [])
            csf_line = "TBD"
            if mapping:
                fn = mapping[0].get("function", "TBD")
                cats = mapping[0].get("categories", [])
                if isinstance(cats, str):
                    cats = [cats]
                csf_line = f"{fn}" + (f" — {', '.join(cats)}" if cats else "")
            technical_framing = csf_line

        # If ethical_tension wasn't provided in at_a_glance, fall back to first tension description (existing behavior)
        if not ethical_tension:
            tensions = case["ethical"].get("tensions", [])
            ethical_tension = "TBD"
            if tensions:
                ethical_tension = tensions[0].get("description", "TBD")

        # Constraints listed as bullets (not a count)
        constraints_html = "<span class='sub'>TBD</span>"
        if constraints:
            # support either list[str] OR list[dict]
            items = []
            for c in constraints:
                if isinstance(c, dict):
                    items.append(c.get("description") or c.get("type") or "TBD")
                else:
                    items.append(str(c))
            constraints_html = "<ul class='tight-list'>" + "".join(
                f"<li>{html.escape(i)}</li>" for i in items
            ) + "</ul>"

        st.markdown(
            f"""
<div class="listbox">
  <div style="font-weight:700; margin-bottom:6px;">At a glance</div>
  <ul class="tight-list">
    <li><span class="sub">Decision context:</span> {decision_context[:220] + ("…" if len(decision_context) > 220 else "") if decision_context else "TBD"}</li>
    <li><span class="sub">Technical framing (NIST CSF 2.0):</span> {technical_framing[:220] + ("…" if len(technical_framing) > 220 else "") if technical_framing else "TBD"}</li>
    <li><span class="sub">Ethical tension (PFCE):</span> {ethical_tension[:220] + ("…" if len(ethical_tension) > 220 else "") if ethical_tension else "TBD"}</li>
    <li><span class="sub">Institutional and governance constraints:</span> {constraints_html}</li>
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
    # VIEW 2: WALKTHROUGH (STEP-BASED)
    # ==========================================================
    if view == "walkthrough":
        if "cb_step" not in st.session_state:
            st.session_state["cb_step"] = 1
        step = st.session_state["cb_step"]

        st.subheader(case.get("title", case_id))
        if case.get("short_summary"):
            st.caption(case.get("short_summary", ""))

        st.progress(step / 9.0)

        if step == 1:
            st.header("1. Technical and Operational Background")
            st.write(case["background"].get("technical_operational_background", "TBD"))
            st.markdown("---")

        if step == 2:
            st.header("2. Triggering Condition and Key Events")
            st.write(case["background"].get("triggering_condition_key_events", "TBD"))
            st.markdown("---")

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
                    if isinstance(cats, str):
                        cats = [cats]
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

        if step == 4:
            st.header("4. PFCE Analysis")
            st.write(case["ethical"].get("pfce_analysis", "TBD"))
            st.markdown("---")

        if step == 5:
            st.header("5. Ethical Tension")
            tensions = case["ethical"].get("tensions", [])
            if tensions:
                for t in tensions:
                    st.markdown(f"- {t.get('description', 'TBD')}")
            else:
                st.write("TBD")
            st.markdown("---")

        if step == 6:
            st.header("6. PFCE Principle Mapping")
            pfce = case["ethical"].get("pfce_mapping", [])
            if pfce:
                for p in pfce:
                    st.markdown(f"- **{p.get('principle','TBD')}** – {p.get('description','TBD')}")
            else:
                st.write("TBD")
            st.markdown("---")

        if step == 7:
            st.header("7. Institutional and Governance Constraints")
            constraints = case.get("constraints", [])
            if constraints:
                for c in constraints:
                    if isinstance(c, dict):
                        st.markdown(f"- **{c.get('type','TBD')}** – {c.get('description','TBD')}")
                        if c.get("effect_on_decision"):
                            st.markdown(f"  \n  _Effect on decision_: {c.get('effect_on_decision')}")
                    else:
                        st.markdown(f"- {c}")
            else:
                st.write("TBD")
            st.markdown("---")

        if step == 8:
            st.header("8. Decision")
            st.write(case["decision_outcome"].get("decision", "TBD"))
            st.markdown("---")

        if step == 9:
            st.header("9. Outcomes and Implications")
            st.write(case["decision_outcome"].get("outcomes_implications", "TBD"))

            implications = case["decision_outcome"].get("ethical_implications", [])
            if implications:
                st.markdown("**Ethical Implications:**")
                for i in implications:
                    st.markdown(f"- {i}")

            st.markdown("---")

        # Navigation controls
        colA, colB, colC = st.columns([1, 1, 1])
        with colA:
            if st.button("◀ Back to At-a-Glance", key=f"cb_back_glance_{case_id}"):
                st.session_state["cb_view"] = "collapsed"
                _safe_rerun()

        with colB:
            if step > 1 and st.button("◀ Previous", key=f"cb_prev_{step}_{case_id}"):
                st.session_state["cb_step"] = max(1, step - 1)
                _safe_rerun()

        with colC:
            if step < 9:
                if st.button("Next ▶", key=f"cb_next_{step}_{case_id}"):
                    st.session_state["cb_step"] = min(9, step + 1)
                    _safe_rerun()
            else:
                st.info("End of case. Switch cases above or return to At-a-Glance.")

        return

    # ==========================================================
    # VIEW 3: FULL NARRATIVE (OPTIONAL)
    # ==========================================================
    if view == "narrative":
        st.subheader(case.get("title", case_id))
        if case.get("short_summary"):
            st.caption(case.get("short_summary", ""))

        if st.button("◀ Back to At-a-Glance", key=f"cb_back_glance_narr_{case_id}"):
            st.session_state["cb_view"] = "collapsed"
            _safe_rerun()

        st.markdown("---")

        # Show narrative blocks if you have them; otherwise show what exists
        with st.expander("Technical and Operational Background", expanded=True):
            st.write(case["background"].get("technical_operational_background", "TBD"))

        with st.expander("Triggering Condition and Key Events"):
            st.write(case["background"].get("triggering_condition_key_events", "TBD"))

        with st.expander("Decision Context and NIST CSF Mapping"):
            st.write(case["technical"].get("decision_context", "TBD"))
            mapping = case["technical"].get("nist_csf_mapping", [])
            if mapping:
                st.markdown("**NIST CSF Mapping**")
                for m in mapping:
                    st.markdown(f"- **Function:** {m.get('function', 'TBD')}")
                    cats = m.get("categories", [])
                    if isinstance(cats, str):
                        cats = [cats]
                    if cats:
                        st.markdown("  - **Categories:**")
                        for c in cats:
                            st.markdown(f"    - {c}")
                    if m.get("rationale"):
                        st.markdown(f"  _Rationale_: {m.get('rationale')}")

        with st.expander("PFCE Analysis"):
            st.write(case["ethical"].get("pfce_analysis", "TBD"))

        with st.expander("Ethical Tensions"):
            tensions = case["ethical"].get("tensions", [])
            if tensions:
                for t in tensions:
                    st.markdown(f"- {t.get('description', 'TBD')}")
            else:
                st.write("TBD")

        with st.expander("Institutional and Governance Constraints"):
            constraints = case.get("constraints", [])
            if constraints:
                for c in constraints:
                    if isinstance(c, dict):
                        st.markdown(f"- **{c.get('type','TBD')}** – {c.get('description','TBD')}")
                    else:
                        st.markdown(f"- {c}")
            else:
                st.write("TBD")

        with st.expander("Decision, Outcomes, and Implications"):
            st.write(case["decision_outcome"].get("decision", "TBD"))
            st.write(case["decision_outcome"].get("outcomes_implications", "TBD"))

        return
