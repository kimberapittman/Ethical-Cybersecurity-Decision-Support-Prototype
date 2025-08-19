import streamlit as st
from datetime import datetime

# ----------------------------
# Page + Layout
# ----------------------------
st.set_page_config(
    page_title="Municipal Ethical Cyber Decision Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("🛡️ Municipal Ethical Cyber Decision Tool")
st.caption("Integrates NIST CSF actions with principlist ethical reasoning under municipal constraints.")

# ----------------------------
# Reference Data
# ----------------------------
PRINCIPLES = ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"]

NIST_FUNCTIONS = {
    "Identify": [
        "Inventory affected assets/services",
        "Classify criticality & dependencies",
        "Map stakeholders & harms",
        "Establish legal/policy requirements",
    ],
    "Protect": [
        "Apply access controls/segmentation",
        "Harden endpoints & configurations",
        "Safeguard backups & keys",
        "Protect sensitive data",
    ],
    "Detect": [
        "Triage alerts & indicators",
        "Hunt for persistence/lateral movement",
        "Validate scope & root cause",
        "Monitor for recurrence",
    ],
    "Respond": [
        "Containment & eradication",
        "Ransom/payment decision path",
        "Regulatory/comms notifications",
        "Coordinate with law enforcement",
    ],
    "Recover": [
        "Restore systems/services",
        "Validate integrity & safety",
        "Lessons learned & postmortem",
        "Improvements & resilience upgrades",
    ],
}

# Ethical prompts mapped to NIST CSF (ties the “how” to the “why”)
NIST_TO_ETHICAL_QUESTIONS = {
    "Identify": {
        "Beneficence": "Which essential services/people benefit most from rapid stabilization?",
        "Non-maleficence": "What foreseeable harms arise if we misclassify criticality?",
        "Justice": "Are impacts unequal across neighborhoods or groups?",
        "Autonomy": "Whose data/choices are implicated by our asset/stakeholder mapping?",
        "Explicability": "Can we clearly explain our scoping assumptions and criteria?",
    },
    "Protect": {
        "Beneficence": "Which protections most directly reduce imminent risk to the public?",
        "Non-maleficence": "Could protective controls themselves cause harm (e.g., lockouts)?",
        "Justice": "Do protections shift burdens unfairly (e.g., service cuts in one area)?",
        "Autonomy": "Do controls respect individuals’ rights/consent expectations?",
        "Explicability": "Can protections and trade-offs be explained to non-experts?",
    },
    "Detect": {
        "Beneficence": "Will faster detection materially improve safety/outcomes?",
        "Non-maleficence": "What is the harm of false positives/negatives here?",
        "Justice": "Are monitoring capabilities equitably deployed?",
        "Autonomy": "Does detection infringe privacy beyond proportional need?",
        "Explicability": "Is our detection rationale transparent and auditable?",
    },
    "Respond": {
        "Beneficence": "What action restores essential services most quickly and safely?",
        "Non-maleficence": "Does this response encourage future attacks or cause collateral harm?",
        "Justice": "Are costs/risks of response fairly distributed?",
        "Autonomy": "Are we acting within lawful authority and respecting due process?",
        "Explicability": "Can we defend this response publicly and to oversight bodies?",
    },
    "Recover": {
        "Beneficence": "Which recovery path best improves long-term well-being?",
        "Non-maleficence": "How do we avoid reintroducing vulnerabilities or unsafe configs?",
        "Justice": "Are restorations prioritized fairly (not just politically)?",
        "Autonomy": "Are restoration choices transparent and respect residents’ expectations?",
        "Explicability": "Is the recovery rationale clear, documented, and reviewable?",
    },
}

# Simple keyword-based heuristic to auto-suggest implicated principles
AUTO_KEYWORDS = {
    "Beneficence": ["restore", "safety", "public health", "911", "water", "service"],
    "Non-maleficence": ["harm", "injury", "extortion", "ransom", "misuse", "outage"],
    "Autonomy": ["privacy", "consent", "choice", "monitor", "surveillance", "ai"],
    "Justice": ["equity", "disparity", "fair", "disproportionate", "neighborhood"],
    "Explicability": ["transparency", "explain", "disclose", "accountability", "audit"],
}

# Weights used in the decision matrix (you can tune for your thesis emphasis)
PRINCIPLE_WEIGHTS = {
    "Beneficence": 2.0,
    "Non-maleficence": 2.0,
    "Justice": 1.5,
    "Autonomy": 1.25,
    "Explicability": 1.25,
}

# ----------------------------
# Sidebar: Mode + About
# ----------------------------
with st.sidebar:
    st.subheader("Run Mode")
    crisis_mode = st.toggle("🚨 Crisis Mode (2–5 min workflow)", value=False)
    st.markdown("---")
    st.markdown("**About**")
    st.write(
        "- **Principlist Framework** surfaces value tensions (why).  \n"
        "- **NIST CSF 2.0** structures the operational levers (how).  \n"
        "- **Constraints** capture municipal reality (can)."
    )

# ----------------------------
# 1) Incident Overview
# ----------------------------
st.markdown("### 1) Incident Overview")

colA, colB = st.columns([1, 1])
with colA:
    incident_type = st.selectbox(
        "Incident type",
        ["Ransomware", "Phishing", "Unauthorized Access", "Data Breach", "AI/Autonomous System Failure", "Other"],
    )
with colB:
    severity = st.select_slider("Assessed severity", options=["Low", "Moderate", "High", "Severe"], value="Moderate")

incident_description = st.text_area(
    "Briefly describe the incident (what failed, who is affected, immediate risks):",
    placeholder="e.g., Ransomware impacted finance, water billing, and permitting; 911 unaffected; public-facing portals offline..."
)

# ----------------------------
# 2) NIST CSF Functions + Ethical Prompts
# ----------------------------
st.markdown("### 2) NIST CSF Functions in Play + Value Prompts")

nist_selected = st.multiselect(
    "Select the NIST CSF functions relevant now:",
    list(NIST_FUNCTIONS.keys()),
    default=(["Respond", "Recover"] if "ransom" in incident_description.lower() else []),
)

# Auto-suggest implicated principles from the incident description
def auto_principles(text: str):
    s = text.lower()
    hits = []
    for p, keys in AUTO_KEYWORDS.items():
        if any(k in s for k in keys):
            hits.append(p)
    # If nothing matched, suggest a balanced default
    return hits or ["Beneficence", "Non-maleficence", "Explicability"]

suggested_principles = auto_principles(incident_description)

st.info(f"Auto‑suggested ethical principles implicated (based on description): {', '.join(suggested_principles)}")

# Show ethical prompts aligned to the selected NIST functions (crisis mode collapses detail)
if nist_selected:
    if not crisis_mode:
        tabs = st.tabs(nist_selected)
        for i, fn in enumerate(nist_selected):
            with tabs[i]:
                st.markdown(f"**{fn} – Common actions**")
                st.write("\n".join([f"- {a}" for a in NIST_FUNCTIONS[fn]]))
                st.markdown(f"**{fn} – Ethical prompts (Principlist)**")
                q = NIST_TO_ETHICAL_QUESTIONS[fn]
                for p in PRINCIPLES:
                    st.write(f"- *{p}*: {q[p]}")
    else:
        st.markdown("**Crisis Mode prompts (condensed):**")
        for fn in nist_selected:
            st.write(f"- {fn}: " + "; ".join([NIST_TO_ETHICAL_QUESTIONS[fn][p] for p in suggested_principles]))

# ----------------------------
# 3) Stakeholders & Values
# ----------------------------
st.markdown("### 3) Stakeholders & Public Values")

col1, col2 = st.columns(2)
with col1:
    stakeholders = st.multiselect(
        "Stakeholders impacted",
        ["Residents", "City Employees", "Vendors", "Elected Officials", "Emergency Services", "Regulators", "Media", "Other"],
        default=["Residents", "City Employees"] if not crisis_mode else ["Residents", "Emergency Services"],
    )
with col2:
    values_at_risk = st.multiselect(
        "Public values at risk",
        ["Privacy", "Transparency", "Trust", "Safety", "Equity", "Autonomy", "Accountability"],
        default=["Safety", "Trust", "Transparency"] if "ransom" in incident_description.lower() else [],
    )

# ----------------------------
# 4) Constraints (Institutional & Governance)
# ----------------------------
st.markdown("### 4) Institutional & Governance Constraints")

colc1, colc2, colc3, colc4 = st.columns(4)
with colc1:
    budget = st.slider("Budget constraints", 0, 10, 6 if crisis_mode else 5)
with colc2:
    staffing = st.slider("Staffing capacity", 0, 10, 6 if crisis_mode else 5)
with colc3:
    legal = st.slider("Legal/policy complexity", 0, 10, 5)
with colc4:
    time_pressure = st.slider("Time pressure/urgency", 0, 10, 8 if crisis_mode else 6)

constraint_notes = st.text_area(
    "Notes on constraints (e.g., fragmented authority, vendor opacity, election cycle, public pressure):",
    placeholder="e.g., Split authority across IT/Utilities/Mayor; vendor contract blocks code audit; council session in 24h...",
)

# ----------------------------
# 5) Ethical Evaluation (Principlist) – short or full
# ----------------------------
st.markdown("### 5) Ethical Evaluation (Principlist)")

def default_text(p):
    if p in suggested_principles:
        return f"(Auto‑flagged) Key concerns for {p.lower()} given the incident description…"
    return ""

colp = st.columns(5)
inputs = {}
for i, p in enumerate(PRINCIPLES):
    with colp[i]:
        inputs[p] = st.text_area(p, value=default_text(p), height=100 if crisis_mode else 140)

# ----------------------------
# 6) Decision Options & Matrix
# ----------------------------
st.markdown("### 6) Decision Options & Ethical Impact Matrix")

st.caption("Rate each option’s expected effect on each principle: -2 (strongly harms) to +2 (strongly advances).")

opt_cols = st.columns(3)
options = []
for i in range(3):
    with opt_cols[i]:
        title = st.text_input(f"Option {i+1} – label", value=["Rebuild from backups", "Limited partial restoration", "Pay ransom & decrypt"][i] if i==0 else "")
        if i == 1 and not title:
            title = st.text_input(f"Option {i+1} – label ", value="Limited partial restoration")
        if i == 2 and not title:
            title = st.text_input(f"Option {i+1} – label  ", value="Pay ransom & decrypt")

        scores = {}
        for p in PRINCIPLES:
            scores[p] = st.slider(f"{title} → {p}", -2, 2, 0, key=f"{title}-{p}")
        options.append({"title": title, "scores": scores})

# Weighted scoring
def score_option(opt):
    return sum(opt["scores"][p] * PRINCIPLE_WEIGHTS[p] for p in PRINCIPLES)

ranked = sorted(
    [{"title": o["title"], "score": score_option(o), "scores": o["scores"]} for o in options if o["title"].strip()],
    key=lambda x: x["score"],
    reverse=True
)

# ----------------------------
# 7) Synthesis & Recommendation
# ----------------------------
st.markdown("### 7) Synthesis & Recommendation")

def calc_tension_index():
    # crude composite: constraints + time pressure + implicated principles + severity
    constraints_load = budget + staffing + legal + time_pressure  # 0–40
    principle_load = len([p for p,v in inputs.items() if v.strip()]) * 2  # 0–10
    sev = {"Low": 2, "Moderate": 5, "High": 8, "Severe": 10}[severity]
    raw = constraints_load + principle_load + sev
    return min(int(raw * 1.5), 100)

tension = calc_tension_index()
st.progress(tension, text=f"Ethical tension index: {tension}/100")

if ranked:
    best = ranked[0]
    st.success(f"**Provisional Recommendation:** {best['title']} (weighted ethical score: {best['score']:.1f})")
else:
    st.warning("Add at least one decision option to compute a recommendation.")

# ----------------------------
# 8) Justification Narrative (exportable)
# ----------------------------
st.markdown("### 8) Exportable Justification")

def fmt_scores(sc):
    return "; ".join([f"{p}: {('+' if v>0 else '')}{v}" for p, v in sc.items()])

timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

if st.button("Generate Justification"):
    rec_line = f"Recommended path: {ranked[0]['title']} (ethical score {ranked[0]['score']:.1f})." if ranked else "Recommended path: (pending selection)."
    justification = f"""
Municipal Ethical Cyber Decision Log — {timestamp}

Incident
- Type: {incident_type} | Severity: {severity}
- Description: {incident_description}

NIST CSF functions engaged:
- {", ".join(nist_selected) if nist_selected else "(none selected)"}

Stakeholders & public values:
- Stakeholders: {", ".join(stakeholders) if stakeholders else "(none)"}
- Values at risk: {", ".join(values_at_risk) if values_at_risk else "(none)"}

Institutional & governance constraints:
- Budget={budget}/10 | Staffing={staffing}/10 | Legal/Policy={legal}/10 | Time Pressure={time_pressure}/10
- Notes: {constraint_notes or '(none)'}
- Ethical tension index: {tension}/100

Principlist evaluation:
- Beneficence: {inputs['Beneficence'] or '(n/a)'}
- Non-maleficence: {inputs['Non-maleficence'] or '(n/a)'}
- Justice: {inputs['Justice'] or '(n/a)'}
- Autonomy: {inputs['Autonomy'] or '(n/a)'}
- Explicability: {inputs['Explicability'] or '(n/a)'}

Decision options (ethical impacts; -2 harms → +2 advances):
{chr(10).join([f"- {o['title']}: {fmt_scores(o['scores'])}" for o in ranked]) or '(no options)'}

Synthesis
- {rec_line}
- Rationale links NIST CSF actions to ethical requirements:
  - Identify/Protect/Detect/Respond/Recover prompts considered for selected functions.
  - Trade-offs documented across beneficence (public well-being), non-maleficence (avoid foreseeable harm),
    justice (fairness/equity), autonomy (rights/lawful authority), explicability (transparency/accountability).

Governance
- This decision is justified against documented constraints and is suitable for internal review, public explanation,
  and lessons-learned integration into future policy, training, and procurement.
"""
    st.code(justification)
    st.download_button(
        "📄 Download justification (.txt)",
        data=justification,
        file_name="municipal_ethical_decision_justification.txt",
        mime="text/plain",
    )

# ----------------------------
# Footer note for thesis mapping
# ----------------------------
st.caption(
    "Design notes: Principlist = value framing (why); NIST CSF = operational levers (how); "
    "Constraints = municipal realism (can). Crisis Mode condenses prompts for 2–5 minute use."
)
