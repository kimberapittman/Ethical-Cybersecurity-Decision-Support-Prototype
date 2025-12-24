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
    "Beneficence": "Obligation to act in ways that promote well-being and prevent harm.",
    "Non-maleficence": "Obligation to avoid actions that cause harm.",
    "Autonomy": "Respect for individuals’ ability to make informed decisions about matters affecting them.",
    "Justice": "Fair and equitable distribution of benefits, burdens, and risks.",
    "Explicability": "Obligation to ensure decisions and systems can be understood, explained, and justified.",
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
    if prev_case != case_id:
        st.session_state["cb_step"] = 1
        st.session_state["cb_prev_case_id"] = case_id
        st.session_state["cb_view"] = "collapsed"
        # narrative removed; no need to track return-step
        st.session_state.pop("cb_step_return", None)
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
        # At A Glance should pull from YAML: case["at_a_glance"]
        # with fallback to existing fields if needed
        # ----------------------------------------------------------
        glance = case.get("at_a_glance", {}) or {}

        decision_context = glance.get("decision_context") or case["technical"].get("decision_context", "")

        technical_framing = glance.get("technical_framing", "")
        ethical_tension = glance.get("ethical_tension", "")

        # Constraints for At A Glance:
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

        # Normalize at a glance fields to strings (supports YAML list or str)
        decision_context_text = _as_text(decision_context)
        technical_framing_text = _as_text(technical_framing)
        ethical_tension_text = _as_text(ethical_tension)

        def _as_list(value):
            if value is None:
                return []
            if isinstance(value, list):
                return [str(v) for v in value if v is not None and str(v).strip()]
            if isinstance(value, str):
                v = value.strip()
                return [v] if v else []
            return [str(value)]

        def _render_glance_section(title: str, items):
            items = _as_list(items)
            if not items:
                return f"""
<div style="margin: 10px 0 14px 0;">
  <div style="font-weight:700; margin-bottom:6px;">{html.escape(title)}</div>
  <div class="sub">TBD</div>
</div>
"""
            bullets = "".join(f"<li>{html.escape(i)}</li>" for i in items)
            return f"""
<div style="margin: 10px 0 14px 0;">
  <div style="font-weight:700; margin-bottom:6px;">{html.escape(title)}</div>
  <ul class="tight-list" style="margin-top:0; padding-left:22px;">{bullets}</ul>
</div>
"""

        # Build the new "At a glance" layout: heading + bullets under each
        decision_items = _as_list(glance.get("decision_context") or case["technical"].get("decision_context", ""))
        tech_items = _as_list(glance.get("technical_framing") or technical_framing_text)
        ethical_items = _as_list(glance.get("ethical_tension") or ethical_tension_text)

        # Constraints: prefer at_a_glance.constraints, else fallback to case.constraints (existing behavior)
        raw_constraints = glance.get("constraints")
        if raw_constraints is None:
            raw_constraints = case.get("constraints", [])

        # Normalize constraints to list[str] for display
        constraint_items = []
        if raw_constraints:
            for c in raw_constraints:
                if isinstance(c, dict):
                    constraint_items.append(c.get("description") or c.get("type") or "TBD")
                else:
                    constraint_items.append(str(c))

        st.markdown(
            f"""
<div class="listbox">
  <div style="font-weight:700; margin-bottom:10px;">At a glance</div>

  {_render_glance_section("Decision context", decision_items)}
  {_render_glance_section("Technical framing (NIST CSF 2.0)", tech_items)}
  {_render_glance_section("Ethical tension (PFCE)", ethical_items)}
  {_render_glance_section("Institutional and governance constraints", constraint_items)}

</div>
            """,
            unsafe_allow_html=True,
        )

        # Single primary entry point
        if st.button("Open structured walkthrough", key=f"cb_open_walkthrough_{case_id}"):
            st.session_state["cb_view"] = "walkthrough"
            st.session_state["cb_step"] = 1

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
            _render_bullets(case["background"].get("technical_operational_background"))
            st.markdown("---")

        if step == 2:
            st.header("2. Triggering Condition and Key Events")
            _render_bullets(case["background"].get("triggering_condition_key_events"))
            st.markdown("---")

        if step == 3:
            st.header("3. Decision Context & NIST CSF Mapping")
            st.markdown("**Decision Context**")
            _render_bullets(case["technical"].get("decision_context"))

        st.markdown("**NIST CSF Framing**")

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

 
        if step == 4:
            st.header("4. Ethical Tension")
            tensions = case["ethical"].get("tension", [])
            if tensions:
                for t in tensions:
                    st.markdown(f"- {t.get('description', 'TBD')}")
            else:
                st.write("TBD")
            st.markdown("---")


        if step == 5:
            st.header("5. PFCE Analysis")
            _render_bullets(case["ethical"].get("pfce_analysis"))
            st.markdown("---")


        if step == 6:
            st.header("6. PFCE Principle Mapping")
            pfce = case["ethical"].get("pfce_mapping", [])
            if pfce:
                for p in pfce:
                    principle = p.get("principle", "TBD")
                    definition = PFCE_DEFINITIONS.get(principle, "")
                    desc = p.get("description", "TBD")

                    if definition:
                        st.markdown(
                            f"- <strong title='{html.escape(definition)}'>{html.escape(principle)}</strong> – {html.escape(desc)}",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(f"- **{principle}** – {desc}")

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
            st.write(case["decision_outcome"].get("decision"))
            st.markdown("---")

        if step == 9:
            st.header("9. Outcomes and Implications")
            _render_bullets(case["decision_outcome"].get("outcomes_implications"))
            st.markdown("---")

        # Navigation controls (single row)
        col_prev, col_next, col_exit = st.columns([1, 1, 1])

        with col_prev:
            if step > 1 and st.button("◀ Previous", key=f"cb_prev_{step}_{case_id}"):
                st.session_state["cb_step"] = max(1, step - 1)
                _safe_rerun()

        with col_next:
            if step < 9:
                if st.button("Next ▶", key=f"cb_next_{step}_{case_id}"):
                    st.session_state["cb_step"] = min(9, step + 1)
                    _safe_rerun()
            else:
                st.info("End of case.")

        with col_exit:
            if st.button("Exit walkthrough", key=f"cb_exit_walkthrough_{case_id}"):
                st.session_state["cb_view"] = "collapsed"
                _safe_rerun()

        return


