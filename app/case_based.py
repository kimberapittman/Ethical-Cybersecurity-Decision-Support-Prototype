import streamlit as st
from logic.loaders import load_case, list_cases
import html

st.markdown(
    """
    <style>
    .case-badge-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-bottom: 10px;
    }

    .case-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        white-space: nowrap;
    }

    .case-badge.real {
        background: rgba(59, 130, 246, 0.15);   /* muted blue */
        border: 1px solid rgba(59, 130, 246, 0.45);
        color: #cfe2ff;
    }

    .case-badge.hypo {
        background: rgba(148, 163, 184, 0.15);  /* neutral slate */
        border: 1px solid rgba(148, 163, 184, 0.45);
        color: #e5e7eb;
    }
    .case-badge {
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}

    .case-badge:hover {
        box-shadow: 0 0 0 2px rgba(255,255,255,0.08);
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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


NIST_CSF_URL = "https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf"
PFCE_URL = "https://doi.org/10.1016/j.cose.2021.102382"

NIST_CSF_HOVER = (
    "National Institute of Standards and Technology (NIST) Cybersecurity Framework (CSF): "
    "A voluntary framework that provides a common structure for identifying, assessing, and "
    "managing cybersecurity activities across the cybersecurity lifecycle. In this prototype, "
    "the CSF is used to situate decisions procedurally, not to prescribe actions."
)

PFCE_HOVER = (
    "Principlist Framework for Cybersecurity Ethics (PFCE): "
    "A normative, non-prescriptive framework that supports ethical reasoning by identifying "
    "ethically relevant principles and tensions within cybersecurity decision contexts."
)


def _step_title_with_framework(step_num: int, title: str, acronym: str, hover: str, url: str):
    """
    Render a step title where the framework acronym inside the title is:
    - bold
    - underlined to signal hover
    - shows a tooltip on hover
    - links out to the reference

    IMPORTANT: `title` should contain `acronym` somewhere (e.g., "NIST CSF Mapping").
    """
    tooltip_link = (
        f'<a href="{html.escape(url)}" target="_blank" style="text-decoration: none;">'
        f'  <span title="{html.escape(hover)}" '
        f'        style="font-weight: 800; text-decoration: underline; cursor: help;">'
        f'    {html.escape(acronym)}'
        f'  </span>'
        f'</a>'
    )

    # Replace only the first occurrence of the acronym in the title
    safe_title = html.escape(title).replace(html.escape(acronym), tooltip_link, 1)

    st.markdown(
        f"""
<h2 style="margin: 0.2rem 0 0.8rem 0;">
  {step_num}. {safe_title}
</h2>
        """,
        unsafe_allow_html=True,
    )


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


def _html_block(s: str) -> str:
    # Prevent Markdown from treating indented HTML as a code block.
    return "\n".join(line.lstrip() for line in s.splitlines())


def render_case(case_id: str):
    # ==========================================================
    # VIEW STATE (default to "select" to avoid dropdown + open button)
    # ==========================================================
    if "cb_view" not in st.session_state:
        st.session_state["cb_view"] = "select"
    view = st.session_state["cb_view"]

    # ==========================================================
    # VIEW 0: SELECT (three tiles, landing-page styling)
    # ==========================================================
    if view == "select":
        cases = list_cases() or []
        top_cases = cases[:3]

        st.markdown(
    """
<div style='text-align:center; margin-top: 0.5rem;'>
<h2 style='margin-bottom:0.35rem; display:inline-block;'>
    Select a Case
</h2>
</div>
    """,
    unsafe_allow_html=True,
)

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        if not top_cases:
            st.error("No cases found in data/cases.")
            return

        cols = st.columns(3, gap="large")

        for col, c in zip(cols, top_cases):
            cid = c.get("id", "")
            title = c.get("ui_title") or c.get("title", "TBD")
            short_summary = c.get("short_summary", "")

            with col:        
                # Badge selection (based on case id)
                if str(cid).lower() == "riverton":
                    badge_html = (
                        '<div class="case-badge-wrap">'
                        '<span class="case-badge hypo" '
                        'title="Constructed scenario used to demonstrate forward-looking reasoning.">'
                        'Hypothetical Scenario'
                        '</span>'
                        '</div>'
                    )

                else:
                    badge_html = (
                        '<div class="case-badge-wrap">'
                        '<span class="case-badge real" '
                        'title="Reconstructed from documented municipal incidents.">'
                        'Real-World Incident'
                        '</span>'
                        '</div>'
                    )

                st.markdown(
                    _html_block(
                        f"""
                        <a href="?cb_case_id={html.escape(str(cid))}" target="_self"
                        style="text-decoration:none; color: inherit; display:block;">
                        <div class="listbox" style="cursor:pointer;">
                            {badge_html}
                            <div style="font-weight:700; font-size:1.05rem; margin-bottom:6px; text-align:center;">
                            {html.escape(title)}
                            </div>
                            {(
                                '<div class="sub" style="text-align:center;">'
                                + html.escape(short_summary)
                                + '</div>'
                            ) if short_summary else ""}
                        </div>
                        </a>
                        """
                    ),
                    unsafe_allow_html=True,
                )


        # Handle tile click via query params (same tab)
        try:
            qp = st.query_params
            picked = qp.get("cb_case_id", None)
            if picked:
                st.session_state["cb_case_id"] = picked
                st.session_state["cb_prev_case_id"] = picked
                st.session_state["cb_view"] = "walkthrough"
                st.session_state["cb_step"] = 1
                st.session_state.pop("cb_step_return", None)
                try:
                    st.query_params.clear()
                except Exception:
                    pass
                st.rerun()
        except Exception:
            pass

        return

    # ==========================================================
    # WALKTHROUGH: load selected case
    # ==========================================================
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
    case["ethical"].setdefault("pfce_analysis", [])
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
        st.session_state["cb_view"] = "walkthrough"
        st.session_state.pop("cb_step_return", None)
        # IMPORTANT: do NOT call _safe_rerun() here

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
            st.header("3. Decision Context")
            _render_bullets(case["technical"].get("decision_context"))
            st.markdown("---")

        if step == 4:
            _step_title_with_framework(
                4,
                "NIST CSF Mapping",
                "NIST CSF",
                NIST_CSF_HOVER,
                NIST_CSF_URL,
            )

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
            _step_title_with_framework(
                6,
                "PFCE Analysis",
                "PFCE",
                PFCE_HOVER,
                PFCE_URL,
            )

            pfce_items = case["ethical"].get("pfce_analysis", [])

            if isinstance(pfce_items, list) and pfce_items and isinstance(pfce_items[0], dict):
                for p in pfce_items:
                    principle = p.get("principle", "TBD")
                    definition = PFCE_DEFINITIONS.get(principle, "")
                    desc = p.get("description", "TBD")

                    if definition:
                        st.markdown(
                            f"""
- <span title="{html.escape(definition)}"
    style="font-weight:700; text-decoration: underline; cursor: help;">{html.escape(principle)}</span>: {html.escape(desc)}
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(f"- **{principle}**: {desc}")
            else:
                _render_bullets(pfce_items)

            st.markdown("---")

        if step == 7:
            st.header("7. Institutional and Governance Constraints")
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

        if step == 8:
            st.header("8. Decision")
            st.write(case["decision_outcome"].get("decision"))
            st.markdown("---")

        if step == 9:
            st.header("9. Outcomes and Implications")
            _render_bullets(case["decision_outcome"].get("outcomes_implications"))
            st.markdown("---")

        # Navigation controls (Previous | Exit | Next)
        col_prev, col_spacer1, col_exit, col_spacer2, col_next = st.columns([1, 2, 1.2, 2, 1])


        with col_prev:
            if step > 1 and st.button("◀ Previous", key=f"cb_prev_{step}_{case_id}"):
                st.session_state["cb_step"] = max(1, step - 1)
                _safe_rerun()

        with col_exit:
            if st.button("Exit Walkthrough", key=f"cb_exit_walkthrough_{case_id}", use_container_width=True):
                st.session_state["cb_view"] = "select"
                _safe_rerun()

        with col_next:
            if step < 9:
                if st.button(
                    "Next ▶",
                    key=f"cb_next_{step}_{case_id}",
                    use_container_width=True,
                ):
                    st.session_state["cb_step"] = min(9, step + 1)
                    _safe_rerun()
            else:
                st.info("End of Case.")


        return
