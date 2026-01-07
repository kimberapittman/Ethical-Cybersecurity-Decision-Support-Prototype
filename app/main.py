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

from logic.loaders import load_case
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
html, body{
  overflow: auto !important;
}

/* === FONT === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, .stApp{
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji" !important;
}


/* === TOKENS === */
:root{
  --brand: #378AED;     /* Real-World Incident */
  --brand-2: #55CAFF;   /* Hypothetical Scenario */
  --bg-soft: #0b1020;
  --text-strong: #e5e7eb;
  --text-muted: #94a3b8;
  --card-bg: rgba(255,255,255,0.05);
}


/* === APP BACKGROUND === */
div[data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 600px at 10% -10%, rgba(76,139,245,0.15), transparent 60%),
              radial-gradient(900px 500px at 100% 0%, rgba(122,168,255,0.10), transparent 60%),
              var(--bg-soft)
}


/* === HEADER CONTAINER === */
.block-container > div:first-child{
  border-radius: 14px;
  padding: 4px 14px 38px 14px;
  border: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
}


/* === SIDEBAR === */
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
/* The whole expander container */
.sb-details{
  background: linear-gradient(
    180deg,
    rgba(255,255,255,0.06),
    rgba(255,255,255,0.03)
  ) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 14px !important;
  padding: 0 !important;
  overflow: hidden !important; /* critical */
}
.sb-details > summary{
  /* layout */
  list-style: none !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  /* visual */
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03)) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 12px !important;
  color: var(--text-strong) !important;
  /* spacing + typography */
  padding: 12px 14px !important; 
  margin: 0 !important;
  font-weight: 700 !important;
  /* behavior */
  cursor: pointer !important;
}
/* Sidebar chevron */
.sb-details > summary::-webkit-details-marker{ display:none !important; }
.sb-details > summary::marker{ content:"" !important; }
.sb-details > summary::before{
  content: ">";
  font-size: 1rem;
  font-weight: 800;
  line-height: 1;
  opacity: 0.8;
  margin-top: -1px;
  transition: transform 0.12s ease, opacity 0.12s ease;
}
.sb-details[open] > summary::before{
  transform: rotate(90deg);
}
/* Body = same container, no new “tile” */
.sb-details-body{
  padding: 12px 14px !important;
  margin: 0 !important;
  border-top: 1px solid rgba(255,255,255,0.08) !important;
}


/* === BUTTONS === */
div[data-testid="stButton"] > button:not([kind="secondary"]){
  box-sizing: border-box !important;
  padding: 0.7rem 1rem !important;
  border-radius: 12px !important;
  background: rgba(255,255,255,0.06) !important;
  color: var(--text-strong) !important;
  border: 1px solid rgba(76,139,245,0.55) !important;
  box-shadow:
    0 0 0 1px rgba(76,139,245,0.35),
    0 10px 20px rgba(76,139,245,0.35) !important;
  transition: transform .06s ease, box-shadow .15s ease, filter .15s ease !important;
  white-space: nowrap !important;
}
div[data-testid="stButton"] > button:not([kind="secondary"]):hover{
  transform: translateY(-3px) !important;
  cursor: pointer;
  box-shadow:
    0 0 0 3px rgba(76,139,245,0.65),
    0 18px 38px rgba(76,139,245,0.45) !important;
  border-color: rgba(76,139,245,0.95) !important;
  filter: brightness(1.05) !important;
}
/* Secondary Buttons */
div[data-testid="stButton"] > button[kind="secondary"]{
  box-sizing: border-box !important;
  padding: 0.7rem 1rem !important;
  border-radius: 12px !important;
  background: rgba(255,255,255,0.06) !important;
  color: var(--text-strong) !important;
  border: 1px solid rgba(76,139,245,0.55) !important;
  box-shadow:
    0 0 0 1px rgba(76,139,245,0.35),
    0 10px 20px rgba(76,139,245,0.35) !important;
  transition: transform .06s ease, box-shadow .15s ease, filter .15s ease !important;
  white-space: nowrap !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover{
  transform: translateY(-3px) !important;
  cursor: pointer;
  box-shadow:
    0 0 0 3px rgba(76,139,245,0.65),
    0 18px 38px rgba(76,139,245,0.45) !important;
  border-color: rgba(76,139,245,0.95) !important;
  filter: brightness(1.05) !important;
}
div[data-testid="stButton"] > button:active{
  transform: translateY(-1px) !important;
  box-shadow:
    0 0 0 1px rgba(76,139,245,0.45),
    0 8px 16px rgba(76,139,245,0.30) !important;
}
div[data-testid="stButton"] > button:disabled{
  opacity: 0.55 !important;
  background: rgba(255,255,255,0.10) !important;
  border: 1px solid rgba(255,255,255,0.22) !important;
  color: var(--text-strong) !important;
  box-shadow: none !important;
  transform: none !important;
  filter: none !important;
}
div[data-testid="stButton"] > button:disabled:hover{
  transform: none !important;
  cursor: default !important;
  box-shadow: none !important;
  border-color: rgba(255,255,255,0.22) !important;
  filter: none !important;
}
/* OPTIONAL: only make “normal” (non-nav) buttons full width */
div[data-testid="stVerticalBlock"]:not(:has(:is(.cb-nav-anchor,.oe-nav-anchor)))
div[data-testid="stButton"] > button{
  width: 100% !important;
      min-width: 100% !important;
}
/* Keyboard focus only (no mouse click outline) */
div[data-testid="stButton"] > button:focus-visible{
  outline: none !important;
  box-shadow:
    0 0 0 3px rgba(76,139,245,0.75),
    0 0 0 6px rgba(76,139,245,0.25) !important;
}


/* === INPUTS === */
input, textarea, select, .stTextInput input, .stTextArea textarea{
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  color: var(--text-strong) !important;
  border-radius: 10px !important;
}
label, .stRadio, .stSelectbox, .stMultiSelect, .stExpander{
  color: var(--text-strong) !important;
}


/* === CARD TILES === */
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
section-note, .tile-hook { color: var(--text-muted) !important; }


/* === SELECT A MODE TILE SPACING ==== */
div[data-testid="stVerticalBlock"]:has(.mode-tiles-anchor)
.listbox.tile-card.mode-tile{
  padding: 30px 30px !important;  
}
/* Title → hook spacing (same as case tiles) */
div[data-testid="stVerticalBlock"]:has(.mode-tiles-anchor)
.listbox.tile-card.mode-tile .tile-title{
  font-weight: 800 !important;
  font-size: 1.25rem !important;
  text-align: center !important;
  margin: 0 0 20px 0 !important;
  line-height: 1.45 !important;
}
div[data-testid="stVerticalBlock"]:has(.mode-tiles-anchor)
.listbox.tile-card.mode-tile .tile-hook{
  text-align: center !important;
  font-size: 1.25rem !important;
  margin: 0 0 20px 0 !important;   
  line-height: 1.45 !important;
}
/* Expanded body: continuous with summary (no "second tile" look) */
div[data-testid="stVerticalBlock"]:has(.mode-tiles-anchor)
.listbox.tile-card.mode-tile details .details-body{
  margin-top: 0 !important;               
  padding: 12px 12px !important;
  background: rgba(255,255,255,0.03) !important;
  border: 0 !important;                     
  border-radius: 0 0 12px 12px !important;   
}
/* Make summary connect flush into body when open */
div[data-testid="stVerticalBlock"]:has(.mode-tiles-anchor)
.listbox.tile-card.mode-tile details[open] > summary{
  border-bottom-left-radius: 0 !important;
  border-bottom-right-radius: 0 !important;
}


/* === SELECT A CASE - TILE SPACING ==== */
/* Tile padding: top and bottom must match */
div[data-testid="stVerticalBlock"]:has(.case-tiles-anchor)
.listbox.case-tile{
  padding: 30px 30px !important;   /* top/bottom symmetry */
}
/* Badge → title spacing */
div[data-testid="stVerticalBlock"]:has(.case-tiles-anchor)
.listbox.case-tile .case-badge-wrap{
  margin: 0 0 20px 0 !important;
}
/* Title styling + Title → hook spacing */
div[data-testid="stVerticalBlock"]:has(.case-tiles-anchor)
.listbox.case-tile .tile-title{
  font-weight: 800 !important;
  font-size: 1.25rem !important;
  text-align: center !important;
  margin: 0 0 20px 0 !important;   
  line-height: 1.45 !important;
}
/* Hook styling; Hook → bottom spacing comes ONLY from tile padding */
div[data-testid="stVerticalBlock"]:has(.case-tiles-anchor)
.listbox.case-tile .tile-hook{
  text-align: center !important;
  font-size: 1.25rem !important;
  margin: 0 0 20px 0 !important;
  line-height: 1.45 !important;
}


/* === TILE CLICK AFFORDANCE === */
/* Click affordances */
.listbox:hover{
  cursor: pointer;
  transform: translateY(-3px);
  box-shadow:
    0 0 0 2px rgba(76,139,245,0.45),
    0 18px 38px rgba(0,0,0,0.45);
  border-color: rgba(76,139,245,0.75);
}
.listbox:active{
  transform: translateY(0);
  box-shadow: 0 10px 20px rgba(0,0,0,0.25);
}


/* === BULLET LISTS INSIDE TILES === */
.tight-list{ margin: 0.25rem 0 0 1.15rem; padding: 0; }
.tight-list li{ margin: 6px 0; }
.tight-list li::marker{ color: var(--text-muted); }


/* === CASE BADGES === */
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
  font-size:0.85rem !important;
  font-weight:800 !important;
  letter-spacing:0.02em !important;
  padding:8px 14px !important;
  border-radius:999px !important;
  white-space:nowrap !important;
  color:#ffffff !important;
}
.case-badge.real{
  background-color: rgba(55,138,237,0.85) !important;
  border: 1px solid rgba(55,138,237,0.85) !important;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.15);
}
.case-badge.hypo{
  background-color: rgba(85,202,255,0.85) !important;
  border: 1px solid rgba(85,202,255,0.85) !important;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.15);
}
/* MAIN CONTENT expanders only (exclude sidebar) */
div[data-testid="stAppViewContainer"]
:not(section[data-testid="stSidebar"])
details > summary{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 12px;
  padding: 10px 12px;
  color: var(--text-strong);
}


/* DETAILS CHEVRON — MODE + CASE TILES (shared) */
div[data-testid="stVerticalBlock"]:has(:is(.mode-tiles-anchor,.case-tiles-anchor)) details > summary::-webkit-details-marker{
  display: none !important;
}
div[data-testid="stVerticalBlock"]:has(:is(.mode-tiles-anchor,.case-tiles-anchor)) details > summary::marker{
  content: "" !important;
}
div[data-testid="stVerticalBlock"]:has(:is(.mode-tiles-anchor,.case-tiles-anchor)) details > summary{
  list-style: none !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  margin: 0 !important;
  padding: 10px 12px !important;
  padding-left: 34px !important;
  position: relative !important;
}
div[data-testid="stVerticalBlock"]:has(:is(.mode-tiles-anchor,.case-tiles-anchor)) details > summary::before{
  content: ">";
  font-weight: 800;
  display: inline-block;
  font-size: 1rem;
  line-height: 1;
  opacity: 0.8;
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%) rotate(0deg);
  transition: transform 0.12s ease;
}
div[data-testid="stVerticalBlock"]:has(:is(.mode-tiles-anchor,.case-tiles-anchor)) details[open] > summary::before{
  transform: translateY(-50%) rotate(90deg);
}


/* === HIDE STREAMLIT CHROME === */
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


/* === WALKTHROUGH TILES: NOT CLICKABLE ==== */
.listbox.walkthrough-tile{
  cursor: default !important;
  margin-top: 12px;
  margin-bottom: 12px !important;
}
.walkthrough-step-title{
  display: inline-block;     
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.4;
  margin: 0 0 0.6rem 0;
  color: var(--text-strong);
}
/* kill the hover/active "clickable" affordance */
.listbox.walkthrough-tile:hover,
.listbox.walkthrough-tile:active{
  cursor: default !important;
  transform: none !important;
  border-color: rgba(255,255,255,0.10) !important;   /* normal */
  box-shadow: 0 10px 24px rgba(0,0,0,0.25) !important; /* normal */
}
/* Optional polish: soften walkthrough tiles slightly */
.listbox.walkthrough-tile{
  box-shadow: 0 8px 18px rgba(0,0,0,0.22) !important;
}
:root{ --disclaimer-h: 56px; }
/* Reserve space so content never hides behind the footer */
div[data-testid="stMainBlockContainer"]{
  padding-bottom: calc(var(--disclaimer-h) + 16px) !important;
}
.disclaimer-overlay{
  position: fixed !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100% !important;
  max-width: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  z-index: 2147483647 !important; /* go nuclear */
  pointer-events: none !important;
}
/* Prevent any ancestor from turning fixed into “fixed inside container” */
div[data-testid="stAppViewContainer"],
div[data-testid="stMain"],
div[data-testid="stMainBlockContainer"],
main{
  transform: none !important;
  filter: none !important;
  perspective: none !important;
}
/* The actual bar */
.disclaimer-footer{
  height: var(--disclaimer-h) !important;
  width: 100% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  background: rgba(11,16,32,0.92) !important;
  border-top: 1px solid rgba(255,255,255,0.10) !important;
  color: rgba(229,231,235,0.75) !important;
  font-size: 0.85rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.01em !important;
  margin: 0 !important;
  padding: 0 12px !important; /* small side padding */
  text-align: center !important;
  pointer-events: none !important;
}
/* === WALKTHROUGH NAV ==== */
/* Only inside the nav row area */
div[data-testid="stVerticalBlock"]:has(:is(.cb-nav-anchor,.oe-nav-anchor))
div[data-testid="stHorizontalBlock"]{
  width: 100% !important;
}
/* Make each column a flex lane */
div[data-testid="stVerticalBlock"]:has(:is(.cb-nav-anchor,.oe-nav-anchor))
div[data-testid="column"]{
  display: flex !important;
}
/* The column inner wrapper must stretch full width */
div[data-testid="stVerticalBlock"]:has(:is(.cb-nav-anchor,.oe-nav-anchor))
div[data-testid="column"] > div{
  width: 100% !important;
  display: flex !important;
}
/* Left lane pinned */
div[data-testid="stVerticalBlock"]:has(:is(.cb-nav-anchor,.oe-nav-anchor))
div[data-testid="column"]:first-child > div{
  justify-content: flex-start !important;
}
/* Right lane pinned */
div[data-testid="stVerticalBlock"]:has(:is(.cb-nav-anchor,.oe-nav-anchor))
div[data-testid="column"]:last-child > div{
  justify-content: flex-end !important;
}
/* Keep nav buttons pill-sized */
div[data-testid="stVerticalBlock"]:has(:is(.cb-nav-anchor,.oe-nav-anchor))
div[data-testid="stButton"] > button{
  width: auto !important;
  min-width: unset !important;
}
/* Stack only when truly narrow */
@media (max-width: 520px){
  div[data-testid="stVerticalBlock"]:has(:is(.cb-nav-anchor,.oe-nav-anchor))
  div[data-testid="column"] > div{
    justify-content: stretch !important;
  }
  div[data-testid="stVerticalBlock"]:has(:is(.cb-nav-anchor,.oe-nav-anchor))
  div[data-testid="stButton"] > button{
    width: 100% !important;
    min-width: 100% !important;
  }
}
</style>
""",
    unsafe_allow_html=True,
)


def html_block(s: str) -> str:
    # Prevent Markdown from treating indented HTML as a code block.
    return "\n".join(line.lstrip() for line in textwrap.dedent(s).splitlines())


def _open_sidebar_once():
    # Only try once per browser session (Streamlit session_state)
    if st.session_state.get("_sidebar_opened_once", False):
        return
    st.session_state["_sidebar_opened_once"] = True

    st.markdown(
        """
        <script>
        (function () {
          const doc = window.parent.document;

          function isCollapsed(sidebarEl) {
            if (!sidebarEl) return false;
            const w = sidebarEl.getBoundingClientRect().width;
            // When collapsed, sidebar width is usually very small (often < ~80px)
            return w < 120;
          }

          function findToggleButton() {
            // Try multiple selectors (Streamlit changes these)
            const selectors = [
              'button[data-testid="collapsedControl"]',
              'button[aria-label="Expand sidebar"]',
              'button[aria-label="Collapse sidebar"]',
              'button[title="Expand sidebar"]',
              'button[title="Collapse sidebar"]',
              // Fallback: any header button with "sidebar" in aria-label/title
              'button[aria-label*="sidebar"]',
              'button[title*="sidebar"]'
            ];

            for (const sel of selectors) {
              const btn = doc.querySelector(sel);
              if (btn) return btn;
            }
            return null;
          }

          function tryOpen(attempt) {
            const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
            const toggle = findToggleButton();

            if (sidebar && toggle && isCollapsed(sidebar)) {
              toggle.click();
              return;
            }

            // Retry while Streamlit finishes layout
            if (attempt < 20) {
              setTimeout(() => tryOpen(attempt + 1), 120);
            }
          }

          tryOpen(0);
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer_footer():
    txt = "This prototype is designed for research and demonstration purposes and is not intended for operational deployment"

    st.markdown(
        f"""
        <div class="disclaimer-overlay">
          <div class="disclaimer-footer">
            {html.escape(txt)}
          </div>
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
                  <div class="listbox tile-card mode-tile" style="cursor:pointer;">

                    <div class="tile-title">Case-Based Mode</div>

                    <div class="tile-hook">Explore the prototype through reconstructed case demonstrations.</div>


                    <!-- Collapsible details (inside tile) -->
                    <details onclick="event.stopPropagation();">
                      <summary style="user-select:none;" onclick="event.stopPropagation();">
                        About Case-Based Mode
                      </summary>

                      <div class="details-body">
                        <div class="mode-detail-text">
                          Uses reconstructed municipal cybersecurity cases to demonstrate how the decision-support prototype structures ethical reasoning and technical decision-making across an entire decision process.
                        </div>

                        <ul class="tight-list">
                          <li>Pre-structured cases reconstructed from documented municipal incidents</li>
                          <li>Walks through defined decision points and ethical triggers</li>
                          <li>Shows how CSF procedural logic and PFCE reasoning are applied in practice</li>
                          <li>Establishes a shared reference point for how the prototype is intended to be used</li>
                        </ul>
                      </div>
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
                  <div class="listbox tile-card mode-tile" style="cursor:pointer;">

                    <div class="tile-title">Open-Ended Mode</div>

                    <div class="tile-hook">Utilize the prototype for a decision context you define.</div>

                    <!-- Collapsible details (inside tile) -->
                    <details onclick="event.stopPropagation();">
                      <summary style="user-select:none;" onclick="event.stopPropagation();">
                        About Open-Ended Mode
                      </summary>

                      <div class="details-body">
                        <div class="mode-detail-text">
                          Provides a structured walkthrough for analyzing the ethical significance of a user-defined cybersecurity decision, without prescribing outcomes.
                        </div>

                        <ul class="tight-list">
                          <li>User-defined decision context</li>
                          <li>Supports identification of ethical significance and competing obligations</li>
                          <li>Structures reasoning using CSF procedural context and PFCE principles</li>
                          <li>Documents ethical reasoning to support transparency and defensibility</li>
                        </ul>
                      </div>
                    </details>

                  </div>
                </a>
                """
            ),
            unsafe_allow_html=True,
        )

    # --- Auto-scroll when opening "About" dropdowns on landing page ---
    st.markdown("""
<script>
(function () {
  const FOOTER_H = 56;   // match --disclaimer-h
  const PAD = 14;

  function isScrollable(el) {
    if (!el) return false;
    const s = getComputedStyle(el);
    const oy = s.overflowY;
    return (oy === "auto" || oy === "scroll") && el.scrollHeight > el.clientHeight + 2;
  }

  function getScrollParent(el) {
    let p = el;
    while (p && p !== document.body) {
      if (isScrollable(p)) return p;
      p = p.parentElement;
    }
    const main = document.querySelector('section[data-testid="stMain"]');
    if (isScrollable(main)) return main;
    return window;
  }

  function scrollIntoViewSmart(target) {
    if (!target) return;

    const scroller = getScrollParent(target);
    const isWindow = (scroller === window);

    const rect = target.getBoundingClientRect();
    const visibleBottom = window.innerHeight - FOOTER_H - PAD;

    // If bottom is below visible viewport (above footer), scroll down
    const down = rect.bottom - visibleBottom;
    if (down > 4) {
      if (isWindow) window.scrollBy({ top: down, behavior: "smooth" });
      else scroller.scrollBy({ top: down, behavior: "smooth" });
    }
  }

  function wire(root) {
    if (!root) return;
    root.querySelectorAll("details").forEach(d => {
      if (d.__autoScrollWired) return;
      d.__autoScrollWired = true;

      d.addEventListener("toggle", () => {
        if (!d.open) return;

        // wait for layout expansion
        let tries = 0;
        const tick = () => {
          tries += 1;
          scrollIntoViewSmart(d);
          if (tries < 6) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      });
    });
  }

  function findRoot() {
    return document.querySelector(".mode-tiles")
      || document.querySelector('div[data-testid="stVerticalBlock"]:has(.mode-tiles-anchor)');
  }

  // Initial wire
  wire(findRoot());

  // Light-touch rewire on rerender (no DOM mutation)
  const obs = new MutationObserver(() => wire(findRoot()));
  obs.observe(document.body, { childList: true, subtree: true });
})();
</script>
    """, unsafe_allow_html=True)


def render_app_header(show_banner: bool = True):
    # --- Back buttons (secondary nav) ---
    show_back = st.session_state.get("landing_complete", False)

    in_case_select = (
        st.session_state.get("active_mode") == "Case-Based"
        and st.session_state.get("cb_view") == "select"
    )
    in_case_walkthrough = (st.session_state.get("cb_view") == "walkthrough")
    in_open_ended = (st.session_state.get("active_mode") == "Open-Ended")

    if show_back and (in_case_select or in_case_walkthrough or in_open_ended):
        st.markdown('<div class="header-nav-anchor"></div>', unsafe_allow_html=True)

        if in_case_walkthrough:
            if st.button("← Back to Case Selection", key="back_to_cases", type="secondary"):
                st.session_state["cb_view"] = "select"
                st.session_state.pop("cb_step", None)
                st.session_state.pop("cb_step_return", None)
                st.rerun()
        else:
            if st.button("← Back to Mode Selection", key="back_to_modes", type="secondary"):
                st.session_state["landing_complete"] = False
                st.session_state.pop("cb_view", None)
                st.session_state.pop("cb_case_id", None)
                st.session_state.pop("cb_prev_case_id", None)
                st.session_state.pop("cb_step", None)
                st.session_state.pop("cb_step_return", None)
                st.session_state.pop("oe_step", None)
                st.rerun()

    # --- Prototype banner (select pages only) ---
    if show_banner:
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

def render_divider():
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

    if st.session_state.get("active_mode") == "Case-Based" and "cb_view" not in st.session_state:
        st.session_state["cb_view"] = "select"

    _open_sidebar_once()

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
    import textwrap

    def html_block(s: str) -> str:
        return "\n".join(line.lstrip() for line in textwrap.dedent(s).splitlines())

    with st.sidebar:
        st.markdown("---")
        st.markdown(
            "<h3 style='margin:0 0 0.5rem 0; font-weight:700;'>Prototype Overview</h3>",
            unsafe_allow_html=True,
        )

        st.markdown(
            html_block(
                """
                <details class="sb-details">
                  <summary>ℹ️ About This Prototype</summary>
                  <div class="sb-details-body">

                    <span style="font-weight:700; border-bottom:2px solid rgba(255,255,255,0.6); padding-bottom:2px;">
                    What It Is
                    </span>

                    <ul style="margin: 8px 0 14px 18px; padding: 0;">
                      <li>A decision-support prototype designed to help municipal cybersecurity practitioners surface and reason through ethical tensions that may arise within cybersecurity decision-making</li>
                      <li>Focused on structuring ethical and technical reasoning, not prescribing actions or determining outcomes</li>
                    </ul>

                    <span style="font-weight:700; border-bottom:2px solid rgba(255,255,255,0.6); padding-bottom:2px;">
                    How It Works
                    </span>

                    <ul style="margin: 8px 0 10px 18px; padding: 0;">
                      <li>Guides practitioners through a structured, step-by-step reasoning walkthrough implemented in two complementary modes:</li>
                    </ul>

                    <div style="margin-left: 18px;">
                      <strong>Case-Based Mode</strong><br>
                      Uses reconstructed municipal cybersecurity cases to demonstrate the walkthrough and illustrate how the prototype was developed through analysis of real-world incidents.
                      <br><br>
                      <strong>Open-Ended Mode</strong><br>
                      Applies the same walkthrough to a user-defined cybersecurity decision context and represents the intended use of the prototype.
                    </div>

                    <ul style="margin: 10px 0 0 18px; padding: 0;">
                      <li>Across both modes, the walkthrough is structured to surface and document:
                        <ul style="margin: 6px 0 0 18px; padding: 0;">
                          <li>A triggering condition and decision context</li>
                          <li>Where the decision sits procedurally within the <strong>NIST Cybersecurity Framework (CSF) 2.0</strong></li>
                          <li>The ethical tension raised by the decision context and how it can be articulated using the <strong>Principlist Framework for Cybersecurity Ethics (PFCE)</strong></li>
                          <li>Institutional and governance constraints that shape feasible response options</li>
                        </ul>
                      </li>
                    </ul>

                  </div>
                </details>
                """
            ),
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(
            "<h3 style='margin:0 0 0.5rem 0; font-weight:700;'>Appendix</h3>",
            unsafe_allow_html=True,
        )

        st.markdown(
            html_block(
                """
                <details class="sb-details">
                  <summary>📚 Framework References</summary>
                  <div class="sb-details-body">

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

                    (Access to the full text may depend on institutional or publisher subscriptions.)

                  </div>
                </details>
                """
            ),
            unsafe_allow_html=True,
        )

        st.markdown("---")


    # ---------- HEADER ----------
    in_case_walkthrough = st.session_state.get("cb_view") == "walkthrough"
    in_open_walkthrough = st.session_state.get("oe_step", 0) > 0
    in_any_walkthrough = in_case_walkthrough or in_open_walkthrough

    # Banner only on select pages
    render_app_header(show_banner=not in_any_walkthrough)

    # Divider rules:
    # - Always show divider on select pages (under banner)
    # - On Open-Ended walkthrough, main.py must show divider under the step title (which will be in open_ended.py or main)
    if not in_any_walkthrough:
        render_divider()


    # ---------- LANDING GATE ----------
    if not st.session_state.get("landing_complete", False):
        _render_landing_page()
        render_disclaimer_footer()
        return
    
    # ---------- ACTIVE MODE ----------
    mode = st.session_state.get("active_mode", "Case-Based")

    if mode == "Case-Based" and "cb_view" not in st.session_state:
        st.session_state["cb_view"] = "select"

    # ---------- ROUTING ----------
    if mode == "Case-Based":
        case_based.render_case(st.session_state.get("cb_case_id"))
    else:
        open_ended.render_open_ended()

    # ---------- DISCLAIMER (ONLY ON SELECTION SCREENS) ----------
    show_disclaimer = (
        st.session_state.get("active_mode") == "Case-Based"
        and st.session_state.get("cb_view") == "select"
    )

    if show_disclaimer:
        render_disclaimer_footer()


if __name__ == "__main__":
    main()