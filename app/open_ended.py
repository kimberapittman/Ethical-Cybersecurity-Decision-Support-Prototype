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


# Practitioner-friendly NIST CSF 2.0 function prompts for Open-Ended Mode
CSF_FUNCTION_OPTIONS = {
    "GV": {
        "label": "GOVERN (GV)",
        "prompt": (
            "Are you establishing, reviewing, or implementing cybersecurity policy, "
            "governance expectations, or organizational risk strategy?"
        ),
    },
    "ID": {
        "label": "IDENTIFY (ID)",
        "prompt": (
            "Are you assessing vulnerabilities, reviewing system risks, or determining "
            "what assets or stakeholders are affected?"
        ),
    },
    "PR": {
        "label": "PROTECT (PR)",
        "prompt": (
            "Are you applying safeguards or controls to prevent unauthorized access or "
            "data exposure?"
        ),
    },
    "DE": {
        "label": "DETECT (DE)",
        "prompt": (
            "Have you observed indicators of compromise or suspicious behavior that "
            "require investigation?"
        ),
    },
    "RS": {
        "label": "RESPOND (RS)",
        "prompt": (
            "Has a cybersecurity incident been detected and you must take action "
            "immediately?"
        ),
    },
    "RC": {
        "label": "RECOVER (RC)",
        "prompt": (
            "Are you restoring systems, data, or services after an incident and deciding "
            "what to prioritize or how transparent to be?"
        ),
    },
}


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

        func_options.append((func_id, func_label))

        categories = fn.get("categories", []) or []
        cat_tuples = []

        for cat in categories:
            cat_id = cat.get("id")
            if not cat_id:
                continue

            cat_title = cat.get("title") or cat.get("name") or ""
            cat_label = f"{cat_id} – {cat_title}" if cat_title else cat_id
            cat_tuples.append((cat_id, cat_label))

            outcomes = cat.get("outcomes") or cat.get("subcategories") or []
            sub_tuples = []

            for item in outcomes:
                sub_id = item.get("id")
                if not sub_id:
                    continue

                desc = item.get("outcome") or item.get("description") or ""
                sub_label = f"{sub_id} – {desc}" if desc else sub_id
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
    "GV": ["policy", "policies", "authority", "approval", "oversight", "governance", "charter", "compliance", "board", "council"],
    "ID": ["inventory", "inventories", "classify", "classification", "asset", "assets", "dependency", "dependencies", "risk register", "risk assessment"],
    "PR": ["access", "permission", "privilege", "authorization", "encrypt", "encryption", "credential", "password", "data protection", "control", "controls", "configuration"],
    "DE": ["monitor", "monitoring", "alert", "alerts", "anomaly", "anomalies", "flagged", "suspicious", "detection", "log review"],
    "RS": ["disconnect", "isolate", "contain", "mitigate", "shutdown", "shut down", "take offline", "incident response", "triage", "manual control", "disable automation", "block traffic"],
    "RC": ["restore", "restoration", "rebuild", "recover", "back online", "return to operations", "post-incident review", "lessons learned"],
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

    if all(score == 0 for score in scores.values()):
        return None

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

ETHICAL_CONDITION_TAG_OPTIONS = [
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
# PDF export helper (keeps your imports useful)
# ------------------------------


def _build_pdf(title: str, lines: list[str]) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    x = 54
    y = height - 54

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, title[:120])
    y -= 24

    c.setFont("Helvetica", 10)

    for raw in lines:
        wrapped = textwrap.wrap(raw, width=100) if raw else [""]
        for wline in wrapped:
            if y < 72:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 54
            c.drawString(x, y, wline)
            y -= 14
        y -= 6

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ------------------------------
# Open-Ended Mode UI (aligned to schema)
# ------------------------------


def render_open_ended():
    st.markdown(
        "<h2 style='text-align: center; margin-top: 0.25rem;'>Open-Ended Mode</h2>",
        unsafe_allow_html=True,
    )
    st.caption("Use this mode to walk a new dilemma through the same nine-component structure as the thesis cases.")

    if "oe_step" not in st.session_state:
        st.session_state["oe_step"] = 1
    step = st.session_state["oe_step"]

    st.progress(step / 9.0)

    pfce_auto = st.session_state.get("oe_pfce_auto", [])

    # ---------------- Step 1: Technical & Operational Background ----------------
    if step == 1:
        st.markdown("### 1. Technical and Operational Background")
        st.caption("Describe the technical environment and operational setting that shaped the decision context (brief).")

        st.text_area(
            "Background (optional)",
            key="oe_background",
            height=140,
            placeholder="Example: distributed municipal IT environment; vendor-managed platform; critical infrastructure dependencies; staffing constraints.",
        )
        st.markdown("---")

    # ---------------- Step 2: Triggering Condition & Key Events ----------------
    if step == 2:
        st.markdown("### 2. Triggering Condition and Key Events")
        st.caption("Document the condition that initiated the situation and the key events that established the decision context.")

        st.selectbox(
            "Triggering condition type",
            options=TRIGGER_TYPE_OPTIONS,
            key="oe_trigger_type",
        )

        st.text_area(
            "Triggering condition and key events (1–2 short paragraphs)",
            key="oe_triggering_condition",
            height=160,
            placeholder="Example: system flagged anomalous access; automated restrictions applied; staff notified; logs reviewed; additional alerts observed.",
        )

        st.markdown("---")

    # ---------------- Step 3: Decision Context & NIST CSF Mapping ----------------
    if step == 3:
        st.markdown("### 3. Decision Context and NIST CSF Mapping")
        st.caption("State the decision context in procedural terms, then map it into NIST CSF 2.0.")

        st.selectbox(
            "Primary decision context type (optional)",
            options=DECISION_TYPE_OPTIONS,
            key="oe_decision_type",
        )

        decision_context = st.text_area(
            "Decision context (1–2 sentences)",
            key="oe_decision_context",
            height=110,
            placeholder=(
                "Example: Determine whether to maintain AI-imposed operational restrictions or restore full manual control "
                "while analysts review anomalous alerts."
            ),
        )

        suggested_func_id = guess_csf_function(decision_context)
        st.session_state["oe_suggested_func"] = suggested_func_id

        st.markdown("#### NIST CSF 2.0 mapping")

        option_texts = []
        codes_list = list(CSF_FUNCTION_OPTIONS.keys())
        for code in codes_list:
            meta = CSF_FUNCTION_OPTIONS[code]
            option_texts.append(f"{meta['label']}: {meta['prompt']}")

        default_index = 0
        current_code = st.session_state.get("oe_csf_function")
        if current_code in CSF_FUNCTION_OPTIONS:
            default_index = codes_list.index(current_code)
        elif suggested_func_id in CSF_FUNCTION_OPTIONS:
            default_index = codes_list.index(suggested_func_id)

        selected_option = st.radio(
            "Select the option that best matches your current procedural situation:",
            options=option_texts,
            index=default_index,
            key="oe_csf_choice_step3",
        )

        selected_label_prefix = selected_option.split(":")[0]
        selected_code = None
        for code, meta in CSF_FUNCTION_OPTIONS.items():
            if meta["label"] == selected_label_prefix:
                selected_code = code
                break

        if selected_code:
            st.session_state["oe_csf_function"] = selected_code
            st.session_state["oe_csf_function_label"] = CSF_FUNCTION_OPTIONS[selected_code]["label"]

        st.info(f"Current CSF 2.0 context: **{st.session_state.get('oe_csf_function_label', 'Not selected')}**")

        selected_func_id = st.session_state.get("oe_csf_function")
        cat_options = CATS_BY_FUNC.get(selected_func_id, [])
        cat_ids = [cid for cid, _ in cat_options]
        cat_labels = {cid: lbl for cid, lbl in cat_options}

        selected_cat_id = st.selectbox(
            "Category",
            options=cat_ids if cat_ids else ["(no categories defined)"],
            format_func=lambda cid: cat_labels.get(cid, cid),
            key="oe_csf_category",
        )

        subs = SUBS_BY_CAT.get(selected_cat_id, [])
        sub_labels = {sid: lbl for sid, lbl in subs}

        selected_sub_ids = st.multiselect(
            "Subcategories / outcomes most directly involved",
            options=[sid for sid, _ in subs],
            format_func=lambda sid: sub_labels.get(sid, sid),
            key="oe_csf_subcategories",
        )

        st.caption("Optional: explain why these CSF outcomes are most relevant to the decision context.")
        st.text_area(
            "CSF rationale (optional)",
            key="oe_csf_rationale",
            height=90,
        )

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

        st.session_state["oe_pfce_auto"] = pfce_auto

        st.markdown("---")

    # ---------------- Step 4: PFCE Analysis ----------------
    if step == 4:
        st.markdown("### 4. PFCE Analysis")
        st.caption("Clarify why this situation is ethically significant before stating the central ethical tension.")

        st.multiselect(
            "Ethical condition tags (optional)",
            options=ETHICAL_CONDITION_TAG_OPTIONS,
            key="oe_ethical_condition_tags",
        )

        st.text_area(
            "PFCE analysis (brief)",
            key="oe_pfce_analysis",
            height=160,
            placeholder=(
                "Example: Automated restrictions constrained operator control; beneficence and non-maleficence were implicated "
                "by precautionary posture vs operational reliability; autonomy was constrained; explicability was limited."
            ),
        )

        st.markdown("---")

    # ---------------- Step 5: Ethical Tension ----------------
    if step == 5:
        st.markdown("### 5. Ethical Tension")
        st.caption(
            "State the central ethical tension as two justified obligations that cannot both be fully fulfilled in this situation."
        )

        st.text_area(
            "Express the tension as: obligation A **vs.** obligation B",
            key="oe_ethical_tension",
            height=120,
            placeholder=(
                "Example: Maintain precautionary restrictions to reduce potential harm **vs.** restore full operator control "
                "to maintain treatment reliability."
            ),
        )

        st.markdown("---")

    # ---------------- Step 6: PFCE Principle Mapping ----------------
    if step == 6:
        st.markdown("### 6. PFCE Principle Mapping (Principlist Framework for Cybersecurity Ethics)")
        st.caption(
            "Select the PFCE principles most relevant in this decision context. Suggestions (if any) are based on the CSF outcomes selected."
        )

        pfce_auto_unique = []
        for p in pfce_auto:
            if p in PFCE_NAMES and p not in pfce_auto_unique:
                pfce_auto_unique.append(p)

        st.multiselect(
            "PFCE principles",
            options=PFCE_NAMES,
            default=pfce_auto_unique,
            key="oe_pfce_principles",
        )

        st.caption("Optional: explain how these principles relate to the decision context.")
        st.text_area(
            "PFCE rationale (optional)",
            key="oe_pfce_rationale",
            height=110,
        )

        st.markdown("---")

    # ---------------- Step 7: Institutional & Governance Constraints ----------------
    if step == 7:
        st.markdown("### 7. Institutional and Governance Constraints")
        st.caption("Document the institutional and governance constraints that shape or limit feasible responses.")

        st.multiselect(
            "Constraints (select any that apply)",
            options=GOV_CONSTRAINTS,
            key="oe_constraints",
        )

        st.text_area(
            "Other constraints (optional)",
            key="oe_constraints_other",
            height=90,
        )

        st.markdown("---")

    # ---------------- Step 8: Decision ----------------
    if step == 8:
        st.markdown("### 8. Decision")
        st.caption("Record the decision taken or proposed in clear operational terms.")

        st.text_area(
            "Decision",
            key="oe_decision",
            height=120,
        )

        st.markdown("---")

    # ---------------- Step 9: Outcomes and Implications ----------------
    if step == 9:
        st.markdown("### 9. Outcomes and Implications")
        st.caption("Describe what resulted and why it mattered operationally and ethically (narrative).")

        st.text_area(
            "Outcomes and implications",
            key="oe_outcomes_implications",
            height=160,
            placeholder="Example: restrictions maintained during analysis; operational inefficiencies; later determined non-malicious cause; full control restored; effects on service continuity and trust.",
        )

        st.markdown("---")

    # ---------------- Navigation + Summary ----------------
    nav_col1, nav_col2 = st.columns([1, 1])

    with nav_col1:
        if step > 1:
            if st.button("◀ Previous", key=f"oe_prev_{step}"):
                st.session_state["oe_step"] = max(1, step - 1)
                _safe_rerun()

    with nav_col2:
        if step < 9:
            if st.button("Next ▶", key=f"oe_next_{step}"):
                st.session_state["oe_step"] = min(9, step + 1)
                _safe_rerun()
        else:
            if st.button("Generate decision rationale", key="oe_generate_summary"):
                ts = datetime.now().isoformat(timespec="minutes")

                st.success("Decision rationale generated below.")
                st.markdown("#### Decision Rationale (for thesis demonstration)")
                st.write(f"**Timestamp:** {ts}")

                # Build label dictionaries for CSF display
                func_labels = {fid: lbl for fid, lbl in FUNC_OPTIONS}
                cat_labels = {}
                for fid, cats in CATS_BY_FUNC.items():
                    for cid, lbl in cats:
                        cat_labels[cid] = lbl
                sub_labels = {}
                for cid, subs in SUBS_BY_CAT.items():
                    for sid, lbl in subs:
                        sub_labels[sid] = lbl

                # Pull values
                background = st.session_state.get("oe_background", "")
                trigger_type = st.session_state.get("oe_trigger_type", "")
                triggering_condition = st.session_state.get("oe_triggering_condition", "")

                decision_type = st.session_state.get("oe_decision_type", "")
                decision_context = st.session_state.get("oe_decision_context", "")

                selected_func_id = st.session_state.get("oe_csf_function", "")
                selected_cat_id = st.session_state.get("oe_csf_category", "")
                selected_sub_ids = st.session_state.get("oe_csf_subcategories", [])
                csf_rationale = st.session_state.get("oe_csf_rationale", "")

                ethical_tags = st.session_state.get("oe_ethical_condition_tags", [])
                pfce_analysis = st.session_state.get("oe_pfce_analysis", "")

                ethical_tension = st.session_state.get("oe_ethical_tension", "")

                selected_pfce = st.session_state.get("oe_pfce_principles", [])
                pfce_rationale = st.session_state.get("oe_pfce_rationale", "")

                selected_constraints = st.session_state.get("oe_constraints", [])
                other_constraints = st.session_state.get("oe_constraints_other", "")

                decision = st.session_state.get("oe_decision", "")
                outcomes_implications = st.session_state.get("oe_outcomes_implications", "")

                # Print sections aligned to schema/case-based structure
                st.markdown("**1. Technical and Operational Background**")
                st.write(background or "—")

                st.markdown("**2. Triggering Condition and Key Events**")
                if trigger_type:
                    st.write(f"Trigger type: {trigger_type}")
                st.write(triggering_condition or "—")

                st.markdown("**3. Decision Context and NIST CSF Mapping**")
                if decision_type:
                    st.write(f"Decision context type: {decision_type}")
                st.write(decision_context or "—")

                st.markdown("**NIST CSF mapping**")
                st.write(f"- Function: {func_labels.get(selected_func_id, selected_func_id or '—')}")
                st.write(f"- Category: {cat_labels.get(selected_cat_id, selected_cat_id or '—')}")
                if selected_sub_ids:
                    st.write("- Subcategories / outcomes:")
                    for sid in selected_sub_ids:
                        st.write(f"  - {sub_labels.get(sid, sid)}")
                else:
                    st.write("- Subcategories / outcomes: —")
                if csf_rationale:
                    st.write(f"- Rationale: {csf_rationale}")

                st.markdown("**4. PFCE Analysis**")
                if ethical_tags:
                    st.write("Tags: " + ", ".join(ethical_tags))
                st.write(pfce_analysis or "—")

                st.markdown("**5. Ethical Tension**")
                st.write(ethical_tension or "—")

                st.markdown("**6. PFCE Principle Mapping**")
                if selected_pfce:
                    st.write(", ".join(selected_pfce))
                    st.write("**Overall ethical focus:** " + summarize_pfce(selected_pfce))
                else:
                    st.write("—")
                if pfce_rationale:
                    st.markdown("**PFCE rationale**")
                    st.write(pfce_rationale)

                st.markdown("**7. Institutional and Governance Constraints**")
                if selected_constraints:
                    for c in selected_constraints:
                        st.write(f"- {c}")
                else:
                    st.write("—")
                if other_constraints:
                    st.write(f"Other: {other_constraints}")

                st.markdown("**8. Decision**")
                st.write(decision or "—")

                st.markdown("**9. Outcomes and Implications**")
                st.write(outcomes_implications or "—")

                # Optional PDF download (mirrors Open-Ended vibe; safe + contained)
                lines = [
                    f"Timestamp: {ts}",
                    "",
                    "1. Technical and Operational Background",
                    background or "—",
                    "",
                    "2. Triggering Condition and Key Events",
                    f"Trigger type: {trigger_type or '—'}",
                    triggering_condition or "—",
                    "",
                    "3. Decision Context and NIST CSF Mapping",
                    f"Decision context type: {decision_type or '—'}",
                    decision_context or "—",
                    f"Function: {func_labels.get(selected_func_id, selected_func_id or '—')}",
                    f"Category: {cat_labels.get(selected_cat_id, selected_cat_id or '—')}",
                    "Subcategories / outcomes:",
                    *(["  - " + sub_labels.get(sid, sid) for sid in selected_sub_ids] if selected_sub_ids else ["  - —"]),
                    ("Rationale: " + csf_rationale) if csf_rationale else "",
                    "",
                    "4. PFCE Analysis",
                    ("Tags: " + ", ".join(ethical_tags)) if ethical_tags else "Tags: —",
                    pfce_analysis or "—",
                    "",
                    "5. Ethical Tension",
                    ethical_tension or "—",
                    "",
                    "6. PFCE Principle Mapping",
                    (", ".join(selected_pfce) if selected_pfce else "—"),
                    ("Overall ethical focus: " + summarize_pfce(selected_pfce)) if selected_pfce else "",
                    ("PFCE rationale: " + pfce_rationale) if pfce_rationale else "",
                    "",
                    "7. Institutional and Governance Constraints",
                    *(selected_constraints if selected_constraints else ["—"]),
                    ("Other: " + other_constraints) if other_constraints else "",
                    "",
                    "8. Decision",
                    decision or "—",
                    "",
                    "9. Outcomes and Implications",
                    outcomes_implications or "—",
                ]
                pdf = _build_pdf("Decision Rationale (Open-Ended Mode)", [ln for ln in lines if ln is not None])

                st.download_button(
                    "Download decision rationale (PDF)",
                    data=pdf,
                    file_name="decision_rationale_open_ended.pdf",
                    mime="application/pdf",
                )
