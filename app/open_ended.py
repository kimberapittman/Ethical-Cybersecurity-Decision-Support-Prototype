import streamlit as st
from datetime import datetime

from logic.loaders import (
    load_csf_data,
    load_pfce_crosswalk,
    load_pfce_principles,
    load_constraints,
)
from logic.reasoning import apply_crosswalk, summarize_pfce


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
        func_options.append(func_label)

        categories = fn.get("categories", []) or []
        cats_by_func[func_id] = []

        for cat in categories:
            cat_id = cat.get("id")
            if not cat_id:
                continue

            cat_title = cat.get("title") or cat.get("name") or ""
            cat_label = f"{cat_id} – {cat_title}" if cat_title else cat_id
            cats_by_func[func_id].append(cat_label)

            # Your JSON uses "outcomes" instead of "subcategories"
            outcomes = cat.get("outcomes") or cat.get("subcategories") or []
            subs = []
            for item in outcomes:
                sub_id = item.get("id")
                if not sub_id:
                    continue

                desc = item.get("outcome") or item.get("description") or ""
                sub_label = f"{sub_id} – {desc}" if desc else sub_id
                subs.append(sub_label)

            subs_by_cat[cat_id] = subs

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
# Open-Ended Mode UI
# ------------------------------

def render_open_ended():
    st.markdown("## Open-Ended Mode")

    # 0. Basic context fields
    st.markdown("#### Context")
    c1, c2 = st.columns(2)
    with c1:
        incident_title = st.text_input("Incident Title")
        municipality = st.text_input("Municipality / Organization (optional)")
    with c2:
        role = st.text_input("Your Role")
        notes = st.text_area("Notes (optional)", height=80)

    st.markdown("---")

    # 1. Technical Trigger
    st.markdown("### 1. Technical Trigger")
    st.caption("Describe the event, condition, or vulnerability that triggered this decision.")
    technical_trigger = st.text_area(
        " ",
        key="oe_technical_trigger",
        height=120,
        label_visibility="collapsed",
        placeholder="Example: A ransomware payload was activated on a shared file server hosting multiple city department shares..."
    )

    # 2. Technical Decision Point
    st.markdown("### 2. Technical Decision Point")
    st.caption("Specify what must be decided in technical terms (e.g., shut down, isolate, pay, disclose, reconfigure).")
    technical_decision = st.text_area(
        "  ",
        key="oe_technical_decision",
        height=120,
        label_visibility="collapsed",
        placeholder="Example: Decide whether to take the permitting system fully offline for 48 hours to rebuild from backups..."
    )

    st.markdown("---")

    # 3. Technical Mapping (NIST CSF 2.0)
    st.markdown("### 3. Technical Mapping (NIST CSF 2.0)")
    st.caption("Map this incident and decision into the NIST CSF 2.0 structure to clarify where it sits procedurally.")

    # Function selection
    func_ids = [fid for fid, _ in FUNC_OPTIONS]
    func_labels = {fid: lbl for fid, lbl in FUNC_OPTIONS}

    selected_func_id = st.selectbox(
        "Function",
        options=func_ids,
        format_func=lambda fid: func_labels.get(fid, fid),
        key="oe_csf_function",
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
        "Subcategories (outcomes most directly involved)",
        options=sub_ids,
        format_func=lambda sid: sub_labels.get(sid, sid),
        key="oe_csf_subcategories",
    )

    st.caption("Optional: briefly explain why these CSF outcomes are most relevant to this incident.")
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

            st.markdown(f"**{csf_id} – {outcome}**")
            if pfce:
                st.markdown("• Suggested principles: " + ", ".join(pfce))
                pfce_auto.extend(pfce)
            if rationale:
                st.markdown(f"_Why this matters_: {rationale}")
            st.markdown("---")

    st.markdown("---")

    # 4. Ethical Trigger
    st.markdown("### 4. Ethical Trigger")
    st.caption("Describe what makes this more than a purely technical choice (who or what might be harmed, burdened, or treated unfairly).")
    ethical_trigger = st.text_area(
        "Ethical trigger",
        key="oe_ethical_trigger",
        height=120,
    )

    # 5. Ethical Tension
    st.markdown("### 5. Ethical Tension")
    st.caption("State the main ethical tension as a trade-off between two justified but competing obligations.")
    ethical_tension = st.text_area(
        "Ethical tension",
        key="oe_ethical_tension",
        height=120,
        placeholder="Example: Restore public-facing systems as quickly as possible vs. preserve forensic evidence and avoid rewarding extortion..."
    )

    st.markdown("---")

    # 6. Ethical Mapping (PFCE)
    st.markdown("### 6. Ethical Mapping (Principlist Framework for Cybersecurity Ethics)")
    st.caption("Select the PFCE principles that are most relevant in this dilemma.")

    pfce_auto_unique = []
    for p in pfce_auto:
        if p in PFCE_NAMES and p not in pfce_auto_unique:
            pfce_auto_unique.append(p)

    selected_pfce = st.multiselect(
        "Principles",
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

    # 7. Institutional and Governance Constraints
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

    # 8. Decision Outcome and Ethical Implications
    st.markdown("### 8. Decision Outcome and Ethical Implications")
    st.caption("Record the decision taken (or proposed) and reflect on its ethical implications within these constraints.")

    decision_outcome = st.text_area(
        "Decision taken / recommended",
        key="oe_decision_outcome",
        height=110,
    )

    ethical_implications = st.text_area(
        "Ethical implications (who is helped, who is harmed, what is at stake long-term?)",
        key="oe_ethical_implications",
        height=130,
    )

    st.markdown("---")

    # Simple summary panel
    if st.button("Summarize open-ended decision"):
        st.success("Structured summary generated below.")
        st.markdown("#### Summary (for thesis demonstration)")
        st.write(f"**Timestamp:** {datetime.now().isoformat(timespec='minutes')}")
        st.write(f"**Incident Title:** {incident_title or '—'}")
        st.write(f"**Role / Org:** {role or '—'} / {municipality or '—'}")

        st.markdown("**Technical Trigger**")
        st.write(technical_trigger or "—")

        st.markdown("**Technical Decision Point**")
        st.write(technical_decision or "—")

        st.markdown("**NIST CSF Mapping**")
        st.write(f"- Function: {func_labels.get(selected_func_id, selected_func_id)}")
        st.write(f"- Category: {cat_labels.get(selected_cat_id, selected_cat_id)}")
        if selected_sub_ids:
            st.write("- Subcategories:")
            for sid in selected_sub_ids:
                st.write(f"  - {sub_labels.get(sid, sid)}")
        else:
            st.write("- Subcategories: —")
        if csf_rationale:
            st.write(f"- Rationale: {csf_rationale}")

        st.markdown("**Ethical Trigger**")
        st.write(ethical_trigger or "—")

        st.markdown("**Ethical Tension**")
        st.write(ethical_tension or "—")

        st.markdown("**PFCE Principles**")
        if selected_pfce:
            st.write(", ".join(selected_pfce))
            st.write("**Overall ethical focus:** " + summarize_pfce(selected_pfce))
        else:
            st.write("—")

        if pfce_rationale:
            st.markdown("**PFCE Rationale**")
            st.write(pfce_rationale)

        st.markdown("**Institutional & Governance Constraints**")
        if selected_constraints:
            for c in selected_constraints:
                st.write(f"- {c}")
        else:
            st.write("—")
        if other_constraints:
            st.write(f"Other: {other_constraints}")

        st.markdown("**Decision Outcome**")
        st.write(decision_outcome or "—")

        st.markdown("**Ethical Implications**")
        st.write(ethical_implications or "—")
