import streamlit as st
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(page_title="Municipal Ethical Cyber Decision-Support", layout="wide")

# ---------- Simple rule-based NLP helpers (no external deps) ----------
NIST_KB = {
    "ransomware": ["Identify", "Protect", "Detect", "Respond", "Recover"],
    "phishing":   ["Protect", "Detect", "Respond", "Recover"],
    "unauthorized access": ["Detect", "Respond", "Recover", "Identify"],
    "data breach": ["Identify", "Protect", "Detect", "Respond", "Recover"],
    "surveillance": ["Identify", "Protect", "Respond"],
    "ai-enabled": ["Identify", "Detect", "Respond", "Recover"]
}

ETHICAL_HINTS = {
    "privacy": ["Autonomy", "Justice", "Explicability"],
    "surveillance": ["Autonomy", "Justice", "Explicability", "Non-maleficence"],
    "ransom": ["Justice", "Non-maleficence", "Beneficence"],
    "water": ["Beneficence", "Non-maleficence", "Justice", "Explicability"],
    "health": ["Beneficence", "Non-maleficence", "Justice"],
    "email": ["Autonomy", "Explicability"],
    "outage": ["Non-maleficence", "Beneficence", "Explicability"],
    "protest": ["Justice", "Autonomy", "Explicability"],
    "equity": ["Justice"],
    "ai": ["Autonomy", "Explicability", "Non-maleficence"],
}

GOV_CONSTRAINTS = [
    "Fragmented authority / unclear decision rights",
    "Procurement did not disclose ethical/surveillance risk",
    "Limited budget / staffing",
    "No/weak incident playbooks or continuity plans",
    "Vendor opacity (limited audit of code/training data)",
    "Lack of public engagement / oversight",
    "Legacy tech / poor segmentation / patch backlog",
    "Ambiguous data sharing/retention policies"
]

NIST_ACTIONS = {
    "Identify": [
        "Confirm crown jewels & service criticality",
        "Establish incident objectives, decision authority, and escalation paths",
        "Map stakeholders and equity impacts"
    ],
    "Protect": [
        "Harden access (MFA, least privilege, network segmentation)",
        "Freeze risky changes; ensure backups are protected/offline",
        "Apply emergency configuration baselines"
    ],
    "Detect": [
        "Correlate alerts; verify indicators of compromise",
        "Expand monitoring to adjacent systems",
        "Preserve logs and evidence (chain of custody)"
    ],
    "Respond": [
        "Contain (isolate affected hosts/segments); coordinate with counsel/LE",
        "Activate comms plan; publish clear, non-speculative updates",
        "Decide on takedown/disablement with proportionality & due process"
    ],
    "Recover": [
        "Restore by criticality with integrity checks",
        "Post-incident review; address root causes & policy gaps",
        "Update playbooks; brief council/public with lessons learned"
    ],
}

PRINCIPLES = ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"]

def suggest_nist(incident_type:str, description:str):
    it = incident_type.lower()
    seed = []
    for k, v in NIST_KB.items():
        if k in it or k in description.lower():
            seed.extend(v)
    # fallback if nothing matched
    if not seed:
        seed = ["Identify", "Protect", "Detect", "Respond", "Recover"]
    # dedupe preserving order
    seen, ordered = set(), []
    for x in seed:
        if x not in seen:
            ordered.append(x); seen.add(x)
    return ordered

def suggest_principles(description:str):
    hits = []
    text = description.lower()
    for k, plist in ETHICAL_HINTS.items():
        if k in text:
            hits.extend(plist)
    if not hits:
        hits = ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"]
    seen, ordered = set(), []
    for p in hits:
        if p not in seen:
            ordered.append(p); seen.add(p)
    return ordered

def quick_ethics_blurbs(principles, ctx):
    blurbs = []
    for p in PRINCIPLES:
        if p in principles:
            if p == "Beneficence":
                blurbs.append("Beneficence: Prioritize restoring essential services and public well-being.")
            if p == "Non-maleficence":
                blurbs.append("Non-maleficence: Avoid foreseeable harms from containment, disclosure, or automation side-effects.")
            if p == "Autonomy":
                blurbs.append("Autonomy: Respect rights, choice, and due process—minimize unnecessary surveillance or coercive measures.")
            if p == "Justice":
                blurbs.append("Justice: Distribute burdens/benefits fairly; prevent disproportionate impact on specific neighborhoods or groups.")
            if p == "Explicability":
                blurbs.append("Explicability: Communicate decisions and rationales clearly, with auditable records.")
    return blurbs

def score_tension(selected_principles, selected_nist, constraints, stakeholders, values):
    # A simple, transparent heuristic you can report in Chapter IV
    base = 10
    base += 5 * len(selected_principles)
    base += 3 * len(selected_nist)
    base += 6 * len(constraints)
    base += 3 * len(stakeholders)
    base += 4 * len(values)
    return min(base, 100)

# ---------- Sidebar: mode and presets ----------
st.sidebar.header("Mode & Presets")
mode = st.sidebar.radio("Mode", ["Quick triage (2–3 min)", "Full deliberation (8–12 min)"])

preset = st.sidebar.selectbox("Load a preset (optional)", [
    "— None —",
    "Baltimore-style: Ransomware on core city services",
    "San Diego-style: Tech repurposed for surveillance",
    "Riverton-style: AI-enabled incident on critical infra"
])

preset_data = {
    "Baltimore-style: Ransomware on core city services": dict(
        incident_type="Ransomware",
        description="City servers encrypted; email and payment portals offline; pressure to pay ransom vs. restore from backups.",
        stakeholders=["Residents","City Employees","City Council","Courts/Recorders"],
        values=["Safety","Trust","Transparency","Equity","Autonomy"],
        constraints=["Legacy tech / poor segmentation / patch backlog",
                     "Limited budget / staffing",
                     "No/weak incident playbooks or continuity plans"]
    ),
    "San Diego-style: Tech repurposed for surveillance": dict(
        incident_type="Technology repurposing / Surveillance use",
        description="Sensor-enabled streetlights used by police for investigations without prior public process; policy and equity concerns.",
        stakeholders=["Residents","City Council","Media","Civil Rights Groups"],
        values=["Privacy","Transparency","Trust","Equity","Autonomy"],
        constraints=["Procurement did not disclose ethical/surveillance risk",
                     "Lack of public engagement / oversight",
                     "Ambiguous data sharing/retention policies",
                     "Fragmented authority / unclear decision rights"]
    ),
    "Riverton-style: AI-enabled incident on critical infra": dict(
        incident_type="AI-enabled intrusion on water treatment network",
        description="AI monitor auto-acted on adversarial signal, disrupting water distribution; choice between disabling AI or retraining live.",
        stakeholders=["Residents","Public Utilities Board","Vendors","Mayor’s Office"],
        values=["Safety","Trust","Transparency","Equity","Autonomy"],
        constraints=["Vendor opacity (limited audit of code/training data)",
                     "Fragmented authority / unclear decision rights",
                     "No/weak incident playbooks or continuity plans"]
    )
}

# ---------- Intro ----------
st.title("🛡️ Municipal Ethical Cyber Decision-Support (Prototype)")
st.caption("Integrates NIST CSF 2.0 + Principlist ethics, and considers municipal institutional and governance constraints.")

with st.expander("About this prototype"):
    st.markdown("""
- **Purpose:** Real-time support for municipal incident decisions that involve ethical trade-offs.
- **Backbone:** NIST CSF 2.0 (Identify/Protect/Detect/Respond/Recover) + Principlist ethics (Beneficence, Non‑maleficence, Autonomy, Justice, Explicability).
- **Context:** Reflects institutional and governance constraints common in municipalities (procurement opacity, fragmented authority, legacy tech, limited staffing, etc.).
""")

# ---------- Incident Overview ----------
st.markdown("### 1) Incident overview")
colA, colB = st.columns([1.2, 2])

if preset != "— None —":
    pd = preset_data[preset]
else:
    pd = dict(incident_type="", description="", stakeholders=[], values=[], constraints=[])

with colA:
    incident_type = st.text_input("Incident type", pd.get("incident_type",""))
    description = st.text_area("Brief description", pd.get("description",""), height=110)
with colB:
    suggested_nist = suggest_nist(incident_type, description)
    st.write("**Suggested NIST CSF functions** (editable):")
    selected_nist = st.multiselect("", ["Identify","Protect","Detect","Respond","Recover"], default=suggested_nist)

# ---------- Stakeholders, values, constraints ----------
st.markdown("### 2) Stakeholders, values, and constraints")

col1, col2, col3 = st.columns(3)
with col1:
    stakeholders = st.multiselect(
        "Stakeholders affected",
        ["Residents","City Employees","Vendors","City Council","Mayor’s Office",
         "Public Utilities Board","Police Department","Civil Rights Groups","Media","Courts/Recorders"],
        default=pd.get("stakeholders",[])
    )
with col2:
    values = st.multiselect(
        "Public values at risk",
        ["Privacy","Transparency","Trust","Safety","Equity","Autonomy"],
        default=pd.get("values",[])
    )
with col3:
    constraints = st.multiselect(
        "Institutional & governance constraints",
        GOV_CONSTRAINTS,
        default=pd.get("constraints",[])
    )

# ---------- Ethical evaluation ----------
st.markdown("### 3) Ethical evaluation (Principlist)")

auto_principles = suggest_principles(description + " " + " ".join(values))
selected_principles = st.multiselect(
    "Suggested principles (editable)", PRINCIPLES, default=auto_principles
)

if mode.startswith("Quick"):
    st.info("Quick triage mode: we’ll generate short principle prompts for rapid documentation.")
    blurbs = quick_ethics_blurbs(selected_principles, description)
    for b in blurbs:
        st.write("• " + b)
else:
    colp1, colp2 = st.columns(2)
    with colp1:
        beneficence = st.text_area("Beneficence – promote well-being", "")
        autonomy = st.text_area("Autonomy – respect rights/choice", "")
        justice = st.text_area("Justice – fairness/equity", "")
    with colp2:
        non_maleficence = st.text_area("Non‑maleficence – avoid harm", "")
        explicability = st.text_area("Explicability – transparency/accountability", "")

# ---------- Tension score ----------
st.markdown("### 4) Ethical tension score")
score = score_tension(selected_principles, selected_nist, constraints, stakeholders, values)
st.progress(score, text=f"Ethical/contextual tension: {score}/100")

if score < 35:
    st.success("Low tension: document rationale and proceed.")
elif score < 70:
    st.warning("Moderate tension: ensure proportionality, comms, and oversight are in place.")
else:
    st.error("High tension: escalate, ensure cross‑dept decision rights, consider external ethics/LE counsel.")

# ---------- Action plan (NIST-aligned) ----------
st.markdown("### 5) NIST‑aligned action plan (editable)")
plan = []
for f in selected_nist:
    st.write(f"**{f}**")
    chosen = st.multiselect(f"Select {f} actions", NIST_ACTIONS[f], default=NIST_ACTIONS[f], key=f)
    plan.extend([f"{f}: {a}" for a in chosen])

# ---------- Communication checklist (explicability in practice) ----------
with st.expander("Public communication & accountability checklist"):
    st.checkbox("Name a responsible official and decision authority for this incident", value=True)
    st.checkbox("Publish plain‑language status, impacts, and next steps (no speculation)", value=True)
    st.checkbox("State data handling, retention, and law‑enforcement coordination terms", value=True)
    st.checkbox("Record rationale for decisions (pay/no‑pay; enable/disable tech; scope of surveillance)", value=True)
    st.checkbox("Equity statement: assess & mitigate disproportionate impact by neighborhood/group", value=True)

# ---------- Generate justification ----------
st.markdown("### 6) Generate justification")
if st.button("Create decision record"):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    ethics_summary = ""
    if mode.startswith("Quick"):
        ethics_summary = "\n".join(quick_ethics_blurbs(selected_principles, description))
    else:
        ethics_summary = "\n".join([
            f"Beneficence: {beneficence or '—'}",
            f"Non-maleficence: {non_maleficence or '—'}",
            f"Autonomy: {autonomy or '—'}",
            f"Justice: {justice or '—'}",
            f"Explicability: {explicability or '—'}",
        ])

    record = f"""# Municipal Cyber Decision Record
Timestamp: {timestamp}

## Incident
Type: {incident_type or '—'}
Description: {description or '—'}

## Frameworks
NIST CSF: {", ".join(selected_nist)}
Principlist: {", ".join(selected_principles)}

## Context
Stakeholders: {", ".join(stakeholders) or '—'}
Public values at risk: {", ".join(values) or '—'}
Constraints: {", ".join(constraints) or '—'}
Ethical/context tension score: {score}/100

## Action plan (NIST‑aligned)
- """ + "\n- ".join(plan) + f"""

## Ethical rationale
{ethics_summary}

## Notes
This decision reflects principlist ethical reasoning and NIST CSF 2.0 practices, applied within municipal governance constraints.
"""
    st.code(record, language="markdown")
    st.download_button("📥 Download decision record (.md)", record, file_name="decision_record.md")

# ---------- Footer hint ----------
st.caption("Prototype: for thesis demonstration (Chapter IV) — aligns case presets with your Chapter III scenarios.")

