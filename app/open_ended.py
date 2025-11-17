import streamlit as st
from datetime import datetime

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
import textwrap

from logic.loaders import (
    load_csf_data,
    load_pfce_crosswalk,
    load_pfce_principles,
    load_constraints,
)
from logic.reasoning import apply_crosswalk, summarize_pfce


def _safe_rerun():
    """Compat helper for rerunning the app across Streamlit versions."""
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    except Exception:
        pass


# ------------------------------
# Data loading / indexing helpers
# ------------------------------

@st.cache_data
def _load_core_data():
    csf = load_csf_data()
    crosswalk = load_pfce_crosswalk()
    pfce = load_pfce_principles()
    constraints = load_constraints()
    return csf, crosswalk, pfce, constraints


CSF_DATA, PFCE_CROSSWALK, PFCE_PRINCIPLES, GOV_CONSTRAINTS_RAW = _load_core_data()
PFCE_NAMES = [p.get("name", "") for p in PFCE_PRINCIPLES if p.get("name")]


def _index_csf(csf_raw):
    """
    Normalize CSF data into three structures:

    - FUNC_OPTIONS:          [(func_id, func_label), ...]
    - CATS_BY_FUNC[func_id]: [(cat_id, cat_label), ...]
    - SUBS_BY_CAT[cat_id]:   [(sub_id, sub_label), ...]
    """

    # Accept either {"functions": [...]} or [...] as the top level
    if isinstance(csf_raw, dict):
        functions = csf_raw.get("functions", []) or []
    elif isinstance(csf_raw, list):
        functions = csf_raw
    else:
        functions = []

    func_options = []
    cats_by_func = {}
    subs_by_cat = {}

    for fn in functions:
        func_id = fn.get("id")
        if not func_id:
            continue

        func_title = fn.get("title") or fn.get("name") or ""
        func_label = f"{func_id} – {func_title}" if func_title else func_id

        # store as (id, label) tuple
        func_options.append((func_id, func_label))

        categories = fn.get("categories", []) or []
        cat_tuples = []

        for cat in categories:
            cat_id = cat.get("id")
            if not cat_id:
                continue

            cat_title = cat.get("title") or cat.get("name") or ""
            cat_label = f"{cat_id} – {cat_title}" if cat_title else cat_id

            # store category as tuple
            cat_tuples.append((cat_id, cat_label))

            # Your JSON uses "outcomes" instead of "subcategories"
            outcomes = cat.get("outcomes") or cat.get("subcategories") or []
            sub_tuples = []

            for item in outcomes:
                sub_id = item.get("id")
                if not sub_id:
                    continue

                desc = item.get("outcome") or item.get("description") or ""
                sub_label = f"{sub_id} – {desc}" if desc else sub_id

                # store outcome/subcategory as tuple
                sub_tuples.append((sub_id, sub_label))

            subs_by_cat[cat_id] = sub_tuples

        cats_by_func[func_id] = cat_tuples

    return func_options, cats_by_func, subs_by_cat


FUNC_OPTIONS, CATS_BY_FUNC, SUBS_BY_CAT = _index_csf(CSF_DATA)


def _normalize_constraints(raw):
    """Ensure constraints is a flat list of strings."""
    if isinstance(raw, list):
        return [str(x) for x in raw]
    if isinstance(raw, dict):
        if isinstance(raw.get("constraints"), list):
            return [str(x) for x in raw["constraints"]]
        return [str(v) for v in raw.values()]
    return []


GOV_CONSTRAINTS = _normalize_constraints(GOV_CONSTRAINTS_RAW)


# ------------------------------
# Hinting logic for CSF Function
# ------------------------------

CSF_HINT_KEYWORDS = {
    # Govern
    "GV": [
        "policy", "policies", "authority", "approval", "oversight",
        "governance", "charter", "compliance", "board", "council"
    ],
    # Identify
    "ID": [
        "inventory", "inventories", "classify", "classification",
        "asset", "assets", "dependency", "dependencies",
        "risk register", "risk assessment"
    ],
    # Protect
    "PR": [
        "access", "permission", "privilege", "authorization",
        "encrypt", "encryption", "credential", "password",
        "data protection", "control", "controls", "configuration"
    ],
    # Detect
    "DE": [
        "monitor", "monitoring", "alert", "alerts", "anomaly",
        "anomalies", "flagged", "suspicious", "detection", "log review"
    ],
    # Respond
    "RS": [
        "disconnect", "isolate", "contain", "mitigate", "shutdown",
        "shut down", "take offline", "incident response", "triage",
        "manual control", "disable automation", "block traffic"
    ],
    # Recover
    "RC": [
        "restore", "restoration", "rebuild", "recover", "back online",
        "return to operations", "post-incident review", "lessons learned"
    ],
}


def guess_csf_function(decision_text: str) -> str | None:
    """Best-effort, non-prescriptive guess of the primary CSF function from decision wording."""
    if not decision_text:
        return None

    text = decision_text.lower()
    scores = {fn: 0 for fn in CSF_HINT_KEYWORDS.keys()}

    for fn, keywords in CSF_HINT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[fn] += 1

    # If everything scored 0, no useful hint
    if all(score == 0 for score in scores.values()):
        return None

    # Return the function with the highest score
    return max(scores, key=scores.get)


# ------------------------------
# Option vocabularies
# ------------------------------

TRIGGER_TYPE_OPTIONS = [
    "Ransomware or malware activation",
    "Unauthorized access or account compromise",
    "Vulnerability exploitation",
    "Service or system outage",
    "Data exposure or potential breach",
    "Anomalous telemetry or sensor readings",
    "Malicious or unsafe AI system behavior",
    "Vendor platform failure or misconfiguration",
    "Suspicious network traffic or lateral movement",
    "Other (not listed here)",
]

DECISION_TYPE_OPTIONS = [
    "Shut down or isolate a system",
    "Maintain, reduce, or reroute operations",
    "Grant, restrict, or revoke access",
    "Disconnect or disable automation",
    "Engage or escalate to vendor support",
    "Pay or refuse an extortion or ransom demand",
    "Switch to manual control or fallback mode",
    "Notify or withhold information from leadership/public",
    "Apply a patch, reconfiguration, or policy change",
    "Other (not listed here)",
]

ETHICAL_TRIGGER_OPTIONS = [
    "Potential harm to residents or service users",
    "Potential harm to critical services (e.g., police, fire, water)",
    "Disproportionate impact on vulnerable populations",
    "Risks to employees or internal staff",
    "Privacy or confidentiality concerns",
    "Risks to public trust or legitimacy",
    "Legal or regulatory exposure",
    "Other ethical concerns",
]


# ------------------------------
# Open-Ended Mode UI
# ------------------------------

def render_open_ended():
    st.markdown("## Open-Ended Mode")

    # Maintain a simple step index in session_state
    if "oe_step" not in st.session_state:
        st.session_state["oe_step"] = 1
    step = st.session_state["oe_step"]

    st.caption(
        "This guided flow walks through the same eight-element structure used in the case reconstructions, "
        "one question at a time."
    )

    st.progress(step / 9.0)

    # ---------------- Step 1: Technical Trigger ----------------
    if step >= 1:
        st.markdown("### 1. Technical Trigger")
        st.caption(
            "What type of technical event set this decision in motion? "
            "Select one or more, then add a sentence if helpful."
        )

        trigger_types = st.multiselect(
            "Technical event type(s)",
            options=TRIGGER_TYPE_OPTIONS,
            key="oe_trigger_types",
        )

        technical_trigger = st.text_area(
            "Optional: Add 1–2 sentences of technical context",
            key="oe_technical_trigger",
            height=90,
            placeholder=(
                "Example: A ransomware payload was activated on a shared file server hosting multiple "
                "departmental shares, locking staff out of key operational systems."
            ),
        )

        st.markdown("---")

    # ---------------- Step 2: Technical Decision Point ----------------
    if step >= 2:
        st.markdown("### 2. Technical Decision Point")
        st.caption(
            "What must be decided in technical terms? Select the decision type, then describe the specific choice."
        )

        decision_type = st.selectbox(
            "Primary decision type",
            options=DECISION_TYPE_OPTIONS,
            key="oe_decision_type",
        )

        technical_decision = st.text_area(
            "Describe the specific choice in your own words (1–2 sentences)",
            key="oe_technical_decision",
            height=90,
            placeholder=(
                "Example: Decide whether to disconnect the AI platform and revert to manual control, "
                "or maintain limited automated operations while investigating the anomaly."
            ),
        )

        # Compute and store a CSF function hint based on the decision wording
        suggested_func_id = guess_csf_function(technical_decision)
        st.session_state["oe_suggested_func"] = suggested_func_id

        st.markdown("---")

    # ---------------- Step 3: Technical Mapping (NIST CSF 2.0) ----------------
    if step >= 3:
        st.markdown("### 3. Technical Mapping (NIST CSF 2.0)")
        st.caption(
            "Map this decision into the NIST CSF 2.0 structure. "
            "Select the primary function, then refine to category and outcome(s)."
        )

        # Function selection with hint
        func_ids = [fid for fid, _ in FUNC_OPTIONS]
        func_labels = {fid: lbl for fid, lbl in FUNC_OPTIONS}

        hinted = st.session_state.get("oe_suggested_func")
        # Use hint only if widget not yet set
        if "oe_csf_function" in st.session_state and st.session_state["oe_csf_function"] in func_ids:
            selected_func_id = st.selectbox(
                "Primary CSF function for this decision",
                options=func_ids,
                format_func=lambda fid: func_labels.get(fid, fid),
                key="oe_csf_function",
            )
        else:
            # If we have a hint and it is valid, use it as the default index
            if hinted in func_ids:
                default_index = func_ids.index(hinted)
            else:
                default_index = 0
            selected_func_id = st.selectbox(
                "Primary CSF function for this decision",
                options=func_ids,
                index=default_index,
                format_func=lambda fid: func_labels.get(fid, fid),
                key="oe_csf_function",
            )

        if hinted and hinted in func_labels:
            st.info(
                f"Suggested based on your decision description: **{func_labels[hinted]}**. "
                "You can change this if it does not fit."
            )

        # Category selection (filtered by function)
        cat_options = CATS_BY_FUNC.get(selected_func_id, [])
        cat_ids = [cid for cid, _ in cat_options]
        cat_labels = {cid: lbl for cid, lbl in cat_options}

        selected_cat_id = st.selectbox(
            "Category",
            options=cat_ids if cat_ids else ["(no categories defined)"],
            format_func=lambda cid: cat_labels.get(cid, cid),
            key="oe_csf_category",
        )

        # Subcategory selection (filtered by category)
        subs = SUBS_BY_CAT.get(selected_cat_id, [])
        sub_ids = [sid for sid, _ in subs]
        sub_labels = {sid: lbl for sid, lbl in subs}

        selected_sub_ids = st.multiselect(
            "Subcategories (outcomes most directly involved in this decision)",
            options=sub_ids,
            format_func=lambda sid: sub_labels.get(sid, sid),
            key="oe_csf_subcategories",
        )

        st.caption(
            "Optional: briefly explain why these CSF outcomes are most relevant to this decision."
        )
        csf_rationale = st.text_area(
            "CSF rationale (optional)",
            key="oe_csf_rationale",
            height=90,
        )

        # 3b. Optional PFCE mapping via crosswalk
        pfce_auto = []
        if selected_sub_ids and PFCE_CROSSWALK:
            matches = apply_crosswalk(selected_sub_ids, PFCE_CROSSWALK)
            st.markdown("#### CSF → PFCE Ethical Hints")
            for m in matches:
                csf_id = m.get("csf_id", "")
                outcome = m.get("csf_outcome", "")
                pfce = m.get("pfce", []) or []
                rationale = m.get("rationale", "")

                if csf_id or outcome:
                    st.markdown(f"**{csf_id} – {outcome}**".strip(" –"))

                if pfce:
                    st.markdown("• Suggested principles: " + ", ".join(pfce))
                    pfce_auto.extend(pfce)
                if rationale:
                    st.markdown(f"_Why this matters_: {rationale}")
                st.markdown("---")
        else:
            pfce_auto = []

        st.markdown("---")
    else:
        # If we haven't reached Step 3 yet, no auto PFCE hints
        pfce_auto = []

    # ---------------- Step 4: Ethical Trigger ----------------
    if step >= 4:
        st.markdown("### 4. Ethical Trigger")
        st.caption(
            "Who or what might be harmed, burdened, or treated unfairly by this decision?"
        )

        ethical_trigger_tags = st.multiselect(
            "Who or what is most affected?",
            options=ETHICAL_TRIGGER_OPTIONS,
            key="oe_ethical_trigger_tags",
        )

        ethical_trigger = st.text_area(
            "Optional: Add 1–2 sentences describing why this is more than a purely technical choice",
            key="oe_ethical_trigger",
            height=100,
        )

        st.markdown("---")

    # ---------------- Step 5: Ethical Tension ----------------
    if step >= 5:
        st.markdown("### 5. Ethical Tension")
        st.caption(
            "State the main ethical tension as a trade-off between two justified but competing obligations."
        )

        ethical_tension = st.text_area(
            "Express the tension as: obligation A **vs.** obligation B",
            key="oe_ethical_tension",
            height=110,
            placeholder=(
                "Example: Restore public-facing systems as quickly as possible "
                "vs. preserve forensic evidence and avoid rewarding extortion."
            ),
        )

        st.markdown("---")

    # ---------------- Step 6: Ethical Mapping (PFCE) ----------------
    if step >= 6:
        st.markdown("### 6. Ethical Mapping (Principlist Framework for Cybersecurity Ethics)")
        st.caption(
            "Select the PFCE principles that are most relevant in this dilemma. "
            "Suggestions (if any) are based on the CSF outcomes you selected."
        )

        pfce_auto_unique = []
        for p in pfce_auto:
            if p in PFCE_NAMES and p not in pfce_auto_unique:
                pfce_auto_unique.append(p)

        selected_pfce = st.multiselect(
            "PFCE principles",
            options=PFCE_NAMES,
            default=pfce_auto_unique,
            key="oe_pfce_principles",
        )

        st.caption("Optional: explain how these principles interact in this dilemma.")
        pfce_rationale = st.text_area(
            "PFCE rationale (optional)",
            key="oe_pfce_rationale",
            height=100,
        )

        st.markdown("---")

    # ---------------- Step 7: Institutional and Governance Constraints ----------------
    if step >= 7:
        st.markdown("### 7. Institutional and Governance Constraints")
        st.caption("Document the institutional or governance factors that shape or limit your options.")

        selected_constraints = st.multiselect(
            "Constraints (select any that apply)",
            options=GOV_CONSTRAINTS,
            key="oe_constraints",
        )

        other_constraints = st.text_area(
            "Other constraints (optional)",
            key="oe_constraints_other",
            height=90,
        )

        st.markdown("---")

    # ---------------- Step 8: Decision Outcome ----------------
    if step >= 8:
        st.markdown("### 8. Decision Outcome")
        st.caption(
            "Record the decision taken (or proposed). "
            "This should match the technical decision but in clear, operational terms."
        )

        decision_outcome = st.text_area(
            "Decision taken / recommended",
            key="oe_decision_outcome",
            height=110,
        )

        st.markdown("---")

    # ---------------- Step 9: Ethical Implications ----------------
    if step >= 9:
        st.markdown("### 9. Ethical Implications")
        st.caption(
            "Reflect on the ethical implications of this decision within the constraints you documented."
        )

        ethical_implications = st.text_area(
            "Who is helped, who is harmed, and what is at stake long-term?",
            key="oe_ethical_implications",
            height=130,
        )

        st.markdown("---")

    # ---------------- Navigation + Summary ----------------

    nav_col1, nav_col2 = st.columns([1, 1])

    # Previous button – hidden on first step
    with nav_col1:
        if step > 1:
            if st.button("◀ Previous", key=f"oe_prev_{step}"):
                st.session_state["oe_step"] = max(1, step - 1)
                _safe_rerun()
    # Next / Summary button
    with nav_col2:
        if step < 9:
            if st.button("Next ▶", key=f"oe_next_{step}"):
                st.session_state["oe_step"] = min(9, step + 1)
                _safe_rerun()
        else:
            # Final step – build a PDF reasoning summary from collected inputs

            # Pull fields from session_state
            incident_title       = st.session_state.get("oe_incident_title", "")
            role                 = st.session_state.get("oe_role", "")
            municipality         = st.session_state.get("oe_municipality", "")
            notes                = st.session_state.get("oe_notes", "")
            technical_trigger    = st.session_state.get("oe_technical_trigger", "")
            technical_decision   = st.session_state.get("oe_technical_decision", "")
            ethical_trigger      = st.session_state.get("oe_ethical_trigger", "")
            ethical_tension      = st.session_state.get("oe_ethical_tension", "")
            constraints          = st.session_state.get("oe_constraints", "")
            decision             = st.session_state.get("oe_decision", "")
            rationale            = st.session_state.get("oe_rationale", "")

            # --- Build PDF ---
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=LETTER)
            width, height = LETTER

            left_margin   = 72
            right_margin  = 72
            top_margin    = 72
            bottom_margin = 72
            line_height   = 14

            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawCentredString(
                width / 2,
                height - top_margin,
                "Municipal Cyber Ethics Reasoning Summary"
            )

            pdf.setLineWidth(0.5)
            pdf.line(
                left_margin,
                height - top_margin - 8,
                width - right_margin,
                height - top_margin - 8,
            )

            y = height - top_margin - 24

            def draw_wrapped_text(text, indent=0, wrap_width=95):
                nonlocal y
                pdf.setFont("Helvetica", 11)
                text = text or "—"
                for line in textwrap.wrap(text, width=wrap_width):
                    if y < bottom_margin + line_height:
                        pdf.showPage()
                        _draw_header()
                    pdf.drawString(left_margin + indent, y, line)
                    y -= line_height

            def draw_section_heading(title):
                nonlocal y
                if y < bottom_margin + 30:
                    pdf.showPage()
                    _draw_header()
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(left_margin, y, title)
                y -= line_height
                pdf.setLineWidth(0.3)
                pdf.line(left_margin, y + 4, width - right_margin, y + 4)
                y -= (line_height // 2)

            def _draw_header():
                nonlocal y
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawCentredString(
                    width / 2,
                    height - top_margin + 8,
                    "Municipal Cyber Ethics Reasoning Summary",
                )
                pdf.setLineWidth(0.3)
                pdf.line(
                    left_margin,
                    height - top_margin - 2,
                    width - right_margin,
                    height - top_margin - 2,
                )
                y = height - top_margin - 24

            # --- Sections ---
            draw_section_heading("Metadata")
            draw_wrapped_text(
                f"Timestamp: {datetime.now().isoformat(timespec='minutes')}",
                indent=10,
            )
            draw_wrapped_text(f"Incident Title: {incident_title}", indent=10)
            draw_wrapped_text(
                f"Role / Organization: {role} / {municipality}", indent=10
            )

            draw_section_heading("Technical Context")
            draw_wrapped_text(
                f"Technical Trigger: {technical_trigger}", indent=10
            )
            draw_wrapped_text(
                f"Technical Decision Point: {technical_decision}", indent=10
            )

            draw_section_heading("Ethical Context")
            draw_wrapped_text(
                f"Ethical Trigger: {ethical_trigger}", indent=10
            )
            draw_wrapped_text(
                f"Ethical Tension(s): {ethical_tension}", indent=10
            )

            draw_section_heading("Institutional & Governance Constraints")
            draw_wrapped_text(constraints, indent=10)

            draw_section_heading("Decision-Making Context")
            draw_wrapped_text(
                f"Operational Decision: {decision}", indent=10
            )
            draw_wrapped_text(
                f"Ethical–Technical Reasoning: {rationale}", indent=10
            )

            draw_section_heading("Additional Notes")
            draw_wrapped_text(notes, indent=10)

            # Footer
            pdf.setFont("Helvetica-Oblique", 9)
            pdf.drawCentredString(
                width / 2,
                bottom_margin / 2,
                "Generated via Municipal Cyber Ethics Decision-Support Prototype – Open-Ended Mode",
            )

            pdf.save()
            buffer.seek(0)

            st.download_button(
                label="Download Reasoning Summary (PDF)",
                data=buffer,
                file_name="reasoning_summary.pdf",
                mime="application/pdf",
            )

   
      
