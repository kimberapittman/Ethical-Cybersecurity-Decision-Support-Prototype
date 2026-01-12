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
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    except Exception:
        pass


def _html_block(s: str) -> str:
    return "\n".join(line.lstrip() for line in s.splitlines())


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


@st.cache_data
def _load_core_data():
    csf = load_csf_data()
    crosswalk = load_pfce_crosswalk()
    pfce = load_pfce_principles()
    constraints = load_constraints()
    return csf, crosswalk, pfce, constraints

OE_STEP_TITLES = {
    1: "Decision Context",
    2: "NIST CSF 2.0 Mapping",
    3: "PFCE Analysis and Ethical Tension",
    4: "Institutional and Governance Constraints",
    5: "Decision (and documented rationale)",
}
OE_TOTAL_STEPS = len(OE_STEP_TITLES)


CSF_DATA, PFCE_CROSSWALK, PFCE_PRINCIPLES, GOV_CONSTRAINTS_RAW = _load_core_data()
PFCE_NAMES = [p.get("name", "") for p in PFCE_PRINCIPLES if p.get("name")]


PFCE_DEFINITIONS = {
    "Beneficence": (
        "Cybersecurity technologies should be used to benefit humans, promote human well-being, "
        "and make our lives better overall."
    ),
    "Non-maleficence": (
        "Cybersecurity technologies should not be used to intentionally harm humans or to make "
        "our lives worse overall."
    ),
    "Autonomy": (
        "Cybersecurity technologies should be used in ways that respect human autonomy. Humans "
        "should be able to make informed decisions for themselves about how that technology is used "
        "in their lives."
    ),
    "Justice": (
        "Cybersecurity technologies should be used to promote fairness, equality, and impartiality. "
        "They should not be used to unfairly discriminate, undermine solidarity, or prevent equal access."
    ),
    "Explicability": (
        "Cybersecurity technologies should be used in ways that are intelligible, transparent, and "
        "comprehensible, and it should be clear who is accountable and responsible for their use."
    ),
}


def _index_csf(csf_raw):
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
    if isinstance(raw, list):
        return [str(x) for x in raw]
    if isinstance(raw, dict):
        if isinstance(raw.get("constraints"), list):
            return [str(x) for x in raw["constraints"]]
        return [str(v) for v in raw.values()]
    return []


GOV_CONSTRAINTS = _normalize_constraints(GOV_CONSTRAINTS_RAW)


CSF_HINT_KEYWORDS = {
    "GV": ["policy", "policies", "authority", "approval", "oversight", "governance", "charter", "compliance", "board", "council"],
    "ID": ["inventory", "inventories", "classify", "classification", "asset", "assets", "dependency", "dependencies", "risk register", "risk assessment"],
    "PR": ["access", "permission", "privilege", "authorization", "encrypt", "encryption", "credential", "password", "data protection", "control", "controls", "configuration"],
    "DE": ["monitor", "monitoring", "alert", "alerts", "anomaly", "anomalies", "flagged", "suspicious", "detection", "log review"],
    "RS": ["disconnect", "isolate", "contain", "mitigate", "shutdown", "shut down", "take offline", "incident response", "triage", "manual control", "disable automation", "block traffic"],
    "RC": ["restore", "restoration", "rebuild", "recover", "back online", "return to operations", "post-incident review", "lessons learned"],
}


def guess_csf_function(decision_text: str):
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


TRIGGER_EXAMPLE_OPTIONS = [
    "Example (Baltimore): Ransomware deployed across municipal systems; service disruption and containment decisions.",
    "Example (San Diego): Smart streetlight footage accessed for law-enforcement use beyond documented program scope.",
    "Example (Riverton): AI system flagged anomalous control activity; imposed restrictions pending review."
]

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

def _render_open_header(step: int):
    step_title = OE_STEP_TITLES.get(step, "Open-Ended Mode")

    st.markdown(
        f"""
        <div style="text-align:center; margin-top: 0;">
        <h2 style="margin: 0 0 0.25rem 0;">{step_title}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
def render_open_ended():
    # ==========================================================
    # WALKTHROUGH STATE (single flow, no gate)
    # ==========================================================
    if "oe_step" not in st.session_state:
        st.session_state["oe_step"] = 1
    step = st.session_state["oe_step"]

    total_steps = OE_TOTAL_STEPS

    _render_open_header(step)
    st.progress(step / float(total_steps))
    st.caption(f"Step {step} of {total_steps}")

    def _render_step_tile_html(title: str, body_html: str):
        st.markdown(
            f"""
            <div class="listbox walkthrough-tile">
            <div class="walkthrough-step-title">{title}</div>
            {body_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ==========================================================
    # STEP 1: DECISION CONTEXT
    # ==========================================================
    if step == 1:
        # Tighten spacing ONLY for this Step 1 text area
        st.markdown(
            """
            <style>
            /* Scope to Open-Ended Step 1 only */
            div[data-testid="stVerticalBlock"]:has(#oe-step1-anchor)
            div[data-testid="stTextArea"]{
            margin-top: 0 !important;
            }
            </style>
            <div id="oe-step1-anchor"></div>
            """,
            unsafe_allow_html=True,
        )

        # Instruction text above the input
        st.markdown(
            """
            <div style="
                margin: 0 0 6px 0;
                font-weight: 500;
                color: rgba(229,231,235,0.90);
                font-size: 1.05rem;
                line-height: 1.45;
            ">
            Describe the cybersecurity decision you are facing or examining before a course of action is chosen.
            </div>
            """,
            unsafe_allow_html=True
        )

        # Text box with ONLY guidance as placeholder
        decision_context = st.text_area(
            "Decision context",
            key="oe_decision_context",
            height=120,
            placeholder="1–2 sentences describing the decision context (not the outcome or justification).",
            label_visibility="collapsed",
        )

        # Optional examples (expander)
        st.markdown(
            _html_block(
                """
        <details class="oe-example-expander">
        <summary title="Examples are drawn from reconstructed municipal cybersecurity incidents and a purpose-built hypothetical scenario used to inform the design of this prototype.">
            See example decision contexts (optional)
        </summary>

        <div class="oe-example-body">
            <p><strong>Baltimore (Ransomware):</strong><br>
            Maintain network connectivity while assessing the scope of a ransomware attack or proactively disconnect additional systems.</p>

            <p><strong>San Diego (Surveillance Repurposing):</strong><br>
            Maintain or modify current law-enforcement access to smart streetlight video surveillance.</p>

            <p><strong>Riverton (AI-Enabled Control System):</strong><br>
            Maintain AI-imposed restrictions or restore full operator control.</p>
        </div>
        </details>
                """
            ),
            unsafe_allow_html=True
        )


    # ==========================================================
    # STEP 2: NIST CSF 
    # ==========================================================
    elif step == 2:
        st.markdown(
            """
            <div style="
                margin: 0 0 10px 0;
                color: rgba(229,231,235,0.88);
                font-size: 1.0rem;
                line-height: 1.45;
            ">
            Within your current decision context, where are you operating in the cybersecurity process?
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Build ordered list of CSF function codes
        codes_list = list(CSF_FUNCTION_OPTIONS.keys())

        # Determine default index based on existing selection or suggestion
        default_index = 0
        current_code = st.session_state.get("oe_csf_function")
        suggested = st.session_state.get("oe_suggested_func")

        if current_code in CSF_FUNCTION_OPTIONS:
            default_index = codes_list.index(current_code)
        elif suggested in CSF_FUNCTION_OPTIONS:
            default_index = codes_list.index(suggested)

        # Radio returns the selected CODE, but displays only the PROMPT
        selected_code = st.radio(
            "Select which description best matches your current situation.",
            options=codes_list,  # store codes internally
            index=default_index,
            key="oe_csf_choice_step3",
            format_func=lambda c: CSF_FUNCTION_OPTIONS[c]["prompt"],  # show prompts only
        )

        # Persist selection
        st.session_state["oe_csf_function"] = selected_code
        st.session_state["oe_csf_function_label"] = CSF_FUNCTION_OPTIONS[selected_code]["label"]

        # One explicit, highlighted statement (no duplication)
        st.info(
            f"Based on your selection, the applicable CSF Function is: "
            f"**{st.session_state['oe_csf_function_label']}**"
        )

        st.markdown("### CSF Category")
        st.caption(
            "Select the category that best reflects the type of cybersecurity activity involved."
        )

        selected_func_id = st.session_state.get("oe_csf_function")
        cat_options = CATS_BY_FUNC.get(selected_func_id, [])
        cat_ids = [cid for cid, _ in cat_options]
        cat_labels = {cid: lbl for cid, lbl in cat_options}

        selected_cat_id = st.selectbox(
            "Within this function, what kind of work or concern is this decision about?",
            options=cat_ids if cat_ids else ["(no categories defined)"],
            format_func=lambda cid: cat_labels.get(cid, cid),
            key="oe_csf_category",
        )

        st.markdown("### Relevant CSF Subcategory Outcomes")
        st.caption(
            "Select all outcomes that are directly implicated by this decision."
        )

        subs = SUBS_BY_CAT.get(selected_cat_id, [])
        sub_labels = {sid: lbl for sid, lbl in subs}

        selected_sub_ids = []

        for sid, label in subs:
            checked = st.checkbox(
                f"**{sid}** — {label}",
                key=f"oe_sub_{sid}"
            )
            if checked:
                selected_sub_ids.append(sid)

        st.session_state["oe_csf_subcategories"] = selected_sub_ids


        pfce_auto_local = []
        if selected_sub_ids and PFCE_CROSSWALK:
            st.markdown("#### CSF → PFCE Ethical Hints (non-prescriptive)")
            matches = apply_crosswalk(selected_sub_ids, PFCE_CROSSWALK)
            for m in matches:
                csf_id = m.get("csf_id", "")
                outcome = m.get("csf_outcome", "")
                pfce = m.get("pfce", []) or []
                rationale = m.get("rationale", "")

                if csf_id or outcome:
                    st.markdown(f"**{csf_id} – {outcome}**".strip(" –"))

                if pfce:
                    st.markdown("• Suggested principles: " + ", ".join(pfce))
                    pfce_auto_local.extend(pfce)
                if rationale:
                    st.markdown(f"_Why this matters_: {rationale}")
                st.markdown("---")

        st.session_state["oe_pfce_auto"] = pfce_auto_local

    # ==========================================================
    # STEP 3: PFCE + TENSION
    # ==========================================================
    elif step == 3:
        _render_step_tile_html(
            "Make ethically significant conditions explicit, then state the central tension as two justified obligations.",
        )

        st.multiselect(
            "Ethical condition tags (optional)",
            options=ETHICAL_CONDITION_TAG_OPTIONS,
            key="oe_ethical_condition_tags",
        )

        st.text_area(
            "PFCE analysis (brief — what is ethically significant here?)",
            key="oe_pfce_analysis",
            height=160,
            placeholder=(
                "Example: Containment actions may protect against spread but disrupt essential services; "
                "limited visibility constrains justification for isolation scope; impacts may fall unevenly across residents."
            ),
        )

        # ----------------------------------------------------------
        # PFCE PRINCIPLE TRIAGE (mirrors CSF step style, multi-select)
        # ----------------------------------------------------------

        # Build display strings like: "BENEFICENCE (B): Does this decision impact human well-being?"
        # You can adjust label formatting to match your preferred style.
        pfce_option_texts = []
        pfce_ids = list(PFCE_DEFINITIONS.keys())  # assumes keys like "beneficence", etc.

        for pid in pfce_ids:
            name = pid.replace("-", " ").title()  # fallback if you don't have PFCE_NAMES mapping
            definition = PFCE_DEFINITIONS.get(pid, "").strip()
            pfce_option_texts.append(f"{name}: {definition}")

        # Default selections: use auto suggestions (from CSF crosswalk) if present
        pfce_auto_unique = []
        for p in st.session_state.get("oe_pfce_auto", []):
            # allow either ids or names depending on what your crosswalk produces
            if p in pfce_ids and p not in pfce_auto_unique:
                pfce_auto_unique.append(p)

        # Convert defaults into the same "Name: definition" strings
        default_pfce_texts = []
        for pid in pfce_auto_unique:
            name = pid.replace("-", " ").title()
            definition = PFCE_DEFINITIONS.get(pid, "").strip()
            default_pfce_texts.append(f"{name}: {definition}")

        _render_step_tile_html(
            "Use the PFCE to make ethically significant conditions explicit. "
            "This does not prescribe outcomes; it structures ethical reasoning.",
        )

        selected_pfce_texts = st.multiselect(
            "Which PFCE principles are implicated in this decision context?",
            options=pfce_option_texts,
            default=default_pfce_texts,
            key="oe_pfce_choice_step4",
        )

        # Map back to principle IDs
        selected_pfce_ids = []
        for opt in selected_pfce_texts:
            label_prefix = opt.split(":")[0].strip().lower()
            # rebuild the pid format you used earlier
            # (this matches our fallback name formatting)
            pid_guess = label_prefix.replace(" ", "-")
            if pid_guess in pfce_ids and pid_guess not in selected_pfce_ids:
                selected_pfce_ids.append(pid_guess)

        # Store into the same keys you already use elsewhere
        st.session_state["oe_pfce_principles"] = selected_pfce_ids

        # Optional "current selection" indicator (mirrors your st.info pattern)
        if selected_pfce_ids:
            pretty = ", ".join([pid.replace("-", " ").title() for pid in selected_pfce_ids])
            st.info(f"Current PFCE context: **{pretty}**")
        else:
            st.info("Current PFCE context: **None selected**")

        st.caption("Optional: explain how the selected PFCE principles show up in this decision context.")
        st.text_area(
            "PFCE rationale (optional)",
            key="oe_pfce_rationale",
            height=110,
        )

    # ==========================================================
    # STEP 4: CONSTRAINTS
    # ==========================================================
    elif step == 4:
        _render_step_tile_html(
            "Document constraints that shape or limit feasible actions or justification.",
        )

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

    # ==========================================================
    # STEP 5: DECISION + OUTPUT 
    # ==========================================================
    elif step == 5:
        _render_step_tile_html(
            "Record the decision in operational terms, then generate a structured rationale for demonstration purposes.",
        )

        st.text_area(
            "Decision (operational)",
            key="oe_decision",
            height=120,
            placeholder="Example: Disconnect additional systems while confirming scope; preserve critical service workflows via manual workarounds.",
        )

        st.markdown("---")

        if st.session_state.get("oe_generate"):
            st.session_state["oe_generate"] = False  # reset trigger

            ts = datetime.now().isoformat(timespec="minutes")
            st.success("Decision rationale generated below.")
            st.markdown("#### Decision Rationale (Open-Ended Mode)")
            st.write(f"**Timestamp:** {ts}")

            func_labels = {fid: lbl for fid, lbl in FUNC_OPTIONS}
            cat_labels = {cid: lbl for _, cats in CATS_BY_FUNC.items() for cid, lbl in cats}
            sub_labels = {sid: lbl for _, subs in SUBS_BY_CAT.items() for sid, lbl in subs}

            trigger_example = st.session_state.get("oe_gate_trigger_example", "")
            trigger_type = st.session_state.get("oe_gate_trigger_type", "")
            triggering_condition = st.session_state.get("oe_gate_triggering_condition", "")

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

            st.markdown("**Triggering condition and key events**")
            if trigger_example:
                st.write(f"Example: {trigger_example}")
            st.write(f"Trigger type: {trigger_type or '—'}")
            st.write(triggering_condition or "—")

            st.markdown("**Decision context**")
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

            st.markdown("**PFCE analysis and ethical tension**")
            if ethical_tags:
                st.write("Tags: " + ", ".join(ethical_tags))
            st.write(pfce_analysis or "—")
            st.write(f"**Ethical tension:** {ethical_tension or '—'}")

            st.markdown("**PFCE principles (if selected)**")
            if selected_pfce:
                st.write(", ".join(selected_pfce))
                st.write("**Overall ethical focus:** " + summarize_pfce(selected_pfce))
            else:
                st.write("—")
            if pfce_rationale:
                st.markdown("**PFCE rationale**")
                st.write(pfce_rationale)

            st.markdown("**Institutional and governance constraints**")
            if selected_constraints:
                for c in selected_constraints:
                    st.write(f"- {c}")
            else:
                st.write("—")
            if other_constraints:
                st.write(f"Other: {other_constraints}")

            st.markdown("**Decision**")
            st.write(decision or "—")

            lines = [
                f"Timestamp: {ts}",
                "",
                "Triggering condition and key events",
                f"Example: {trigger_example or '—'}",
                f"Trigger type: {trigger_type or '—'}",
                triggering_condition or "—",
                "",
                "Decision context",
                f"Decision context type: {decision_type or '—'}",
                decision_context or "—",
                "",
                "NIST CSF mapping",
                f"Function: {func_labels.get(selected_func_id, selected_func_id or '—')}",
                f"Category: {cat_labels.get(selected_cat_id, selected_cat_id or '—')}",
                "Subcategories / outcomes:",
                *(
                    ["  - " + sub_labels.get(sid, sid) for sid in selected_sub_ids]
                    if selected_sub_ids
                    else ["  - —"]
                ),
                ("Rationale: " + csf_rationale) if csf_rationale else "",
                "",
                "PFCE analysis and ethical tension",
                ("Tags: " + ", ".join(ethical_tags)) if ethical_tags else "Tags: —",
                pfce_analysis or "—",
                "Ethical tension: " + (ethical_tension or "—"),
                "",
                "PFCE principles",
                (", ".join(selected_pfce) if selected_pfce else "—"),
                ("Overall ethical focus: " + summarize_pfce(selected_pfce)) if selected_pfce else "",
                ("PFCE rationale: " + pfce_rationale) if pfce_rationale else "",
                "",
                "Institutional and governance constraints",
                *(selected_constraints if selected_constraints else ["—"]),
                ("Other: " + other_constraints) if other_constraints else "",
                "",
                "Decision",
                decision or "—",
            ]

            pdf = _build_pdf(
                "Decision Rationale (Open-Ended Mode)",
                [ln for ln in lines if ln is not None and ln != ""],
            )

            st.download_button(
                "Download decision rationale (PDF)",
                data=pdf,
                file_name="decision_rationale_open_ended.pdf",
                mime="application/pdf",
            )

    # NAV CONTROLS
    with st.container():
        st.markdown('<div class="oe-nav-anchor"></div>', unsafe_allow_html=True)

        col_l, col_r = st.columns(2, gap="large")

        with col_l:
            if step > 1:
                if st.button("◀ Previous", key=f"oenav_prev_{step}", use_container_width=False):
                    st.session_state["oe_step"] = step - 1
                    _safe_rerun()
            else:
                st.empty()

        with col_r:
            if step < total_steps:
                if st.button("Next ▶", key=f"oenav_next_{step}", use_container_width=False):
                    st.session_state["oe_step"] = step + 1
                    _safe_rerun()
            else:
                if st.button("Generate PDF", key="oe_generate_pdf", use_container_width=False):
                    st.session_state["oe_generate"] = True
                    _safe_rerun()






