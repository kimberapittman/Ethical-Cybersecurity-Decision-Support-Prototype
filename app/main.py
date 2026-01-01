import sys
from pathlib import Path
import textwrap
import html

# -*- coding: utf-8 -*-

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from logic.loaders import list_cases, load_case
from app import case_based, open_ended

# ---------- Page config ----------
st.set_page_config(
    page_title="Municipal Cyber Ethics Decision-Support",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown(
    """
<style>
/* === Font (Inter) + base tokens === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class^="css"] {
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji"!important;
}

/* tokens */
:root{
  --brand: #378AED;     /* Real-World Incident */
  --brand-2: #55CAFF;   /* Hypothetical Scenario */
  --bg-soft: #0b1020;
  --text-strong: #111827;
  --text-muted: #6b7280;
  --card-bg: #f9fbff;
  --card-border: var(--brand);
}
@media (prefers-color-scheme: dark){
  :root{
    --text-strong: #e5e7eb;
    --text-muted: #94a3b8;
    --card-bg: rgba(255,255,255,0.05);
  }
}

/* App background */
div[data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 600px at 10% -10%, rgba(76,139,245,0.15), transparent 60%),
              radial-gradient(900px 500px at 100% 0%, rgba(122,168,255,0.10), transparent 60%),
              var(--bg-soft);
  --text-strong: #e5e7eb;
  --text-muted: #94a3b8;
  --card-bg: rgba(255,255,255,0.05);
}

/* Force ALL Streamlit buttons (wrapper + button) to fill their container */
div[data-testid="stButton"]{
  width: 100% !important;
}

/* Force buttons to truly occupy the full column width (prevents shrink-to-fit in narrow layouts) */
div[data-testid="stButton"] > button {
  min-width: 100% !important;
  box-sizing: border-box !important;
}

/* Navigation buttons: Previous / Next should size to content */
.nav-button > div[data-testid="stButton"] > button {
  width: auto !important;
  padding-left: 1.2rem;
  padding-right: 1.2rem;
}

div[data-testid="stButton"] > button,
div[data-testid="stButton"] button{
  width: 100% !important;
  max-width: 100% !important;
  display: block !important;
  white-space: nowrap !important;
}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  border-right: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(6px);
}
section[data-testid="stSidebar"] *{
  color: var(--text-strong) !important;
}

/* --- FIX: allow long sidebar text/URLs to wrap so the resizer doesn't "snap" --- */
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] span{
  overflow-wrap: anywhere !important;
  word-break: break-word !important;
  white-space: normal !important;
}

/* Header container */
.block-container > div:first-child{
  backdrop-filter: blur(6px);
  border-radius: 14px;
  padding: 8px 14px;
  border: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
}

/* Cards */
.listbox{
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
  border-left: 4px solid var(--brand);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 10px 24px rgba(0,0,0,0.25);
  padding: 12px 14px;
  border-radius: 14px;
  margin: 8px 0 16px;
}
.listbox, .listbox *{ color: var(--text-strong) !important; }
.tight-list{ margin: 0.25rem 0 0 1.15rem; padding: 0; }
.tight-list li{ margin: 6px 0; }
.tight-list li::marker{ color: var(--text-muted); }

/* === Step tile wrapper inside walkthrough === */
div[data-testid="stVerticalBlock"]:has(.step-tile-anchor){
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
  border-left: 4px solid var(--brand);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 10px 24px rgba(0,0,0,0.25);
  padding: 12px 14px;
  border-radius: 14px;
  margin: 8px 0 16px;
}

/* Section captions */
.section-note, .sub{ color: var(--text-muted) !important; }

/* Buttons */
.stButton > button{
  border: 0;
  padding: 0.7rem 1rem;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: white !important;
  box-shadow: 0 10px 20px rgba(76,139,245,0.35);
  transition: transform .06s ease, box-shadow .15s ease, filter .15s ease;
}
.stButton > button:hover{
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(76,139,245,0.45);
  filter: brightness(1.05);
}
.stButton > button:active{ transform: translateY(0); }

/* Inputs */
input, textarea, select, .stTextInput input, .stTextArea textarea{
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  color: var(--text-strong) !important;
  border-radius: 10px !important;
}
label, .stRadio, .stSelectbox, .stMultiSelect, .stExpander{
  color: var(--text-strong) !important;
}

/* === Clickable tile affordances === */
.listbox {
  transition:
    transform 0.12s ease,
    box-shadow 0.12s ease,
    border-color 0.12s ease,
    background 0.12s ease;
}

/* --- Case type badges --- */
.case-badge-wrap{
  width:100% !important;
  display:flex !important;
  justify-content:center !important;
  margin: 0 0 10px 0 !important;
}

.case-badge{
  display:inline-flex !important;
  align-items:center !important;
  justify-content:center !important;
  font-size:0.72rem !important;
  font-weight:800 !important;
  letter-spacing:0.02em !important;
  padding:7px 14px !important;
  border-radius:999px !important;
  white-space:nowrap !important;
  color:#ffffff !important;
}

/* Real-World Incident = darker blue */
.case-badge.real{
  background-color:#378AED !important;
  border:1px solid #378AED !important;
}

/* Hypothetical Scenario = lighter blue */
.case-badge.hypo{
  background-color:#55CAFF !important;
  border:1px solid #55CAFF !important;
}

/* Hover = discoverable click */
.listbox:hover {
  cursor: pointer;
  transform: translateY(-2px);
  box-shadow: 0 16px 34px rgba(0, 0, 0, 0.35);
  border-color: rgba(76, 139, 245, 0.65);
}

/* Active = confirmation of click */
.listbox:active {
  transform: translateY(0);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.25);
}

/* Expander headers */
details > summary{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 12px;
  padding: 10px 12px;
  color: var(--text-strong);
}

/* Checkbox / radio accent color */
input[type="checkbox"], input[type="radio"]{ accent-color: var(--brand); }

/* Hide Streamlit chrome */
header[data-testid="stHeader"]{ background: transparent; }
footer, #MainMenu{ visibility: hidden; }

/* === Consistent faint divider (for st.markdown("---")) === */
div[data-testid="stMarkdownContainer"] hr {
  border: none !important;
  height: 1px !important;
  background: rgba(255,255,255,0.14) !important;
  margin: 22px 0 18px 0 !important;
  opacity: 1 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def html_block(s: str) -> str:
    # Prevent Markdown from treating indented HTML as a code block.
    return "\n".join(line.lstrip() for line in textwrap.dedent(s).splitlines())


def _enter_mode(mode: str):
    st.session_state["active_mode"] = mode
    st.session_state["landing_complete"] = True
    # no st.rerun() — Streamlit reruns automatically on button click


def _open_sidebar_once():
    if st.session_state.get("_sidebar_opened_once", False):
        return
    st.session_state["_sidebar_opened_once"] = True

    st.markdown(
        """
        <script>
        (function () {
          const btn = window.parent.document.querySelector('button[data-testid="collapsedControl"]');
          if (btn) btn.click();
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )


def main():
    if "landing_complete" not in st.session_state:
        st.session_state["landing_complete"] = False

    if "active_mode" not in st.session_state:
        st.session_state["active_mode"] = "Case-Based"

    _open_sidebar_once()


def _render_landing_page():
    st.markdown(
        """
    <div style='text-align:center; margin-top: 0.5rem;'>
      <h2 style='margin-bottom:0.35rem; display:inline-block;'>
        Select a Mode
      </h2>
    </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            html_block(
                """
                <a href="?mode=Case-Based&start=walkthrough" target="_self"
                  style="text-decoration:none; color: inherit; display:block;">
                  <div class="listbox" style="cursor:pointer;">

                    <div style="font-weight:700; font-size:1.1rem; margin-bottom:6px; text-align:center;">
                      Case-Based Mode
                    </div>

                    <div class="sub" style="text-align:center; margin-bottom:12px;">
                      <em>Explore the prototype through reconstructed case demonstrations.</em>
                    </div>

                    <div class="sub" style="margin-bottom:10px;">
                      Uses reconstructed municipal cybersecurity cases to demonstrate how the decision-support prototype structures ethical reasoning and technical decision-making across an entire decision process.
                    </div>

                    <ul class="tight-list">
                      <li>Pre-structured cases reconstructed from documented municipal incidents</li>
                      <li>Walks through defined decision points and ethical triggers</li>
                      <li>Shows how CSF procedural logic and PFCE reasoning are applied in practice</li>
                      <li>Establishes a shared reference point for how the prototype is intended to be used</li>
                    </ul>

                  </div>
                </a>
                """
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            html_block(
                """
                <a href="?mode=Open-Ended&start=walkthrough" target="_self"
                  style="text-decoration:none; color: inherit; display:block;">
                  <div class="listbox" style="cursor:pointer;">

                    <div style="font-weight:700; font-size:1.1rem; margin-bottom:6px; text-align:center;">
                      Open-Ended Mode
                    </div>

                    <div class="sub" style="text-align:center; margin-bottom:12px;">
                      <em>Utilize the prototype for a decision context you define.</em>
                    </div>

                    <div class="sub" style="margin-bottom:10px;">
                      Provides a structured walkthrough for analyzing the ethical significance of a user-defined cybersecurity decision, without prescribing outcomes.
                    </div>

                    <ul class="tight-list">
                      <li>User-defined decision context</li>
                      <li>Supports identification of ethical significance and competing obligations</li>
                      <li>Structures reasoning using CSF procedural context and PFCE principles</li>
                      <li>Documents ethical reasoning to support transparency and defensibility</li>
                    </ul>

                  </div>
                </a>
                """
            ),
            unsafe_allow_html=True,
        )

    st.stop()


def render_app_header(compact: bool = False):
    # Case walkthrough header: show CASE TITLE only, then the same blue divider
    in_case_walkthrough = st.session_state.get("cb_view") == "walkthrough"
    if in_case_walkthrough:
        case_id = st.session_state.get("cb_case_id")
        case = load_case(case_id) or {}
        case_title = case.get("ui_title", case_id) if case_id else ""

        st.markdown(
            f"""
            <div style='text-align:center;'>
              <h2 style='margin-bottom:0.25rem;'>{html.escape(str(case_title))}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Existing header behavior (unchanged)
        if compact:
            st.markdown(
                """
                <div style='text-align:center;'>
                  <h2 style='margin-bottom:0.25rem;'>🛡️ Municipal Cyber Ethics Decision-Support Prototype</h2>
                  <div style="font-size:0.75rem; font-weight:800; letter-spacing:0.01em; color:#4C8BF5; margin-top:0.1rem;">
                    Because what's secure isn't always what's right.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style='text-align:center;'>
                  <h1>🛡️ Municipal Cyber Ethics Decision-Support Prototype</h1>
                  <div style="font-size:2.0rem; font-weight:800; letter-spacing:0.01em; color:#4C8BF5; margin-top:0.25rem;">
                    Because what's secure isn't always what's right.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # one consistent divider everywhere (UNCHANGED)
    st.markdown(
        """
        <hr style='
            margin: 14px 0 20px 0;
            border: none;
            height: 2px;
            background: linear-gradient(
                90deg,
                rgba(76,139,245,0.15),
                rgba(76,139,245,0.55),
                rgba(76,139,245,0.15)
            );
        '>
        """,
        unsafe_allow_html=True,
    )


def main():
    # ---------- SESSION STATE DEFAULTS ----------
    if "landing_complete" not in st.session_state:
        st.session_state["landing_complete"] = False

    if "active_mode" not in st.session_state:
        st.session_state["active_mode"] = "Case-Based"

    # ---------- URL PARAM MODE ENTRY (tile click) ----------
    try:
        qp = st.query_params

        # existing params
        mode_qp = qp.get("mode", None)
        start_qp = qp.get("start", None)

        # NEW: case tile selection param
        cb_case_id_qp = qp.get("cb_case_id", None)

        # If a case was clicked, force Case-Based walkthrough for that case
        if cb_case_id_qp:
            st.session_state["active_mode"] = "Case-Based"
            st.session_state["landing_complete"] = True

            st.session_state["cb_case_id"] = cb_case_id_qp
            st.session_state["cb_prev_case_id"] = cb_case_id_qp

            # go straight into walkthrough
            st.session_state["cb_view"] = "walkthrough"
            st.session_state["cb_step"] = 1
            st.session_state.pop("cb_step_return", None)

            try:
                st.query_params.clear()
            except Exception:
                pass

        # Otherwise, handle your existing mode tiles
        elif mode_qp in ("Case-Based", "Open-Ended"):
            st.session_state["active_mode"] = mode_qp
            st.session_state["landing_complete"] = True

            if start_qp == "walkthrough":
                if mode_qp == "Case-Based":
                    # Case-Based must select a case first (tile selector lives in case_based.py)
                    st.session_state["cb_view"] = "select"
                else:
                    if st.session_state.get("oe_step", 0) == 0:
                        st.session_state["oe_step"] = 1

            try:
                st.query_params.clear()
            except Exception:
                pass

    except Exception:
        pass
    

    # ---------- SIDEBAR (ALWAYS) ----------
    with st.sidebar:
        # Prototype Overview (always visible)
        st.markdown(
            "<h3 style='margin:0 0 0.5rem 0; font-weight:700;'>Prototype Overview</h3>",
            unsafe_allow_html=True,
        )

        with st.expander("ℹ️ About This Prototype"):
            st.markdown(
                """
        <span style="font-weight:700; border-bottom:2px solid rgba(255,255,255,0.6); padding-bottom:2px;">
        What It Is
        </span>

        - A decision-support prototype designed to help municipal cybersecurity practitioners surface and reason through ethical tensions that may arise within cybersecurity decision-making  
        - Focused on structuring ethical and technical reasoning, not prescribing actions or determining outcomes  

        <br>

        <span style="font-weight:700; border-bottom:2px solid rgba(255,255,255,0.6); padding-bottom:2px;">
        How It Works
        </span>

        - Guides practitioners through a structured, step-by-step reasoning walkthrough implemented in two complementary modes:  

          <strong>Case-Based Mode</strong>  
          Uses reconstructed municipal cybersecurity cases to demonstrate the walkthrough and illustrate how the prototype was developed through analysis of real-world incidents. 

          <strong>Open-Ended Mode</strong>  
          Applies the same walkthrough to a user-defined cybersecurity decision context and represents the intended use of the prototype.

        - Across both modes, the walkthrough is structured to surface and document:  
          - A triggering condition and decision context  
          - Where the decision sits procedurally within the <strong>NIST Cybersecurity Framework (CSF) 2.0</strong>  
          - The ethical tension raised by the decision context and how it can be articulated using the <strong>Principlist Framework for Cybersecurity Ethics (PFCE)</strong>  
          - Institutional and governance constraints that shape feasible response options  
                """,
                unsafe_allow_html=True,
            )


        st.markdown("---")

        # Appendix (always visible)
        st.markdown(
            "<h3 style='margin:0 0 0.5rem 0; font-weight:700;'>Appendix</h3>",
            unsafe_allow_html=True,
        )

        with st.expander("📚 Framework References"):
            st.markdown(
                """
        <a href="https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf"
          target="_blank"
          title="Open the NIST Cybersecurity Framework (CSF) 2.0 (PDF)"
          style="
            font-weight:800;
            color: white;
            text-decoration-line: underline;
            text-decoration-color: white;
            text-decoration-thickness: 2px;
            text-underline-offset: 4px;
          ">
        NIST Cybersecurity Framework (CSF) 2.0
        </a><br>
        National Institute of Standards and Technology (2024)

        <a href="https://doi.org/10.1016/j.cose.2021.102382"
          target="_blank"
          title="Open the Principlist Framework for Cybersecurity Ethics journal article"
          style="
            font-weight:800;
            color: white;
            text-decoration-line: underline;
            text-decoration-color: white;
            text-decoration-thickness: 2px;
            text-underline-offset: 4px;
          ">
        Principlist Framework for Cybersecurity Ethics (PFCE)
        </a><br>
        Formosa, Paul; Michael Wilson; Deborah Richards (2021)<br>

        <em>(Access to the full text may depend on institutional or publisher subscriptions.)</em>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

    # ---------- HEADER (ALWAYS) ----------
    in_case_walkthrough = st.session_state.get("cb_view") == "walkthrough"
    in_open_walkthrough = st.session_state.get("oe_step", 0) > 0


    render_app_header(compact=in_case_walkthrough or in_open_walkthrough)

    # ---------- LANDING GATE (shown on fresh app load; not on reruns after selection) ----------
    if not st.session_state.get("landing_complete", False):
        _render_landing_page()

    mode = st.session_state.get("active_mode", "Case-Based")

    # Ensure Case-Based uses tile selector by default (prevents dropdown page)
    if mode == "Case-Based" and "cb_view" not in st.session_state:
        st.session_state["cb_view"] = "select"


    # ---------- MODE-SPECIFIC EXPLAINERS (MAIN AREA) ----------
    cb_view = st.session_state.get("cb_view", "collapsed")

    if mode == "Case-Based" and cb_view == "collapsed":
        st.markdown(
            "<h2 style='text-align: center; margin-top: 0.25rem;'>Case-Based Mode</h2>",
            unsafe_allow_html=True,
        )

    elif mode != "Case-Based":
        st.markdown(
            "<h2 style='text-align: center; margin-top: 0.25rem;'>Open-Ended Mode</h2>",
            unsafe_allow_html=True,
        )

    # ---------- CASE SELECTOR (Case-Based Only) ----------
    if mode == "Case-Based" and cb_view == "collapsed":
        cases = list_cases()

        if not cases:
            st.error("No cases found in data/cases.")
        else:
            case_titles = [c.get("ui_title", c["title"]) for c in cases]

            # Initialize selection + id once
            if "cb_case_title" not in st.session_state:
                st.session_state["cb_case_title"] = case_titles[0]

            if "cb_case_id" not in st.session_state:
                first = next(c for c in cases if c["title"] == st.session_state["cb_case_title"])
                st.session_state["cb_case_id"] = first["id"]

            def _on_case_change():
                new_title = st.session_state["cb_case_title"]
                new_case = next(c for c in cases if c["title"] == new_title)

                # Store id + reset navigation immediately
                st.session_state["cb_case_id"] = new_case["id"]
                st.session_state["cb_step"] = 1
                st.session_state["cb_prev_case_id"] = new_case["id"]
                st.session_state["cb_view"] = "walkthrough"

            st.markdown("### Select A Case")
            st.selectbox(
                "Case selection",
                options=case_titles,
                key="cb_case_title",
                label_visibility="collapsed",
                on_change=_on_case_change,
            )


    # ---------- ROUTING ----------
    if mode == "Case-Based":
        case_based.render_case(st.session_state.get("cb_case_id"))
    else:
        open_ended.render_open_ended()

    if not (in_case_walkthrough or in_open_walkthrough):
        st.markdown("---")

    show_change_mode = (
        st.session_state.get("landing_complete", False)
        and not (in_case_walkthrough or in_open_walkthrough)
    )

    # --- Centered Change Mode button (responsive-safe) ---
    if show_change_mode:
        col_left, col_center, col_right = st.columns([2, 1, 2])
        with col_center:
            if st.button("Change Mode", key="change_mode_main", use_container_width=True):
                st.session_state["landing_complete"] = False
                st.rerun()

    st.markdown(
        """
        <div style="
            text-align:center;
            opacity:0.7;
            font-size:0.85rem;
            padding: 0.25rem 0 0.75rem 0;
        ">
            This prototype is designed for research and demonstration purposes and is not intended for operational deployment
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
