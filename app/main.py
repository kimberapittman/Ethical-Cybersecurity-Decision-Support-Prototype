import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

# App-level modules
from app import case_based, open_ended
from logic.loaders import list_cases

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
        st.markdown("<h3 style='margin:0 0 0.5rem 0; font-weight:700;'>Mode</h3>", unsafe_allow_html=True)
        mode = st.radio(
            label="Prototype mode",
            options=["Case-Based", "Open-ended"],
            index=0,
            key="mode_selector",
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Prototype Overview
        st.markdown("<h3 style='margin:0 0 0.5rem 0; font-weight:700;'>Prototype Overview</h3>", unsafe_allow_html=True)
        with st.expander("ℹ️ About This Prototype"):
            st.markdown(
                """
- **Purpose:** Help municipal cybersecurity practitioners reason through ethical tensions within institutional and governance constraints.  
- **How It Works:** Uses the NIST CSF 2.0 to locate the decision procedurally and the PFCE to clarify ethical values in tension.
                """
            )

        st.markdown("---")

        # Appendix
        st.markdown("<h3 style='margin:0 0 0.5rem 0; font-weight:700;'>Appendix</h3>", unsafe_allow_html=True)
        with st.expander("📚 Framework References"):
            st.markdown(
                """
**National Institute of Standards and Technology.**  
*The NIST Cybersecurity Framework (CSF) 2.0.* (2024)  

**Formosa, Paul, Michael Wilson, and Deborah Richards.**  
"A Principlist Framework for Cybersecurity Ethics." (2021)
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

    # ---------- MODE INTRODUCTION ----------
    if mode == "Case-Based":

        # ⭐ ADD CASE-BASED HEADER HERE (new)
        st.markdown(
            "<h2 style='text-align:center; margin-top:0.25rem;'>Case-Based Mode</h2>",
            unsafe_allow_html=True,
        )

        with st.expander("About Case-Based Mode"):
            st.markdown(
                """
This mode presents analytically reconstructed municipal cybersecurity cases that are used to
demonstrate how ethical reasoning can be supported within real-world technical and institutional contexts.

Each case has been structured around a concrete cybersecurity decision context and organized into
a consistent set of analytical elements, including the technical condition that triggered concern,
the decision context as situated within the NIST Cybersecurity Framework (CSF 2.0), the ethically
significant conditions examined through the Principlist Framework for Cybersecurity Ethics (PFCE),
and the institutional and governance constraints that shaped the range of feasible actions.

Users can walk through each case step-by-step to observe how technical decision contexts,
ethical tensions, and organizational constraints interact over the course of a cybersecurity incident.
The purpose of this mode is not to evaluate historical decisions or prescribe outcomes, but to
illustrate how structured, context-sensitive ethical reasoning can be made explicit and traceable
when cybersecurity decisions are examined in a systematic way.

                """
            )

    else:
        with st.expander("About Open-Ended Mode"):
            st.markdown(
                """
This mode allows users to apply the same structured analytical framework used in the case reconstructions to new or hypothetical municipal cybersecurity decision contexts. Rather than presenting a predefined case, Open-Ended Mode supports practitioner-defined situations in which ethical and technical considerations must be examined as they arise.

User-entered scenarios are organized around a concrete cybersecurity decision context and guided through a consistent set of analytical elements, including the operational conditions that prompted concern, the procedural context as situated within the NIST Cybersecurity Framework (CSF 2.0), the ethically significant conditions examined through the Principlist Framework for Cybersecurity Ethics (PFCE), and the institutional and governance constraints that shape feasible courses of action.

As users move step-by-step through the framework, the mode makes explicit how technical decision contexts, ethical tensions, and organizational constraints interact within a single decision episode. The purpose of Open-Ended Mode is not to determine correct decisions or optimize outcomes, but to demonstrate how structured, context-sensitive ethical reasoning can be surfaced, documented, and made transparent when practitioners confront cybersecurity decisions outside of predefined case material.
                """
            )

    # ---------- CASE SELECTOR (Case-Based Only) ----------
    selected_case = None
    if mode == "Case-Based":
        cases = list_cases()
        if not cases:
            st.error("No cases found in data/cases.")
        else:
            case_titles = [c["title"] for c in cases]
            st.markdown("### Select A Case")
            selected_title = st.selectbox(
                label="Case selection",
                options=case_titles,
                key="case_selector",
                label_visibility="collapsed",
            )
            selected_case = next(c for c in cases if c["title"] == selected_title)

    st.divider()

    # ---------- ROUTING ----------
    if mode == "Case-Based":
        if selected_case:
            case_based.render_case(selected_case["id"])
    else:
        open_ended.render_open_ended()

    st.markdown("---")
    st.caption("Prototype created for thesis demonstration purposes.")


if __name__ == "__main__":
    main()
