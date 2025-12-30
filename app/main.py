import sys
from pathlib import Path

# -*- coding: utf-8 -*-

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from logic.loaders import list_cases
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
  --brand: #4C8BF5;
  --brand-2: #7aa8ff;
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

/* Sidebar */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  border-right: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(6px);
}
section[data-testid="stSidebar"] *{
  color: var(--text-strong) !important;
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
</style>
""",
    unsafe_allow_html=True,
)


def _enter_mode(mode: str):
    st.session_state["active_mode"] = mode
    st.session_state["landing_complete"] = True
    st.rerun()


def _render_landing_page():
    st.markdown(
        """
<div style='text-align:center; margin-top: 0.5rem;'>
  <h2 style='margin-bottom:0.35rem;'>Select a Mode</h2>
</div>
        """,
        unsafe_allow_html=True,
    )


    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
<div class="listbox">
  <div style="font-weight:700; font-size:1.1rem; margin-bottom:6px;">Case-Based Mode</div>
  <div class="sub" style="margin-bottom:10px;">
    Uses reconstructed cases to see how the decision-support structure works end-to-end.
  </div>
  <ul class="tight-list">
    <li>Pre-filled case data from Chapter III</li>
    <li>Structured walkthrough across steps</li>
    <li>Demonstrates the prototype’s logic and framing</li>
  </ul>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Enter Case-Based Mode", use_container_width=True, key="enter_case_based"):
            _enter_mode("Case-Based")

    with col2:
        st.markdown(
            """
<div class="listbox">
  <div style="font-weight:700; font-size:1.1rem; margin-bottom:6px;">Open-Ended Mode</div>
  <div class="sub" style="margin-bottom:10px;">
    Apply the structured walkthrough to a new or unfolding cybersecurity dilemma.
  </div>
  <ul class="tight-list">
    <li>User-entered inputs (no prebuilt case)</li>
    <li>CSF procedural framing + PFCE ethical reasoning</li>
    <li>Documents reasoning without prescribing actions</li>
  </ul>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Enter Open-Ended Mode", use_container_width=True, key="enter_open_ended"):
            _enter_mode("Open-Ended")

    st.stop()


def render_app_header(compact: bool = False):
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

    # one consistent divider everywhere
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
        What it is
        </span>

        This prototype is a decision-support tool designed to help municipal cybersecurity practitioners reason through ethically significant cybersecurity decisions.

        It provides a structured walkthrough that helps practitioners:
        - Identify the triggering condition and decision context
        - Recognize why the situation is ethically significant
        - Surface relevant ethical obligations and tensions
        - Account for institutional and governance constraints
        - Document ethical reasoning alongside technical decisions

        <br>

        <span style="font-weight:700; border-bottom:2px solid rgba(255,255,255,0.6); padding-bottom:2px;">
        How it works
        </span>

        The prototype guides practitioners through a step-by-step reasoning process that mirrors real-world cybersecurity decision-making.

        Each step prompts the user to articulate:
        - What triggered the situation and what decision is being faced  
        - How the decision fits procedurally within the cybersecurity lifecycle  
        - Why the situation carries ethical significance  
        - Which ethical principles and tensions are implicated  
        - What institutional or governance conditions constrain feasible responses  

        Technical context is structured using the **NIST Cybersecurity Framework (CSF) 2.0**, while ethical reasoning is supported using the **Principlist Framework for Cybersecurity Ethics (PFCE)**. Together, these frameworks are used to organize and document reasoning—not to prescribe actions or determine outcomes.
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
**National Institute of Standards and Technology.**  
[*The NIST Cybersecurity Framework (CSF) 2.0* (2024)](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf)

**Formosa, Paul, Michael Wilson, and Deborah Richards.**  
[*A Principlist Framework for Cybersecurity Ethics* (2021)](https://doi.org/10.1016/j.cose.2021.102382)
Access to the full text may depend on institutional or publisher subscriptions.
                """
            )
        st.markdown("---")

    # ---------- HEADER (ALWAYS) ----------
    in_case_walkthrough = st.session_state.get("cb_view") == "walkthrough"
    in_open_walkthrough = st.session_state.get("oe_step", 0) > 0

    # Show "Change mode" ONLY when not in a walkthrough
    if st.session_state.get("landing_complete", False) and not (in_case_walkthrough or in_open_walkthrough):
        colA, colB, colC = st.columns([1, 2, 1])
        with colC:
            if st.button("Change mode", key="change_mode_main"):
                st.session_state["landing_complete"] = False
                st.rerun()

    render_app_header(compact=in_case_walkthrough or in_open_walkthrough)


    # ---------- LANDING GATE (shown on fresh app load; not on reruns after selection) ----------
    if not st.session_state.get("landing_complete", False):
        _render_landing_page()

    mode = st.session_state.get("active_mode", "Case-Based")

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
            case_titles = [c["title"] for c in cases]

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

            st.markdown("### Select A Case")
            st.selectbox(
                "Case selection",
                options=case_titles,
                key="cb_case_title",
                label_visibility="collapsed",
                on_change=_on_case_change,
            )

        st.divider()

    # ---------- ROUTING ----------
    if mode == "Case-Based":
        case_based.render_case(st.session_state.get("cb_case_id"))
    else:
        open_ended.render_open_ended()

    st.markdown("---")
    st.caption(
        "This prototype is designed for research and demonstration purposes and is not intended for operational deployment"
    )


if __name__ == "__main__":
    main()
