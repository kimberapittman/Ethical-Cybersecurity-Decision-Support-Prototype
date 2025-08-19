# app.py
import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="Ethical Cybersecurity Decision Tool (Municipal)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Helpers
# ----------------------------
NIST_HELP = {
    "Identify":"Understand business context, assets, risks.",
    "Protect":"Safeguard critical services (access control, training, data security).",
    "Detect":"Discover events (anomalies, continuous monitoring).",
    "Respond":"Contain, analyze, communicate, and mitigate incidents.",
    "Recover":"Restore capabilities/services and improve."
}

PRINCIPLE_HELP = {
    "Beneficence":"Promote public well‑being (e.g., restore essential services).",
    "Non‑maleficence":"Avoid/prevent harm (e.g., minimize outage side‑effects).",
    "Autonomy":"Respect rights/choices and lawful authority (e.g., consent, due process).",
    "Justice":"Distribute burdens/benefits fairly; avoid disparate impacts.",
    "Explicability":"Be transparent, traceable, and justifiable to stakeholders."
}

CONSTRAINTS = [
    ("Funding limitations", "Budget constraints that delay modernization or response."),
    ("Authority fragmentation", "Split decision rights across departments; slows coordination."),
    ("Procurement opacity", "Vague scopes/labels; hidden capabilities (e.g., ‘mission creep’)."),
    ("Vendor opacity", "Limited auditability of code/data/models; contractual blind spots."),
    ("Policy/oversight gaps", "Missing surveillance/incident/AI policies; weak governance."),
    ("Staffing capacity", "Insufficient staff/skills to execute secure/ethical response."),
]

# default text for constraints notes
DEFAULT_NOTES = {
    "Funding limitations": "Capital refresh delayed; competing priorities.",
    "Authority fragmentation": "IT, utilities, and emergency mgmt split; unclear incident lead.",
    "Procurement opacity": "Contract framed as sustainability/efficiency—surveillance/AI not explicit.",
    "Vendor opacity": "No right to audit model/data; limited logs/explainability.",
    "Policy/oversight gaps": "Surveillance ordinance/AI policy absent or immature.",
    "Staffing capacity": "Thin bench for IR, legal, comms; reliance on contractors."
}

# ----------------------------
# Sidebar: Mode & Presets
# ----------------------------
st.sidebar.markdown("## ⚙️ Mode & Presets")

mode = st.sidebar.radio(
    "Workflow speed",
    ["Rapid (≈90 sec triage)", "Standard (full deliberation)"],
    index=1
)

preset = st.sidebar.selectbox(
    "Load a case preset",
    ["— None —", "Baltimore (2019) – ransomware",
     "San Diego (2017–20) – smart streetlights",
     "Riverton (2027) – AI‑enabled network attack"]
)

# state container
if "form" not in st.session_state:
    st.session_state.form = {}

def apply_preset(name:str):
    f = {}
    if name.startswith("Baltimore"):
        f.update({
            "incident_type":"Ransomware",
            "nist":["Identify","Protect","Detect","Respond","Recover"],
            "description":"RobbinHood ransomware encrypted core systems; extortion demanded.",
            "stakeholders":["Residents","City Employees","Vendors","City Council","Media"],
            "values":["Safety","Trust","Transparency","Equity","Autonomy","Privacy"],
            "constraints_scores":{
                "Funding limitations":7,"Authority fragmentation":6,"Procurement opacity":3,
                "Vendor opacity":4,"Policy/oversight gaps":5,"Staffing capacity":6
            },
            "beneficence":"Restore essential services (payments, permitting, property transfers) quickly.",
            "nonmaleficence":"Avoid harms from prolonged outages and workarounds.",
            "autonomy":"Respect residents’ choices; follow lawful authority on ransom guidance.",
            "justice":"Avoid disproportionate harms to vulnerable residents/businesses.",
            "explicability":"Clear, frequent, candid incident comms; document decision rationale."
        })
    elif name.startswith("San Diego"):
        f.update({
            "incident_type":"Technology repurposing / surveillance",
            "nist":["Identify","Protect","Detect","Respond"],
            "description":"Sensor streetlights repurposed for policing without robust public oversight.",
            "stakeholders":["Residents","City Council","City Employees","Media","Community Orgs"],
            "values":["Privacy","Transparency","Trust","Equity","Autonomy","Safety"],
            "constraints_scores":{
                "Funding limitations":4,"Authority fragmentation":7,"Procurement opacity":8,
                "Vendor opacity":6,"Policy/oversight gaps":8,"Staffing capacity":5
            },
            "beneficence":"Leverage data for safety and service improvements.",
            "nonmaleficence":"Prevent civil liberties erosion and misuse of data.",
            "autonomy":"Respect public consent/contestability in surveillance deployments.",
            "justice":"Avoid disparate impacts and racialized surveillance.",
            "explicability":"Full disclosure of capabilities, use, retention, and oversight."
        })
    elif name.startswith("Riverton"):
        f.update({
            "incident_type":"AI‑enabled network attack",
            "nist":["Identify","Protect","Detect","Respond","Recover"],
            "description":"Adversarial ML steered autonomous defenses into unsafe plant shutdown.",
            "stakeholders":["Residents","City Employees","Vendors","City Council","Regulators"],
            "values":["Safety","Trust","Transparency","Autonomy","Equity","Privacy"],
            "constraints_scores":{
                "Funding limitations":5,"Authority fragmentation":6,"Procurement opacity":6,
                "Vendor opacity":9,"Policy/oversight gaps":7,"Staffing capacity":6
            },
            "beneficence":"Restore safe water service; protect public health.",
            "nonmaleficence":"Prevent further unsafe automated actions; contain spillover risk.",
            "autonomy":"Ensure decisions are explainable, auditable, and within legal authority.",
            "justice":"Equitable restoration across neighborhoods; prioritize critical users.",
            "explicability":"Explain AI failure mode and risk; justify disable/rollback choices."
        })
    st.session_state.form = f

if preset != "— None —":
    apply_preset(preset)

# ----------------------------
# Header
# ----------------------------
st.title("🛡️ Ethical Cybersecurity Decision Tool (Municipal)")
st.caption("Integrates NIST CSF 2.0, principlist ethics, and municipal governance constraints for real‑time incident support.")

# ----------------------------
# 1) Incident Overview
# ----------------------------
st.markdown("### 1) Incident Overview")

colA, colB = st.columns([1,2])
with colA:
    incident_type = st.selectbox(
        "Incident type",
        ["Ransomware","Data Breach","Unauthorized Access","Service Disruption",
         "Technology Repurposing","AI‑enabled Network Attack","Other"],
        index=0 if st.session_state.form.get("incident_type") is None else
        ["Ransomware","Data Breach","Unauthorized Access","Service Disruption",
         "Technology Repurposing","AI‑enabled Network Attack","Other"].index(
            st.session_state.form.get("incident_type","Ransomware"))
    )
with colB:
    description = st.text_area(
        "Brief description (what, where, impact)",
        value=st.session_state.form.get("description",""),
        height=100
    )

with st.expander("NIST CSF 2.0 functions (quick reference)"):
    st.write(NIST_HELP)

nist = st.multiselect(
    "NIST CSF functions implicated",
    list(NIST_HELP.keys()),
    default=st.session_state.form.get("nist",[])
)

# ----------------------------
# 2) Stakeholders & Public Values
# ----------------------------
st.markdown("### 2) Stakeholders & Public Values")

stakeholders = st.multiselect(
    "Stakeholders impacted",
    ["Residents","City Employees","Vendors","City Council","Regulators","Media","Community Orgs","Emergency Services","Schools","Other"],
    default=st.session_state.form.get("stakeholders",[])
)

values = st.multiselect(
    "Public values at risk",
    ["Safety","Privacy","Transparency","Trust","Equity","Autonomy","Service Continuity","Accountability"],
    default=st.session_state.form.get("values",[])
)

# ----------------------------
# 3) Institutional & Governance Constraints
# ----------------------------
st.markdown("### 3) Institutional & Governance Constraints")

c_cols = st.columns(6)
constraint_scores = {}
for (i,(name,helptext)) in enumerate(CONSTRAINTS):
    with c_cols[i]:
        constraint_scores[name] = st.slider(name, 0, 10, value=st.session_state.form.get("constraints_scores",{}).get(name,5), help=helptext)

notes = st.text_area(
    "Context notes (political pressures, legal triggers, inter‑agency issues)",
    value="\n".join(f"- {k}: {DEFAULT_NOTES[k]}" for k in DEFAULT_NOTES) if not st.session_state.form else
          "\n".join([f"- {k}: {DEFAULT_NOTES[k]}" for k in DEFAULT_NOTES])
)

# ----------------------------
# 4) Principlist Ethics
# ----------------------------
st.markdown("### 4) Principlist Evaluation")
with st.expander("Principles reference"):
    st.write(PRINCIPLE_HELP)

beneficence = st.text_area("Beneficence – How does your action promote public well‑being?",
                           value=st.session_state.form.get("beneficence",""))
nonmaleficence = st.text_area("Non‑maleficence – How does it avoid or reduce harm?",
                              value=st.session_state.form.get("nonmaleficence",""))
autonomy = st.text_area("Autonomy – Rights, lawful authority, and choice respected?",
                        value=st.session_state.form.get("autonomy",""))
justice = st.text_area("Justice – Fair distribution; any disparate impacts mitigated?",
                       value=st.session_state.form.get("justice",""))
explicability = st.text_area("Explicability – Can you clearly explain and justify?",
                             value=st.session_state.form.get("explicability",""))

# ----------------------------
# 5) Rapid vs Standard sections
# ----------------------------
st.markdown("### 5) Ethical Tension Snapshot")

def tension_score():
    # weights tuned for quick signal, not “truth”
    c = sum(constraint_scores.values())          # 0–60
    s = len(stakeholders) * 4                    # 0–40
    v = len(values) * 3                          # 0–24
    empties = sum(1 for t in [beneficence,nonmaleficence,autonomy,justice,explicability] if not t.strip())
    penalty = empties * 6                        # 0–30
    raw = c + s + v + penalty
    return min(100, int(raw/1.8))

score = tension_score()
st.progress(score, text=f"Tension score: {score}/100")

if score < 35:
    st.success("Low–moderate tension. Proceed with documented justification; monitor conditions.")
elif score < 70:
    st.warning("Elevated tension. Document trade‑offs, consult cross‑functional leads, and time‑box decisions.")
else:
    st.error("High tension. Escalate governance, ensure legal/comms review, consider interim/least‑harm options.")

if mode.startswith("Rapid"):
    st.info("**Rapid mode:** focus on minimal fields → Description, NIST functions, top two constraints, and one‑line notes per principle. You can refine later.")
else:
    st.caption("Standard mode enables fuller documentation and export.")

# ----------------------------
# 6) Decision & NIST alignment builder
# ----------------------------
st.markdown("### 6) Provisional Decision & NIST Alignment")

action = st.text_area(
    "Proposed action (what you will do now)",
    placeholder="e.g., Isolate affected network segments; refuse ransom; publish outage status q4h; prioritize water billing restoration; invoke vendor rollback...",
    height=90
)

nist_alignment = st.multiselect(
    "Which CSF outcomes does this action align with?",
    [
        "ID.AM – Asset mgmt updated",
        "ID.RA – Risk assessment refined",
        "PR.AC – Access controls applied",
        "PR.DS – Data security safeguards",
        "DE.CM – Continuous monitoring",
        "RS.MI – Mitigation executed",
        "RS.CO – Communications executed",
        "RC.RP – Recovery planning enacted",
        "RC.IM – Improvements captured"
    ],
    default=[]
)

# ----------------------------
# 7) Build justification & export
# ----------------------------
st.markdown("### 7) Generate Justification")

if st.button("✅ Generate structured justification"):
    now = datetime.utcnow().isoformat() + "Z"
    record = {
        "timestamp_utc": now,
        "mode": mode,
        "preset": preset,
        "incident_type": incident_type,
        "description": description,
        "nist_functions": nist,
        "stakeholders": stakeholders,
        "values": values,
        "constraints_scores": constraint_scores,
        "notes": notes,
        "principlist": {
            "beneficence": beneficence,
            "non_maleficence": nonmaleficence,
            "autonomy": autonomy,
            "justice": justice,
            "explicability": explicability
        },
        "proposed_action": action,
        "nist_alignment": nist_alignment,
        "tension_score": score
    }

    # human‑readable markdown
    md = f"""# Ethical Decision Justification (Municipal Cybersecurity)

**Timestamp (UTC):** {now}  
**Mode:** {mode}  
**Preset:** {preset}

## Incident
- **Type:** {incident_type}  
- **Description:** {description}

## NIST CSF 2.0 Functions
- {", ".join(nist) if nist else "—"}

## Stakeholders & Values
- **Stakeholders:** {", ".join(stakeholders) if stakeholders else "—"}
- **Public Values at Risk:** {", ".join(values) if values else "—"}

## Institutional & Governance Constraints (0–10)
{chr(10).join([f"- **{k}:** {constraint_scores[k]} — {DEFAULT_NOTES.get(k,'')}" for k,_ in CONSTRAINTS])}

**Context notes:**  
{notes}

## Principlist Evaluation
- **Beneficence:** {beneficence or '—'}
- **Non‑maleficence:** {nonmaleficence or '—'}
- **Autonomy:** {autonomy or '—'}
- **Justice:** {justice or '—'}
- **Explicability:** {explicability or '—'}

## Provisional Action
{action or '—'}

**NIST outcomes referenced:** {", ".join(nist_alignment) if nist_alignment else "—"}  
**Ethical tension score:** {score}/100
"""

    st.success("Structured justification created below. You can copy, or export JSON/Markdown.")
    st.markdown(md)

    st.download_button(
        "⬇️ Download JSON",
        data=json.dumps(record, indent=2),
        file_name="municipal_ethics_decision.json",
        mime="application/json"
    )
    st.download_button(
        "⬇️ Download Markdown",
        data=md,
        file_name="municipal_ethics_decision.md",
        mime="text/markdown"
    )

# ----------------------------
# Footer
# ----------------------------
with st.expander("About this prototype & thesis alignment"):
    st.markdown("""
- **Ethics**: Principlist (beneficence, non‑maleficence, autonomy, justice, explicability) used as the core evaluative lens.  
- **Standards**: Mapped to **NIST CSF 2.0** functions/outcomes to anchor actions in recognized practice.  
- **Municipal governance**: Explicit sliders for funding, authority fragmentation, procurement/vendor opacity, policy gaps, staffing—reflecting Ch. 3 constraints.  
- **Operational reality**: Rapid vs Standard modes; exportable, auditable justification for accountability and post‑incident learning.
""")
