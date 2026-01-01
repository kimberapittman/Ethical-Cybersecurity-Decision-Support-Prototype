import streamlit as st
from logic.loaders import load_case, list_cases
import html
import textwrap

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


CASE_HOOKS = {
    "baltimore": "Preventing harm while sustaining essential public services",
    "sandiego": "Protecting public safety while respecting autonomy and public oversight",
    "riverton": "Delegating control to automated systems without relinquishing human responsibility",
}


def _step_tile_open(title: str):
    st.markdown(
        f"""
        <div class="listbox" style="padding: 18px 18px 10px 18px;">
          <div style="font-weight:800; font-size:1.15rem; margin-bottom:10px; text-align:left;">
            {html.escape(title)}
          </div>
        """,
        unsafe_allow_html=True,
    )

def _step_tile_close():
    st.markdown("</div>", unsafe_allow_html=True)


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


        if not top_cases:
            st.error("No cases found in data/cases.")
            return

        cols = st.columns(3, gap="large")

        for col, c in zip(cols, top_cases):
            cid = c.get("id", "")
            title = c.get("ui_title") or c.get("title", "TBD")
            cid_norm = str(cid).strip().lower()
            hook = CASE_HOOKS.get(cid_norm, "")


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
                                '<div class="sub" style="text-align:center; margin-top:6px; font-size:0.95rem; line-height:1.25;">'
                                + html.escape(hook)
                                + '</div>'
                            ) if hook else ""}
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

        def _bullets_md(value) -> str:
            if value is None:
                return "TBD"
            if isinstance(value, list):
                return "\n".join([f"- {item}" for item in value]) if value else "TBD"
            return str(value)

        def _render_step_tile(inner_md: str):
            st.markdown(
                f"""
                <div class="listbox">
                {inner_md}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.progress(step / 9.0)

        if step == 1:
            inner = f"## 1. Technical and Operational Background\n\n{_bullets_md(case['background'].get('technical_operational_background'))}"
            _render_step_tile(inner)

        if step == 2:
            inner = f"## 2. Triggering Condition and Key Events\n\n{_bullets_md(case['background'].get('triggering_condition_key_events'))}"
            _render_step_tile(inner)

        if step == 3:
            inner = f"## 3. Decision Context\n\n{_bullets_md(case['technical'].get('decision_context'))}"
            _render_step_tile(inner)

        if step == 4:
            mapping = case["technical"].get("nist_csf_mapping", [])
            if mapping:
                lines = []
                for m in mapping:
                    fn = m.get("function", "TBD")

                    cats = m.get("categories", [])
                    if isinstance(cats, str):
                        cats = [cats]
                    cat_text = ", ".join(cats) if cats else "TBD"

                    lines.append(f"- **{fn} — {cat_text}**")
                    if m.get("rationale"):
                        lines.append(f"_Rationale_: {m.get('rationale')}")
                mapping_md = "\n".join(lines)
            else:
                mapping_md = "TBD"

            # Keep your framework title behavior (tooltip + link) as-is, but inside the tile
            tooltip_link = (
                f'<a href="{html.escape(NIST_CSF_URL)}" target="_blank" style="text-decoration: none;">'
                f'  <span title="{html.escape(NIST_CSF_HOVER)}" '
                f'        style="font-weight: 800; text-decoration: underline; cursor: help;">'
                f'    NIST CSF'
                f'  </span>'
                f'</a>'
            )
            inner = f"## 4. NIST CSF Mapping\n\n{mapping_md}"
            inner = inner.replace("NIST CSF", tooltip_link, 1)
            _render_step_tile(inner)

        if step == 5:
            tensions = case["ethical"].get("tension", [])
            if tensions:
                tension_md = "\n".join([f"- {t.get('description', 'TBD')}" for t in tensions])
            else:
                tension_md = "TBD"
            inner = f"## 5. Ethical Tension\n\n{tension_md}"
            _render_step_tile(inner)

        if step == 6:
            pfce_items = case["ethical"].get("pfce_analysis", [])

            # Title with PFCE tooltip/link preserved
            tooltip_link = (
                f'<a href="{html.escape(PFCE_URL)}" target="_blank" style="text-decoration: none;">'
                f'  <span title="{html.escape(PFCE_HOVER)}" '
                f'        style="font-weight: 800; text-decoration: underline; cursor: help;">'
                f'    PFCE'
                f'  </span>'
                f'</a>'
            )

            if isinstance(pfce_items, list) and pfce_items and isinstance(pfce_items[0], dict):
                lines = []
                for p in pfce_items:
                    principle = p.get("principle", "TBD")
                    definition = PFCE_DEFINITIONS.get(principle, "")
                    desc = p.get("description", "TBD")

                    if definition:
                        lines.append(
                            f'- <span title="{html.escape(definition)}" '
                            f'style="font-weight:700; text-decoration: underline; cursor: help;">'
                            f'{html.escape(principle)}</span>: {html.escape(desc)}'
                        )
                    else:
                        lines.append(f"- **{principle}**: {desc}")
                pfce_md = "\n".join(lines)
            else:
                pfce_md = _bullets_md(pfce_items)

            inner = f"## 6. PFCE Analysis\n\n{pfce_md}"
            inner = inner.replace("PFCE", tooltip_link, 1)
            _render_step_tile(inner)

        if step == 7:
            constraints = case.get("constraints", [])
            if constraints:
                lines = []
                for c in constraints:
                    if isinstance(c, dict):
                        lines.append(f"- **{c.get('type','TBD')}** – {c.get('description','TBD')}")
                        if c.get("effect_on_decision"):
                            lines.append(f"  \n  _Effect on decision_: {c.get('effect_on_decision')}")
                    else:
                        lines.append(f"- {c}")
                constraints_md = "\n".join(lines)
            else:
                constraints_md = "TBD"

            inner = f"## 7. Institutional and Governance Constraints\n\n{constraints_md}"
            _render_step_tile(inner)

        if step == 8:
            inner = f"## 8. Decision\n\n{_bullets_md(case['decision_outcome'].get('decision'))}"
            _render_step_tile(inner)

        if step == 9:
            inner = f"## 9. Outcomes and Implications\n\n{_bullets_md(case['decision_outcome'].get('outcomes_implications'))}"
            _render_step_tile(inner)

        # ONE divider between tile and nav (matches Select a Case layout)
        st.markdown("<hr style='margin: 18px 0 14px 0; opacity: 0.35;'>", unsafe_allow_html=True)

        # Navigation controls (Previous | Exit | Next)
        col_prev, col_spacer1, col_exit, col_spacer2, col_next = st.columns([1, 2, 2.2, 2, 1])

        with col_prev:
            if step > 1 and st.button("◀ Previous", key=f"cb_prev_{step}_{case_id}", use_container_width=True):
                st.session_state["cb_step"] = max(1, step - 1)
                _safe_rerun()

        with col_exit:
            if st.button(
                "Exit Walkthrough",
                key=f"cb_exit_walkthrough_{case_id}",
                use_container_width=True
            ):
                st.session_state["cb_view"] = "select"
                _safe_rerun()

        with col_next:
            st.markdown('<div class="nav-button">', unsafe_allow_html=True)

            if step < 9:
                if st.button("Next ▶", key=f"cb_next_{step}_{case_id}"):
                    st.session_state["cb_step"] = min(9, step + 1)
                    _safe_rerun()
            else:
                st.info("End of Case.")

            st.markdown('</div>', unsafe_allow_html=True)

    return