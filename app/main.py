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
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji" !important;
}

/* === Tokens === */
:root{
  --brand: #378AED;     /* Real-World Incident */
  --brand-2: #55CAFF;   /* Hypothetical Scenario */
  --bg-soft: #0b1020;
  --text-strong: #e5e7eb;
  --text-muted: #94a3b8;
  --card-bg: rgba(255,255,255,0.05);
}

/* === App background === */
div[data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 600px at 10% -10%, rgba(76,139,245,0.15), transparent 60%),
              radial-gradient(900px 500px at 100% 0%, rgba(122,168,255,0.10), transparent 60%),
              var(--bg-soft);
}

/* === Sidebar === */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  border-right: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(6px);
}
section[data-testid="stSidebar"] *{
  color: var(--text-strong) !important;
}
/* Allow long sidebar text/URLs to wrap */
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] span{
  overflow-wrap: anywhere !important;
  word-break: break-word !important;
  white-space: normal !important;
}

/* === Header container === */
.block-container > div:first-child{
  backdrop-filter: blur(6px);
  border-radius: 14px;
  padding: 8px 14px;
  border: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
}

/* === Buttons === */
div[data-testid="stButton"] > button{
  min-width: 100% !important;
  box-sizing: border-box !important;
  border: 0;
  padding: 0.7rem 1rem;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: white !important;
  box-shadow: 0 10px 20px rgba(76,139,245,0.35);
  transition: transform .06s ease, box-shadow .15s ease, filter .15s ease;
  white-space: nowrap !important;
}
div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(76,139,245,0.45);
  filter: brightness(1.05);
}
div[data-testid="stButton"] > button:active{ transform: translateY(0); }

/* Ghost nav button (Back to Mode Selection) */
div[data-testid="stButton"] > button[kind="secondary"]{
  background: rgba(255,255,255,0.06) !important;
  box-shadow: none !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover{
  transform: none !important;
  filter: none !important;
  box-shadow: none !important;
}

/* Back to Mode Selection — size to text cleanly */
div[data-testid="stButton"] > button[kind="secondary"]{
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;

  width: auto !important;
  min-width: unset !important;

  padding: 0.45rem 0.9rem !important;
  line-height: 1.2 !important;

  white-space: nowrap !important;
}

/* === Inputs === */
input, textarea, select, .stTextInput input, .stTextArea textarea{
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  color: var(--text-strong) !important;
  border-radius: 10px !important;
}
label, .stRadio, .stSelectbox, .stMultiSelect, .stExpander{
  color: var(--text-strong) !important;
}

/* === Cards / tiles === */
.listbox{
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
  border-left: 4px solid var(--brand);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 10px 24px rgba(0,0,0,0.25);
  padding: 12px 14px;
  border-radius: 14px;
  margin: 0 0 8px;
  transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease, background 0.12s ease;
}
.listbox, .listbox *{ color: var(--text-strong) !important; }
.section-note, .sub{ color: var(--text-muted) !important; }

/* Click affordances */
.listbox:hover{
  cursor: pointer;
  transform: translateY(-2px);
  box-shadow: 0 16px 34px rgba(0,0,0,0.35);
  border-color: rgba(76,139,245,0.65);
}
.listbox:active{
  transform: translateY(0);
  box-shadow: 0 10px 20px rgba(0,0,0,0.25);
}

/* === Bullet list inside tiles === */
.tight-list{ margin: 0.25rem 0 0 1.15rem; padding: 0; }
.tight-list li{ margin: 6px 0; }
.tight-list li::marker{ color: var(--text-muted); }

/* === Case badges === */
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
  padding:10px 14px !important;
  border-radius:999px !important;
  white-space:nowrap !important;
  color:#ffffff !important;
}
.case-badge.real{ background-color:#378AED !important; border:1px solid #378AED !important; }
.case-badge.hypo{ background-color:#55CAFF !important; border:1px solid #55CAFF !important; }

/* === Expanders === */
details > summary{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 12px;
  padding: 10px 12px;
  color: var(--text-strong);
}

/* === Layout: unify Mode + Case tile rows === */

/* Make columns stretch */
div[data-testid="stHorizontalBlock"]{ align-items: stretch !important; }

/* Only on pages that include mode/case anchors: make columns + tiles equal height */
div[data-testid="stVerticalBlock"]:has(.mode-tiles-anchor) div[data-testid="column"],
div[data-testid="stVerticalBlock"]:has(.case-tiles-anchor) div[data-testid="column"]{
  display: flex !important;
  flex-direction: column !important;
}
div[data-testid="stVerticalBlock"]:has(.mode-tiles-anchor) a,
div[data-testid="stVerticalBlock"]:has(.case-tiles-anchor) a{
  display: block !important;
  height: 100% !important;
}
div[data-testid="stVerticalBlock"]:has(.mode-tiles-anchor) .listbox,
div[data-testid="stVerticalBlock"]:has(.case-tiles-anchor) .listbox{
  display: flex !important;
  flex-direction: column !important;
  height: 100% !important;
}

/* Fixed height ONLY for Select-a-Mode (if you still want it) */
.mode-tiles .listbox{ height: 460px !important; }

/* Mobile: don't force tall cards */
@media (max-width: 900px){
  .mode-tiles .listbox{ height: auto !important; }
}

/* === Step tile wrapper inside walkthrough === */
div[data-testid="stVerticalBlock"]:has(.step-tile-anchor){
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
  border-left: 4px solid var(--brand);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 10px 24px rgba(0,0,0,0.25);
  padding: 12px 14px;
  border-radius: 14px;
  margin: 8px 0 8px;
}

/* =========================
   DISCLAIMER FOOTER
   ========================= */

/* Inline disclaimer (normal flow) */
.disclaimer-inline{
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 10px 24px rgba(0,0,0,0.25);
  border-radius: 14px;
  padding: 10px 14px;
  text-align: center;
  color: rgba(229,231,235,0.85);
  margin-top: 18px;
}

/* Pinned disclaimer (viewport bottom) */
.disclaimer-fixed{
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 14px;
  width: min(1100px, calc(100% - 48px));
  z-index: 9999;
  pointer-events: none; /* do not block clicks */
}

.disclaimer-fixed .disclaimer-inner{
  pointer-events: auto;
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 10px 24px rgba(0,0,0,0.25);
  border-radius: 14px;
  padding: 10px 14px;
  text-align: center;
  color: rgba(229,231,235,0.85);
}

/* CRITICAL: reserve space so fixed footer doesn't overlap bottom content */
div[data-testid="stAppViewContainer"] .block-container{
  padding-bottom: 110px !important;
}

/* Visible pill */
.disclaimer-fixed .disclaimer-inner{
  pointer-events: auto;
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 10px 24px rgba(0,0,0,0.25);
  border-radius: 14px;
  padding: 10px 14px;
  text-align: center;
  color: rgba(229,231,235,0.85);
}

/* Spacer so content never hides behind footer */
.disclaimer-spacer{
  height: 84px;
}

/* === Hide Streamlit chrome === */
header[data-testid="stHeader"]{ background: transparent; }
footer, #MainMenu{ visibility: hidden; }

/* Hide header anchor icons */
div[data-testid="stMarkdownContainer"] h1 a,
div[data-testid="stMarkdownContainer"] h2 a,
div[data-testid="stMarkdownContainer"] h3 a,
div[data-testid="stMarkdownContainer"] h4 a,
div[data-testid="stMarkdownContainer"] h5 a,
div[data-testid="stMarkdownContainer"] h6 a{
  display: none !important;
  visibility: hidden !important;
}
button[aria-label*="Copy link"],
button[title*="Copy link"]{
  display: none !important;
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


def render_disclaimer_footer(pinned: bool = False):
    txt = "This prototype is designed for research and demonstration purposes and is not intended for operational deployment"

    if pinned:
        st.markdown(
            f"""
            <div class="disclaimer-spacer"></div>
            <div class="disclaimer-fixed">
              <div class="disclaimer-inner">
                {html.escape(txt)}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="disclaimer-inline">
              {html.escape(txt)}
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_landing_page():
    st.markdown(
        """
    <div style='text-align:center; margin-top: 0; margin-bottom: 0;'>
    <h2 style='margin:0 0 0.1rem 0; display:inline-block;'>
        Select a Mode
    </h2>
    </div>

    <div class="mode-tiles">
      <div class="mode-tiles-anchor"></div>
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

                    <!-- Collapsible details (inside tile) -->
                    <details
                      style="margin-top: 8px;"
                      onclick="event.stopPropagation();"
                    >
                      <summary
                        style="user-select:none;"
                        onclick="event.stopPropagation();"
                      >
                        About Case-Based Mode
                      </summary>

                      <div class="sub" style="margin-top:10px; margin-bottom:10px;">
                        Uses reconstructed municipal cybersecurity cases to demonstrate how the decision-support prototype structures ethical reasoning and technical decision-making across an entire decision process.
                      </div>

                      <ul class="tight-list">
                        <li>Pre-structured cases reconstructed from documented municipal incidents</li>
                        <li>Walks through defined decision points and ethical triggers</li>
                        <li>Shows how CSF procedural logic and PFCE reasoning are applied in practice</li>
                        <li>Establishes a shared reference point for how the prototype is intended to be used</li>
                      </ul>
                    </details>

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

                    <!-- Collapsible details (inside tile) -->
                    <details
                      style="margin-top: 8px;"
                      onclick="event.stopPropagation();"
                    >
                      <summary
                        style="user-select:none;"
                        onclick="event.stopPropagation();"
                      >
                        About Open-Ended Mode
                      </summary>

                      <div class="sub" style="margin-top:10px; margin-bottom:10px;">
                        Provides a structured walkthrough for analyzing the ethical significance of a user-defined cybersecurity decision, without prescribing outcomes.
                      </div>

                      <ul class="tight-list">
                        <li>User-defined decision context</li>
                        <li>Supports identification of ethical significance and competing obligations</li>
                        <li>Structures reasoning using CSF procedural context and PFCE principles</li>
                        <li>Documents ethical reasoning to support transparency and defensibility</li>
                      </ul>
                    </details>

                  </div>
                </a>
                """
            ),
            unsafe_allow_html=True,
        )


def render_app_header(compact: bool = False):
    # --- Back to Mode Selection (secondary nav) ---
    show_back = st.session_state.get("landing_complete", False)

    in_case_select = (
        st.session_state.get("active_mode") == "Case-Based"
        and st.session_state.get("cb_view") == "select"
    )
    in_case_walkthrough = (st.session_state.get("cb_view") == "walkthrough")
    in_open_ended = (st.session_state.get("active_mode") == "Open-Ended")

    if show_back and (in_case_select or in_case_walkthrough or in_open_ended):
        col_left, col_spacer = st.columns([1, 6])
        with col_left:
            if st.button("← Back to Mode Selection", key="back_to_modes", type="secondary"):
                st.session_state["landing_complete"] = False
                st.session_state.pop("cb_view", None)
                st.session_state.pop("cb_case_id", None)
                st.session_state.pop("cb_prev_case_id", None)
                st.session_state.pop("cb_step", None)
                st.session_state.pop("oe_step", None)
                st.rerun()

    # --- Header title ---
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

    # --- Divider (unchanged) ---
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

        mode_qp = qp.get("mode", None)
        start_qp = qp.get("start", None)
        cb_case_id_qp = qp.get("cb_case_id", None)

        # If a case was clicked, force Case-Based walkthrough for that case
        if cb_case_id_qp:
            st.session_state["active_mode"] = "Case-Based"
            st.session_state["landing_complete"] = True

            st.session_state["cb_case_id"] = cb_case_id_qp
            st.session_state["cb_prev_case_id"] = cb_case_id_qp

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
        st.markdown("---")
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

    # ---------- LANDING GATE ----------
    if not st.session_state.get("landing_complete", False):
        _render_landing_page()
        render_disclaimer_footer(pinned=True)
        return  # CRITICAL: stop here so the rest of the app doesn't render on the landing screen

    # ---------- CONTINUE APP ----------
    mode = st.session_state.get("active_mode", "Case-Based")

    if mode == "Case-Based" and "cb_view" not in st.session_state:
        st.session_state["cb_view"] = "select"

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

            if "cb_case_title" not in st.session_state:
                st.session_state["cb_case_title"] = case_titles[0]

            if "cb_case_id" not in st.session_state:
                first = next(c for c in cases if c["title"] == st.session_state["cb_case_title"])
                st.session_state["cb_case_id"] = first["id"]

            def _on_case_change():
                new_title = st.session_state["cb_case_title"]
                new_case = next(c for c in cases if c["title"] == new_title)

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

    # ---------- DISCLAIMER (ONLY ON NON-WALKTHROUGH SCREENS) ----------
    in_case_walkthrough = st.session_state.get("cb_view") == "walkthrough"
    in_open_walkthrough = st.session_state.get("oe_step", 0) > 0
    render_disclaimer_footer(pinned=not (in_case_walkthrough or in_open_walkthrough))

if __name__ == "__main__":
    main()
