import streamlit as st
import json
from datetime import datetime

# ---------- Page setup ----------
st.set_page_config(
    page_title="Ethical Cybersecurity Decision Tool",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Session init ----------
if "presets_loaded" not in st.session_state:
    st.session_state.presets_loaded = False

# ---------- Helpers ----------
NIST_2_FUNCTIONS = [
    "Govern", "Identify", "Protect", "Detect", "Respond", "Recover"
]

NIST_2_HELP = {
    "Govern": "Establish risk management strategy, roles, policies, oversight, and accountability.",
    "Identify": "Understand assets, risks, business context, and dependencies.",
    "Protect": "Safeguard services via controls, training, access, data security.",
    "Detect": "Discover events via monitoring, anomalies, and continuous analysis.",
    "Respond": "Contain, communicate, analyze, and coordinate during incidents.",
    "Recover": "Restore capabilities and improve based on lessons learned."
}

PRINCIPLES = [
    ("Beneficence", "Promote well-being and good outcomes."),
    ("Non-maleficence", "Avoid harm."),
    ("Autonomy", "Respect individuals’ rights and choices."),
    ("Justice", "Ensure fairness and equity."),
    ("Explicability", "Ensure transparency, intelligibility, and accountability.")
]

EXTENDED_OBLIGATIONS = [
    ("Accountability", "Document, justify, and accept responsibility for actions."),
    ("Proportionality", "Match measures to the actual risk and context."),
    ("Privacy & Confidentiality", "Safeguard personal/operational data appropriately."),
    ("Professional Integrity", "Adhere to ethical/technical standards despite pressures."),
    ("Public Trust", "Sustain legitimacy via openness, consistency, and stewardship.")
]

CONSTRAINTS_MENU = [
    "Limited budget",
    "Staffing shortages / skill gaps",
    "Fragmented authority / unclear decision rights",
    "Outdated infrastructure / technical debt",
    "Procurement limits / speed vs. vetting",
    "Vendor opacity / audit limitations",
    "Lack of policy (e.g., surveillance, data governance)",
    "Legal uncertainty / compliance ambiguity",
    "Limited time / incident time pressure",
    "Public trust / political pressure"
]

VALUES_MENU = [
    "Privacy", "Transparency", "Trust", "Safety",
    "Equity", "Autonomy", "Accountability", "Fairness"
]

STAKEHOLDER_MENU = [
    "Residents", "City Employees", "Vendors/Partners",
    "City Council/Mayor", "Public Safety", "Regulators", "Media", "Others"
]

CONFLICT_PAIRS = [
    "Beneficence ↔ Non-maleficence",
    "Beneficence ↔ Autonomy",
    "Justice ↔ Autonomy",
    "Justice ↔ Non-maleficence",
    "Explicability ↔ Any"
]

def chip(label):
    st.markdown(
        f"<span style='display:inline-block;padding:.2rem .5rem;border:1px solid #e5e7eb;"
        f"border-radius:.75rem;font-size:.85rem;background:#fafafa;margin:.1rem .2rem'>{label}</span>",
        unsafe_allow_html=True,
    )

def calc_ethics_tension(num_values, num_stakeholders, constraint_severities, conflict_count, empty_principles):
    # Components
    constraints = sum(constraint_severities) * 2.5              # 0–(10*#sel)*2.5
    scope = (num_values * 4) + (num_stakeholders * 3)            # breadth of impact
    conflicts = conflict_count * 10                               # explicit tensions
    incompleteness = empty_principles * 6                         # missing justifications increase tension
    total = constraints + scope + conflicts + incompleteness
    return min(int(total), 100), {
        "Constraints": constraints,
        "Scope (values/stakeholders)": scope,
        "Conflicts": conflicts,
        "Gaps (missing principle notes)": incompleteness
    }

def make_report(data):
    lines = []
    lines.append("# Ethical Decision Justification\n")
    lines.append(f"**Timestamp:** {datetime.utcnow().isoformat()}Z\n")
    lines.append(f"**Incident Type:** {data['incident_type']}")
    lines.append(f"**Incident Description:** {data['incident_description'] or '—'}\n")
    lines.append("**NIST CSF 2.0 Functions Applied:** " + ", ".join(data['nist']))
    lines.append("\n---\n")
    lines.append("## Stakeholders & Public Values")
    lines.append("**Stakeholders:** " + (", ".join(data['stakeholders']) or "—"))
    lines.append("**Values at Risk:** " + (", ".join(data['values']) or "—"))
    lines.append("\n---\n")
    lines.append("## Institutional & Governance Constraints")
    if data['constraints']:
        for c in data['constraints']:
            sev = data['constraint_severity'].get(c, 0)
            lines.append(f"- {c}: severity {sev}/10")
    else:
        lines.append("- None indicated")
    if data['constraint_notes']:
        lines.append(f"\n**Constraint Notes:** {data['constraint_notes']}")
    lines.append("\n---\n")
    lines.append("## Principlist Evaluation")
    for key, text in data['principles'].items():
        lines.append(f"**{key}:** {text or '—'}")
    if any(data['extended'].values()):
        lines.append("\n### Extended Obligations")
        for key, text in data['extended'].items():
            if text.strip():
                lines.append(f"- **{key}:** {text}")
    lines.append("\n---\n")
    lines.append("## Principle Conflict Matrix")
    if data['conflicts']:
        for row in data['conflicts']:
            lines.append(f"- **Pair:** {row['pair']}; **Provisional priority:** {row['priority']}  \n  **Rationale:** {row['rationale'] or '—'}")
    else:
        lines.append("- None logged")
    lines.append("\n---\n")
    lines.append("## Chosen Action & Alternatives")
    lines.append("**Chosen Action:** " + (data['chosen_action'] or "—"))
    if data['alternatives']:
        for a in data['alternatives']:
            lines.append(f"- {a}")
    else:
        lines.append("- (no alternatives recorded)")
    lines.append("\n---\n")
    lines.append("## NIST Alignment Notes")
    if data['nist_notes']:
        lines.append(data['nist_notes'])
    else:
        lines.append("—")
    lines.append("\n---\n")
    lines.append("## Ethical Tension Score (0–100)")
    lines.append(f"**Total:** {data['score_total']}")
    for k, v in data['score_breakdown'].items():
        lines.append(f"- {k}: {int(v)}")
    lines.append("\n---\n")
    lines.append("## Explicability Summary (for public/oversight)")
    lines.append(
        f"This action was selected after evaluating impacts on **{', '.join(data['values']) or '—'}** "
        f"for **{', '.join(data['stakeholders']) or '—'}**, considering institutional constraints "
        f"({', '.join([f'{c} {data['constraint_severity'].get(c,0)}/10' for c in data['constraints']]) or '—'}). "
        f"The reasoning applied the **Principlist framework** and mapped to **NIST CSF 2.0** functions "
        f"({', '.join(data['nist']) or '—'})."
    )
    return "\n".join(lines)

def load_preset(name):
    # Safe, neutral presets (no numeric claims), consistent with Ch.3 arcs
    if name == "—":
        return
    if name == "Baltimore (ransomware)":
        st.session_state.incident_type = "Ransomware"
        st.session_state.nist_functions = ["Identify", "Protect", "Detect", "Respond", "Recover", "Govern"]
        st.session_state.stakeholders = ["Residents", "City Employees", "Vendors/Partners", "City Council/Mayor", "Public Safety"]
        st.session_state.values = ["Safety", "Trust", "Transparency", "Autonomy", "Equity", "Privacy", "Accountability"]
        st.session_state.constraints_sel = ["Limited budget", "Outdated infrastructure / technical debt", "Fragmented authority / unclear decision rights", "Limited time / incident time pressure", "Public trust / political pressure"]
    if name == "San Diego (smart streetlights)":
        st.session_state.incident_type = "Technology Repurposing / Surveillance Governance"
        st.session_state.nist_functions = ["Govern", "Identify", "Protect", "Respond", "Recover"]
        st.session_state.stakeholders = ["Residents", "City Council/Mayor", "Public Safety", "City Employees", "Media"]
        st.session_state.values = ["Transparency", "Privacy", "Accountability", "Equity", "Trust", "Autonomy"]
        st.session_state.constraints_sel = ["Lack of policy (e.g., surveillance, data governance)", "Fragmented authority / unclear decision rights", "Vendor opacity / audit limitations", "Procurement limits / speed vs. vetting", "Public trust / political pressure"]
    if name == "Riverton (AI-enabled incident)":
        st.session_state.incident_type = "AI-enabled Incident (Critical Infrastructure)"
        st.session_state.nist_functions = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]
        st.session_state.stakeholders = ["Residents", "Public Safety", "Vendors/Partners", "City Council/Mayor", "City Employees"]
        st.session_state.values = ["Safety", "Transparency", "Accountability", "Autonomy", "Trust", "Equity"]
        st.session_state.constraints_sel = ["Vendor opacity / audit limitations", "Limited time / incident time pressure", "Fragmented authority / unclear decision rights", "Procurement limits / speed vs. vetting"]

# ---------- Sidebar: Presets & Modes ----------
st.sidebar.header("Case Preset & Modes")
preset = st.sidebar.selectbox("Load preset (optional)", ["—", "Baltimore (ransomware)", "San Diego (smart streetlights)", "Riverton (AI-enabled incident)"])
if st.sidebar.button("Load preset"):
    load_preset(preset)
    st.session_state.presets_loaded = True
    st.sidebar.success(f"Preset loaded: {preset}")

urgency_mode = st.sidebar.toggle("⏱️ Urgency mode (time pressure)", value=False, help="Highlights minimum documentation fields for fast capture.")
st.sidebar.write("---")
st.sidebar.caption("NIST CSF 2.0 adds **Govern**. This tool aligns your actions with both ethics and standards.")

# ---------- Title / About ----------
st.title("🛡️ Ethical Cybersecurity Decision Tool (Municipal)")
st.markdown("#### Real-time ethical decision support integrating NIST CSF 2.0 and principlist reasoning")

with st.expander("ℹ️ About (fit to thesis)"):
    st.markdown("""
- Built for **municipal** contexts where technical, ethical, and governance constraints collide.
- Implements **NIST CSF 2.0** (including **Govern**) and the **Principlist** framework (beneficence, non‑maleficence, autonomy, justice, explicability).
- Captures **institutional/governance constraints**, logs **principle conflicts**, and generates a clear **Explicability Report** for oversight/public trust.
""")

# ---------- 1) Incident Overview ----------
st.markdown("### 1) 🚨 Incident Overview")
colA, colB = st.columns([1, 2])

with colA:
    incident_type = st.selectbox(
        "Type of Incident",
        [
            st.session_state.get("incident_type", ""),
            "Ransomware",
            "Unauthorized Access",
            "Data Breach",
            "Technology Repurposing / Surveillance Governance",
            "AI-enabled Incident (Critical Infrastructure)",
            "Other"
        ],
        index=0 if st.session_state.get("incident_type") else 1
    )

with colB:
    incident_description = st.text_area("Describe the situation in 2–4 sentences:", placeholder="What happened, what’s at risk, and current status?")

with st.expander("🧭 NIST CSF 2.0 functions (cheat sheet)"):
    cols = st.columns(len(NIST_2_FUNCTIONS))
    for i, fn in enumerate(NIST_2_FUNCTIONS):
        with cols[i]:
            st.markdown(f"**{fn}**")
            st.caption(NIST_2_HELP[fn])

nist_functions = st.multiselect(
    "Which NIST CSF 2.0 functions are in play?",
    NIST_2_FUNCTIONS,
    default=st.session_state.get("nist_functions", [])
)

nist_notes = st.text_area("NIST alignment notes (e.g., categories/activities touched):", placeholder="E.g., RS.CO (Response Communications), GV (Governance), PR.AC (Access Control) …")

# ---------- 2) Stakeholders & Values ----------
st.markdown("### 2) 👥 Stakeholders & Public Values at Risk")
stakeholders = st.multiselect("Who is affected or accountable?", STAKEHOLDER_MENU, default=st.session_state.get("stakeholders", []))
values = st.multiselect("Which values are implicated?", VALUES_MENU, default=st.session_state.get("values", []))

# quick chips
st.caption("Selected:")
st.write("Stakeholders:")
for s in stakeholders: chip(s)
st.write("Values:")
for v in values: chip(v)

# ---------- 3) Institutional & Governance Constraints ----------
st.markdown("### 3) ⚖️ Institutional & Governance Constraints")

constraints_sel = st.multiselect(
    "Select all constraints that materially shape the decision:",
    CONSTRAINTS_MENU,
    default=st.session_state.get("constraints_sel", [])
)

sev_cols = st.columns(5)
constraint_severity = {}
for idx, c in enumerate(constraints_sel):
    with sev_cols[idx % 5]:
        constraint_severity[c] = st.slider(f"{c}", 0, 10, 5)

constraint_notes = st.text_area("Notes on constraints (legal/policy obligations, oversight availability, political/public trust considerations):")

# ---------- 4) Principlist Evaluation + Extended Obligations ----------
st.markdown("### 4) 🧠 Principlist Evaluation & Extended Obligations")

p_cols = st.columns(5)
principle_inputs = {}
for i, (p, helper) in enumerate(PRINCIPLES):
    with p_cols[i]:
        st.caption(f"**{p}** — {helper}")
    principle_inputs[p] = st.text_area(f"{p}: how considered?", key=f"p_{p}", placeholder=f"Record how {p.lower()} is addressed.")

with st.expander("➕ Extended obligations (optional but recommended)"):
    e_cols = st.columns(3)
    extended_inputs = {}
    for i, (name, helper) in enumerate(EXTENDED_OBLIGATIONS):
        with e_cols[i % 3]:
            st.caption(f"**{name}** — {helper}")
            extended_inputs[name] = st.text_area(f"{name}: how considered?", key=f"e_{name}", placeholder=f"Record how {name.lower()} is addressed.")

# ---------- 5) Principle Conflict Matrix ----------
st.markdown("### 5) ⚔️ Principle Conflict Matrix")
conflicts_sel = st.multiselect("Log explicit tensions (pick all that apply):", CONFLICT_PAIRS)
conflict_rows = []
if conflicts_sel:
    for pair in conflicts_sel:
        c1, c2 = pair.split("↔") if "↔" in pair else (pair, "")
        c1, c2 = c1.strip(), c2.strip()
        with st.container():
            ccol1, ccol2 = st.columns([1.2, 1.8])
            with ccol1:
                priority = st.selectbox(f"Provisional priority for **{pair}**", [c1, c2, "Context-dependent / balanced"], key=f"prio_{pair}")
            with ccol2:
                rationale = st.text_input(f"Rationale for **{pair}**", key=f"rat_{pair}", placeholder="Why this priority? Risk, rights, equity, feasibility, etc.")
            conflict_rows.append({"pair": pair, "priority": priority, "rationale": rationale})

# ---------- 6) Ethical Tension Score ----------
st.markdown("### 6) 🔍 Ethical Tension Score (with breakdown)")
empty_principles = sum(1 for v in principle_inputs.values() if not v.strip())
constraint_severities = [constraint_severity.get(c, 0) for c in constraints_sel]
score_total, score_breakdown = calc_ethics_tension(
    num_values=len(values),
    num_stakeholders=len(stakeholders),
    constraint_severities=constraint_severities,
    conflict_count=len(conflict_rows),
    empty_principles=empty_principles
)
st.progress(score_total)
sc1, sc2 = st.columns([1,1])
with sc1:
    if score_total < 30:
        st.success("🟢 Low ethical tension — environment relatively clear.")
    elif score_total < 70:
        st.warning("🟠 Moderate ethical tension — document justification carefully.")
    else:
        st.error("🔴 High ethical tension — revisit conflicts, constraints, and alternatives.")
with sc2:
    st.write("**Breakdown**")
    st.json({k: int(v) for k, v in score_breakdown.items()})

# ---------- 7) Decisions & Alternatives ----------
st.markdown("### 7) ✅ Decision & Alternatives")
chosen_action = st.text_input("Chosen action (describe clearly):", placeholder="E.g., do not pay ransom; enable partial service; issue public notice; enact temporary policy; etc.")
alts = st.tags_input if hasattr(st, "tags_input") else None  # fallback if streamlit-extras not present
alternatives = []
if alts:
    alternatives = st.tags_input("List key alternatives considered (press Enter to add):", ["Alternative A"])
else:
    alt_text = st.text_area("Alternatives considered (comma-separated):", placeholder="Alternative A, Alternative B, …")
    alternatives = [a.strip() for a in alt_text.split(",") if a.strip()]

# ---------- 8) Generate Explicability Report ----------
st.markdown("### 8) 🧾 Generate Explicability Report & Exports")
if st.button("Generate Report"):
    bundle = {
        "incident_type": incident_type,
        "incident_description": incident_description,
        "nist": nist_functions,
        "nist_notes": nist_notes,
        "stakeholders": stakeholders,
        "values": values,
        "constraints": constraints_sel,
        "constraint_severity": constraint_severity,
        "constraint_notes": constraint_notes,
        "principles": principle_inputs,
        "extended": extended_inputs if any(v.strip() for v in extended_inputs.values()) else {},
        "conflicts": conflict_rows,
        "chosen_action": chosen_action,
        "alternatives": alternatives,
        "score_total": score_total,
        "score_breakdown": score_breakdown
    }
    report_md = make_report(bundle)
    st.success("Report generated below. You can copy or download it.")
    st.markdown(report_md)

    st.download_button("📄 Download report (.txt)", data=report_md, file_name="ethical_decision_report.txt", mime="text/plain")
    st.download_button("🧩 Download session (.json)", data=json.dumps(bundle, indent=2), file_name="ethical_decision_session.json", mime="application/json")

# ---------- Footer hint ----------
st.caption("Tip: In urgency mode, complete the Incident, NIST, Principlist (briefly), Constraints (severity), and Decision. You can refine later for a thorough explicability record.")

