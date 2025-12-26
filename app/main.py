main.py 12.26

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

# App-level modules

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


def main():
    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.markdown(
            "<h3 style='margin:0 0 0.5rem 0; font-weight:700;'>Mode</h3>",
            unsafe_allow_html=True,
        )
        mode = st.radio(
            label="Prototype mode",
            options=["Case-Based", "Open-Ended"],
            index=0,
            key="mode_selector",
            label_visibility="collapsed",
        )

        # --- Reset state when switching modes ---
        if "last_mode" not in st.session_state:
            st.session_state["last_mode"] = mode

        if st.session_state["last_mode"] != mode:
            # Clear Case-Based state when leaving/entering Case-Based
            for k in list(st.session_state.keys()):
                if k.startswith("cb_"):
                    del st.session_state[k]

            st.session_state["last_mode"] = mode
            st.rerun()

        st.markdown("---")

        # Prototype Overview
        st.markdown(
            "<h3 style='margin:0 0 0.5rem 0; font-weight:700;'>Prototype Overview</h3>",
            unsafe_allow_html=True,
        )

        with st.expander("ℹ️ About This Prototype"):
            st.markdown(
                """
**Purpose:** This prototype is a software-based decision-support artifact designed to help municipal cybersecurity practitioners reason through ethical tensions that arise within cybersecurity decision-making. It supports structured ethical reasoning alongside technical decision-making by making ethically significant conditions, competing obligations, and institutional and governance constraints explicit. The prototype does not prescribe decisions or evaluate outcomes; instead, it provides a structured means of documenting and justifying ethical reasoning within real-world municipal cybersecurity contexts.

**How it works:** The prototype integrates the procedural logic of the NIST Cybersecurity Framework (CSF) 2.0 with the normative, non-prescriptive reasoning of the Principlist Framework for Cybersecurity Ethics (PFCE). The CSF is used to situate decisions within the cybersecurity lifecycle and clarify the technical decision context, while the PFCE is used to surface ethically significant principles, tensions, and obligations associated with that context.
                """
            )

        st.markdown("---")

        # Appendix
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

    # ---------- MAIN HEADER ----------
    st.markdown(
        """
    <div style='text-align: center;'>
    <h1>🛡️ Municipal Cyber Ethics Decision-Support Prototype</h1>
    <h4 style='color:#4C8BF5;'>Because what's secure isn't always what's right.</h4>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ---------- MODE-SPECIFIC EXPLAINERS (MAIN AREA) ----------
    cb_view = st.session_state.get("cb_view", "collapsed")

    if mode == "Case-Based" and cb_view == "collapsed":
        st.markdown(
            "<h2 style='text-align: center; margin-top: 0.25rem;'>Case-Based Mode</h2>",
            unsafe_allow_html=True,
        )

        with st.expander("About Case-Based Mode"):
            st.markdown(
                """
Case-Based Mode presents analytically structured municipal cybersecurity cases used to demonstrate how the prototype’s decision-support logic operates.

Each case is derived from the Chapter III analysis and organized to surface the decision-relevant elements necessary for structured reasoning, rather than to reproduce the full narrative detail of the dissertation. Users can step through each case to observe how technical context, ethical significance, and organizational conditions interact within a single cybersecurity decision process.

The purpose of this mode is not to evaluate historical decisions or prescribe outcomes, but to illustrate how ethical reasoning can be made explicit, structured, and traceable when cybersecurity decisions are examined systematically.
                """
            )

        st.divider()

    elif mode != "Case-Based":
        st.markdown(
            "<h2 style='text-align: center; margin-top: 0.25rem;'>Open-Ended Mode</h2>",
            unsafe_allow_html=True,
        )

        with st.expander("About Open-Ended Mode"):
            st.markdown(
                """
Open-Ended Mode allows users to apply the prototype’s reasoning structure to new or unfolding cybersecurity situations.

Rather than working from a pre-constructed case, users enter decision-specific information drawn from their own operational context and are guided through the same structured reasoning sequence demonstrated in Case-Based Mode. This enables exploration of how ethical significance, technical context, and institutional conditions interact within decisions that may not yet be fully defined or resolved.

The purpose of this mode is not to generate decisions or recommendations, but to support disciplined ethical reasoning by making assumptions, constraints, and value tensions explicit as cybersecurity practitioners work through complex situations.
                """
            )

    # ---------- CASE SELECTOR (Case-Based Only) ----------
    selected_case = None

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
                first = next(
                    c for c in cases if c["title"] == st.session_state["cb_case_title"]
                )
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
