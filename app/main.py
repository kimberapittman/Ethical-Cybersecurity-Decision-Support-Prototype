import streamlit as st
from datetime import datetime
import re

# ---------- Page config ----------
st.set_page_config(page_title="Municipal Ethical Cyber Decision-Support", layout="wide", initial_sidebar_state="expanded")

# ---------- Minimal styling (cosmetic only) ----------
st.markdown("""
<style>
.listbox{background:#f9fbff;border-left:4px solid #4C8BF5;padding:10px 14px;border-radius:8px;margin:6px 0 14px;}
.section-note{color:#6b7280;font-size:0.9rem;margin:-4px 0 10px 0;}
.tight-list{margin:0.25rem 0 0 1.15rem;padding:0;}
.tight-list li{margin:6px 0;}
.sub{color:#6b7280;font-size:0.95rem;}
.badges{display:flex;flex-wrap:wrap;gap:.35rem;margin:.35rem 0 0 0;}
.badge{display:inline-block;padding:.2rem .5rem;border-radius:999px;border:1px solid #e5e7eb;font-size:.85rem}
.badge.nist{background:#eef2ff;border-color:#c7d2fe;}
.badge.principle{background:#ecfeff;border-color:#a5f3fc;}
.badge.note{background:#fef9c3;border-color:#fde68a;}
h3, h4 { margin-bottom: .4rem; }
</style>
""", unsafe_allow_html=True)

# ---------- NIST CSF 2.0 constants ----------
NIST_FUNCTIONS = [
    "Govern (GV)",
    "Identify (ID)",
    "Protect (PR)",
    "Detect (DE)",
    "Respond (RS)",
    "Recover (RC)",
]

# ---------- Simple rule-based NLP helpers (no external deps) ----------
NIST_KB = {
    "ransomware": ["Govern (GV)", "Identify (ID)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"],
    "phishing":   ["Govern (GV)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"],
    "unauthorized access": ["Govern (GV)", "Detect (DE)", "Respond (RS)", "Recover (RC)", "Identify (ID)"],
    "data breach": ["Govern (GV)", "Identify (ID)", "Protect (PR)", "Detect (DE)", "Respond (RS)", "Recover (RC)"],
    "surveillance": ["Govern (GV)", "Identify (ID)", "Protect (PR)", "Respond (RS)"],
    "ai-enabled": ["Govern (GV)", "Identify (ID)", "Detect (DE)", "Respond (RS)", "Recover (RC)"]
}

# ---------- Open-ended incident archetypes (dropdown) ----------
OPEN_ENDED_INCIDENTS = [
    "Ransomware",
    "Phishing / Business Email Compromise",
    "Unauthorized access / Privilege misuse",
    "Data breach / Exfiltration",
    "Surveillance technology use / repurposing",
    "AI-enabled incident (model drift / adversarial)",
    "DDoS / service outage",
    "Third-party / vendor compromise",
    "OT/ICS disruption (water / utility)",
    "Misconfiguration exposure (cloud / on-prem)"
]

# Map label -> (token for NIST_KB, default description template)
OPEN_ENDED_MAP = {
    "Ransomware": ("ransomware",
        "City systems show widespread file encryption and ransom notes. Multiple departments are locked out; backup status unclear. Critical services impacted include permitting and email. Attackers demand payment in crypto."),
    "Phishing / Business Email Compromise": ("phishing",
        "Multiple staff received credential-harvesting emails. One finance mailbox shows suspicious forwarding rules. Risk of invoice fraud and lateral movement."),
    "Unauthorized access / Privilege misuse": ("unauthorized access",
        "Unusual privileged actions detected on domain controllers. Possible insider misuse or compromised admin account affecting user provisioning and group policy."),
    "Data breach / Exfiltration": ("data breach",
        "Indicators suggest data exfiltration from a file server containing PII of residents and employees. Public disclosure obligations likely; exact scope unknown."),
    "Surveillance technology use / repurposing": ("surveillance",
        "Smart streetlight/video sensors initially deployed for traffic/environmental data are requested for expanded police use. Community consent and policy basis are unclear."),
    "AI-enabled incident (model drift / adversarial)": ("ai-enabled",
        "AI model supporting a safety-critical workflow is behaving unpredictably, potentially due to adversarial inputs or model drift. Debate over disabling vs. live retraining."),
    "DDoS / service outage": ("outage",
        "Public-facing portals (permits, utility bills) are intermittently unavailable due to suspected DDoS. Pressure to geo-block and rate-limit; collateral impact likely."),
    "Third-party / vendor compromise": ("ransomware",
        "Key SaaS vendor suffered a breach affecting the city tenant. Limited visibility into vendor logs; questions about data handling, notifications, and contingency."),
    "OT/ICS disruption (water / utility)": ("ai-enabled",
        "Abnormal setpoints and telemetry in water treatment. Potential ICS compromise. Decisions needed on manual override and safe-mode operations."),
    "Misconfiguration exposure (cloud / on-prem)": ("unauthorized access",
        "Publicly exposed storage bucket and weak access controls may have revealed documents. Need rapid remediation, scoping, and notification assessment.")
}

# ---------- Principlist ----------
PRINCIPLES = ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"]

# === Data-driven highlighter for principles, tensions, and prehighlight ===
_HINTS = {
    r"\b(ransom|ransomware|extort)\b":        ["Justice", "Non-maleficence", "Beneficence", "Explicability"],
    r"\b(surveillance|streetlight|CCTV)\b":   ["Autonomy", "Justice", "Explicability", "Non-maleficence"],
    r"\b(data breach|breach|exfiltration)\b": ["Non-maleficence", "Explicability", "Justice"],
    r"\b(unauthorized access|privilege|insider)\b": ["Non-maleficence", "Explicability", "Justice"],
    r"\b(water|utility|ICS|SCADA)\b":         ["Beneficence", "Non-maleficence", "Justice", "Explicability"],
    r"\b(health|hospital|EMS)\b":             ["Beneficence", "Non-maleficence", "Justice"],
    r"\b(ai|algorithm|model|ml|training)\b":  ["Autonomy", "Explicability", "Non-maleficence", "Beneficence"],
    r"\b(email|phish|credential)\b":          ["Autonomy", "Explicability"],
    r"\b(outage|downtime|service disruption)\b":["Non-maleficence", "Beneficence", "Explicability"],
    r"\b(protest|demonstration|civil unrest)\b":["Justice", "Autonomy", "Explicability"],
    r"\b(equity|bias|disparate|fairness)\b":  ["Justice", "Explicability"],
}

_RULES = [
    (r"\bransom|ransomware\b",
     "Paying ransom for rapid restoration vs. refusing payment to avoid precedent and long-term harm",
     ["Justice", "Non-maleficence", "Beneficence", "Explicability"],
     [("Respond (RS)", "Justice"), ("Protect (PR)", "Non-maleficence"), ("Recover (RC)", "Beneficence"), ("Govern (GV)", "Explicability")]),

    (r"\bsurveillance|streetlight|CCTV\b",
     "Secondary policing use of data vs. original civic purpose and privacy safeguards",
     ["Autonomy", "Justice", "Explicability", "Non-maleficence"],
     [("Govern (GV)", "Autonomy"), ("Govern (GV)", "Justice"), ("Govern (GV)", "Explicability"), ("Protect (PR)", "Non-maleficence"), ("Identify (ID)", "Autonomy")]),

    (r"\bdata breach|exfiltration\b",
     "Early public transparency vs. operational confidentiality to limit further harm",
     ["Explicability", "Non-maleficence", "Justice"],
     [("Respond (RS)", "Explicability"), ("Detect (DE)", "Non-maleficence"), ("Identify (ID)", "Justice")]),

    (r"\bai|algorithm|model|ml|training\b",
     "Automated control for speed vs. human oversight and explainability",
     ["Beneficence", "Autonomy", "Explicability", "Non-maleficence"],
     [("Respond (RS)", "Beneficence"), ("Respond (RS)", "Explicability"), ("Detect (DE)", "Non-maleficence"), ("Govern (GV)", "Explicability")]),

    (r"\bwater|ICS|SCADA|utility\b",
     "Stabilizing essential services rapidly vs. validating safety before full return",
     ["Beneficence", "Non-maleficence", "Justice", "Explicability"],
     [("Identify (ID)", "Beneficence"), ("Recover (RC)", "Justice"), ("Detect (DE)", "Non-maleficence"), ("Govern (GV)", "Explicability")]),
]

def _match_any(pattern: str, text: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE) is not None

def infer_principles(description: str) -> list:
    found = []
    for pat, plist in _HINTS.items():
        if _match_any(pat, description):
            for p in plist:
                if p not in found:
                    found.append(p)
    return found or PRINCIPLES[:]  # fall back to all five

def infer_tradeoffs_and_prehighlight(description: str):
    tensions = []
    pre = set()
    for pat, label, tags, cells in _RULES:
        if _match_any(pat, description):
            tensions.append((label, tags))
            for cell in cells:
                pre.add(cell)
    return tensions, pre

def auto_highlight_from_text(text: str):
    ps = infer_principles(text)
    tensions, pre = infer_tradeoffs_and_prehighlight(text)
    return ps, tensions, pre

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

# ---------- NIST CSF 2.0 action examples ----------
NIST_ACTIONS = {
    "Govern (GV)": [
        "Affirm decision rights, RACI, and escalation paths",
        "Activate risk governance: convene cross-dept incident steering group",
        "Ensure policies for privacy, surveillance use, and AI are applied only with due process",
        "Require procurement/vendor transparency (SBOMs, data handling, model cards)",
        "Coordinate with oversight bodies and document rationale",
        "Mandate equity impact check and mitigations",
    ],
    "Identify (ID)": [
        "Confirm critical assets and services",
        "Establish incident objectives and scope",
        "Map stakeholders and equity impacts",
        "Inventory affected assets, data, and dependencies"
    ],
    "Protect (PR)": [
        "Harden access (MFA, least privilege, segmentation)",
        "Freeze risky changes; ensure backups are protected/offline",
        "Apply emergency configuration baselines",
        "Safeguard sensitive data"
    ],
    "Detect (DE)": [
        "Correlate alerts; verify indicators of compromise",
        "Expand monitoring to adjacent systems",
        "Preserve logs and evidence",
        "Hunt for lateral movement and persistence"
    ],
    "Respond (RS)": [
        "Contain affected hosts/segments; coordinate with counsel/LE",
        "Activate comms plan; publish clear updates",
        "Decide on takedown/disablement with proportionality",
        "Coordinate with vendors and partners"
    ],
    "Recover (RC)": [
        "Restore by criticality with integrity checks",
        "Conduct post-incident review and address root causes",
        "Update playbooks; brief council/public with lessons learned",
        "Track residual risk and follow-up actions"
    ],
}

# ---------- Scenario summaries ----------
scenario_summaries = {
    "Baltimore Ransomware Attack": (
        "In 2019, Baltimore’s municipal systems were crippled by a ransomware attack that locked staff out of essential services. "
        "Cybersecurity practitioners had to guide the city’s response under pressure, weighing whether to recommend paying the ransom or pursuing recovery, each carrying severe consequences."
    ),
    "San Diego Smart Streetlights and Surveillance": (
        "San Diego deployed smart streetlights to collect traffic and environmental data, but the system was later repurposed for police surveillance without public consent. "
        "Cybersecurity practitioners faced ethical trade-offs around enabling law enforcement access versus safeguarding transparency, privacy, and community trust."
    ),
    "Riverton AI-Enabled Threat": (
        "In the fictional city of Riverton, adversarial signals disrupted an AI-based monitoring system at a water treatment facility, threatening public safety. "
        "Cybersecurity practitioners had to decide whether to disable the AI system or attempt risky live retraining, balancing technical reliability, continuity of service, and public trust."
    )
}

# ---------- Sidebar ----------
st.sidebar.header("Options")
mode = st.sidebar.radio("Mode", ["Thesis scenarios", "Open-ended"])

# ---------- Header ----------
st.markdown(
    """
    <div style='text-align: center;'>
        <h1>🛡️ Municipal Ethical Cyber Decision-Support Prototype</h1>
        <h4 style='color:#4C8BF5;'>Because what's secure isn't always what's right.</h4>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("About this prototype"):
    st.markdown(
        """
- **Purpose:** Support municipal cybersecurity practitioners in navigating complex ethical dilemmas. This tool guides users through high-stakes decisions in real time—aligning actions with technical standards, clarifying value conflicts, and documenting justifiable outcomes under institutional and governance constraints.  
- **Backbone:** This prototype draws on the NIST Cybersecurity Framework, guiding users through six core functions: **Govern, Identify, Protect, Detect, Respond, Recover**. These are integrated with Principlist ethical values—**Beneficence, Non-maleficence, Autonomy, Justice, Explicability**—to help users weigh trade-offs and make morally defensible decisions.  
- **Context:** Designed specifically for municipal use, the prototype accounts for real-world constraints like limited budgets, fragmented authority, and vendor opacity. It supports ethical decision-making within these practical and political realities. 
        """
    )

st.divider()

# ---------- 1) Scenario overview ----------
scenario = st.selectbox("Choose a Municipal Cybersecurity Scenario", options=list(scenario_summaries.keys()))
st.markdown("### 1) Scenario Overview")
st.markdown(f"**Scenario Overview:** {scenario_summaries[scenario]}")

incident_type = scenario
description = scenario_summaries[scenario]

# --- Open-ended mode: dropdown + prefilled, editable description ---
if mode == "Open-ended":
    st.markdown("#### Choose an incident archetype")
    archetype = st.selectbox(
        "Common municipal cybersecurity scenarios",
        options=OPEN_ENDED_INCIDENTS,
        key=f"{mode}_archetype"
    )
    token, template = OPEN_ENDED_MAP.get(archetype, ("ransomware", ""))
    description = st.text_area(
        "Describe the incident (you can edit this template)",
        value=template,
        key=f"{mode}_desc",
        height=140,
        help="This description drives the suggested NIST functions, principles, trade-offs, and matrix pre-highlights."
    )
    incident_type = archetype  # label used for display

# Use data-driven highlighter (works for both modes)
auto_principles, tensions_auto, prehighlight_auto = auto_highlight_from_text(description)

# NIST suggestions (use token if in Open-ended mode for stronger keyword match)
def suggest_nist(incident_type: str, description: str):
    it = incident_type.lower()
    seed = []
    for k, v in NIST_KB.items():
        if k in it or k in description.lower():
            seed.extend(v)
    if not seed:
        seed = NIST_FUNCTIONS[:]
    seen, ordered = set(), []
    for x in seed:
        if x not in seen:
            ordered.append(x); seen.add(x)
    return ordered

nist_seed_label = OPEN_ENDED_MAP.get(st.session_state.get(f"{mode}_archetype"), (None, ""))[0] if mode == "Open-ended" else None
suggested_nist = suggest_nist(nist_seed_label if nist_seed_label else incident_type, description)

# Scenario “tags”
st.markdown("<div class='badges'>" + "".join([f"<span class='badge nist'>NIST: {f}</span>" for f in suggested_nist]) + "</div>", unsafe_allow_html=True)
st.markdown("<div class='badges'>" + "".join([f"<span class='badge principle'>{p}</span>" for p in auto_principles]) + "</div>", unsafe_allow_html=True)

st.divider()

# ---------- 2) Technical Evaluation (NIST CSF) ----------
st.markdown("### 2) Technical Evaluation (NIST CSF)")
with st.expander("About the NIST CSF"):
    st.markdown("""
The **NIST Cybersecurity Framework (CSF) 2.0** is a risk-based framework created by the 
National Institute of Standards and Technology to help organizations manage and reduce 
cybersecurity risks. It is organized into six core functions:

- **Govern (GV):** Establish and communicate organizational context, roles, policies, and oversight for managing cybersecurity risk.  
- **Identify (ID):** Develop an organizational understanding of systems, people, assets, data, and capabilities to manage risk.  
- **Protect (PR):** Develop and implement safeguards to ensure delivery of critical services.  
- **Detect (DE):** Develop and implement activities to identify the occurrence of a cybersecurity event.  
- **Respond (RS):** Take appropriate action regarding a detected cybersecurity incident.  
- **Recover (RC):** Maintain plans for resilience and restore capabilities impaired by incidents.  

In this prototype, the CSF provides the **technical backbone**, and the Principlist Framework provides the **ethical backbone**.
    """)

def scenario_csfs_explanations(incident_text: str) -> dict:
    t = incident_text.lower()
    notes = {
        "Govern (GV)": "Clarify decision rights, escalation, and documentation duties for this scenario.",
        "Identify (ID)": "Confirm critical services, impacted assets, and risk to residents for this scenario.",
        "Protect (PR)": "Harden access, backups, and sensitive data paths most relevant here.",
        "Detect (DE)": "Tighten monitoring for IOCs and adjacent systems implicated in this scenario.",
        "Respond (RS)": "Contain, coordinate comms/counsel, and execute proportional response steps.",
        "Recover (RC)": "Restore by criticality, verify integrity, and capture lessons learned."
    }
    if "ransom" in t:
        notes["Protect (PR)"] = "Ensure offline/immutable backups; least-privilege clean-up to prevent re-encryption."
        notes["Respond (RS)"] = "Isolate infected hosts, evaluate ransom stance, coordinate comms and legal."
        notes["Recover (RC)"] = "Prioritize restoration of city services; validate from clean backups."
    if "surveillance" in t or "streetlight" in t:
        notes["Govern (GV)"] = "Ensure policy/oversight and due process around repurposing technology."
        notes["Identify (ID)"] = "Map data types, retention, and groups most affected by repurposing."
        notes["Protect (PR)"] = "Enforce access controls and data minimization for sensitive footage/metadata."
        notes["Respond (RS)"] = "Adjust usage, pause feeds if needed, and publish transparent updates."
    if "ai" in t or "water" in t or "ics" in t or "scada" in t:
        notes["Identify (ID)"] = "Assess critical dependencies and AI decision points in the water/ICS system."
        notes["Detect (DE)"] = "Watch for model drift/adversarial behavior; expand telemetry at interfaces."
        notes["Respond (RS)"] = "Decide on disable vs. retrain; ensure safety-first rollback options."
        notes["Recover (RC)"] = "Validate safe operations before full return; document model/controls changes."
    return notes

scenario_tips = scenario_csfs_explanations(description)

st.markdown("#### Technical considerations in this scenario")
st.caption("What the NIST CSF suggests focusing on for this case.")
if mode == "Thesis scenarios":
    selected_nist = suggested_nist[:]
    items = []
    for fn in NIST_FUNCTIONS:
        mark = " ✓" if fn in suggested_nist else ""
        tip = scenario_tips.get(fn, "—")
        items.append(f"<li><b>{fn}</b>{mark} — {tip}</li>")
    st.markdown(f"<div class='listbox'><ul class='tight-list'>{''.join(items)}</ul></div>", unsafe_allow_html=True)
else:
    selected_nist = []
    st.caption("Quick toggles")
    t1, t2 = st.columns(2)
    with t1:
        if st.button("Select all NIST"):
            for fn in NIST_FUNCTIONS:
                st.session_state[f"{mode}_{scenario}_fn_{fn}"] = True
    with t2:
        if st.button("Clear all NIST"):
            for fn in NIST_FUNCTIONS:
                st.session_state[f"{mode}_{scenario}_fn_{fn}"] = False

    cols_fn = st.columns(3)
    for i, fn in enumerate(NIST_FUNCTIONS):
        with cols_fn[i % 3]:
            ck_key = f"{mode}_{scenario}_fn_{fn}"
            checked = st.checkbox(fn, value=st.session_state.get(ck_key, fn in suggested_nist), key=ck_key)
            if checked:
                selected_nist.append(fn)
            st.caption(scenario_tips.get(fn, "—"))

st.divider()

# ---------- 3) Ethical Evaluation (Principlist) ----------
st.markdown("### 3) Ethical Evaluation (Principlist)")
with st.expander("About the Principlist Framework"):
    st.markdown("""
The **Principlist Framework for Cybersecurity Ethics** balances multiple values when making decisions under pressure:

- **Beneficence:** Promote public well-being and the delivery of essential services.  
- **Non-maleficence:** Avoid foreseeable harm from actions taken or omitted (e.g., over-collection, rash shutdowns).  
- **Autonomy:** Respect legal rights, due process, and meaningful choice for affected people.  
- **Justice:** Distribute burdens and benefits fairly; avoid disproportionate impact on specific communities.  
- **Explicability:** Ensure transparency, accountability, and the ability to explain decisions and system behavior.  
    """)

if mode == "Thesis scenarios":
    selected_principles = auto_principles[:]
else:
    selected_principles = st.multiselect("Select relevant ethical principles (optional)", PRINCIPLES, default=auto_principles, key=f"{mode}_{scenario}_principles")

st.markdown("#### Ethical tensions in this scenario")
st.caption("Key value trade-offs in this case framed in Principlist terms.")
tensions = tensions_auto  # from data-driven rules above
if tensions:
    items = []
    for label, tags in tensions:
        tag_str = ", ".join(tags) if tags else "—"
        items.append(f"<li>{label}<div class='sub'>Principlist lens: <i>{tag_str}</i></div></li>")
    st.markdown(f"<div class='listbox'><ul class='tight-list'>{''.join(items)}</ul></div>", unsafe_allow_html=True)
else:
    st.info("No predefined ethical tensions for this scenario.")

st.divider()

# ---------- 4) Decision-Support Matrix ----------
st.markdown("### 4) Decision-Support Matrix")
with st.expander("What this matrix does"):
    st.markdown("""
The matrix helps practitioners **consider technical and ethical dimensions together**:  
- **Rows = NIST CSF functions** — technical steps for the incident.  
- **Columns = Principlist principles** — values guiding how those steps are carried out.  
- **Cells = integration points** — reminders to ensure each technical action is considered in light of relevant ethical principles.  
    """)

# Quick actions for matrix
qa1, qa2, qa3 = st.columns(3)
with qa1:
    if st.button("Apply scenario highlights"):
        for fn, p in prehighlight_auto:
            st.session_state[f"{mode}_{scenario}_mx_{fn}_{p}"] = True
with qa2:
    if st.button("Clear matrix"):
        for fn in NIST_FUNCTIONS:
            for p in PRINCIPLES:
                st.session_state[f"{mode}_{scenario}_mx_{fn}_{p}"] = False
with qa3:
    if st.button("Select full grid"):
        for fn in NIST_FUNCTIONS:
            for p in PRINCIPLES:
                st.session_state[f"{mode}_{scenario}_mx_{fn}_{p}"] = True

# Render matrix (keys namespaced by mode+scenario)
cols = st.columns([1.1] + [1]*len(PRINCIPLES))
with cols[0]:
    st.markdown("**Function \\ Principle**")
for i, p in enumerate(PRINCIPLES, start=1):
    with cols[i]:
        st.markdown(f"**{p}**")

matrix_state = {}
for fn in NIST_FUNCTIONS:
    row_cols = st.columns([1.1] + [1]*len(PRINCIPLES))
    with row_cols[0]:
        st.markdown(f"**{fn}**")
    for j, p in enumerate(PRINCIPLES, start=1):
        base_key = f"{mode}_{scenario}_mx_{fn}_{p}"
        default_marked = ((fn, p) in prehighlight_auto) if mode == "Thesis scenarios" else False
        with row_cols[j]:
            mark = st.checkbox(" ", value=st.session_state.get(base_key, default_marked), key=base_key, label_visibility="collapsed")
            matrix_state[(fn, p)] = 1 if mark else 0

st.markdown("##### Matrix summary")
fn_totals = {fn: sum(matrix_state[(fn, p)] for p in PRINCIPLES) for fn in NIST_FUNCTIONS}
pr_totals = {p: sum(matrix_state[(fn, p)] for fn in NIST_FUNCTIONS) for p in PRINCIPLES}

colA, colB = st.columns(2)
with colA:
    st.markdown("**Totals by NIST function**")
    for fn in NIST_FUNCTIONS:
        pct = min(int((fn_totals[fn] / len(PRINCIPLES)) * 100), 100)
        st.progress(pct, text=f"{fn}: {fn_totals[fn]}")
with colB:
    st.markdown("**Totals by Ethical principle**")
    for p in PRINCIPLES:
        pct = min(int((pr_totals[p] / len(NIST_FUNCTIONS)) * 100), 100)
        st.progress(pct, text=f"{p}: {pr_totals[p]}")

st.session_state["nist_principle_matrix"] = matrix_state
st.session_state["nist_totals_by_function"] = fn_totals
st.session_state["principle_totals"] = pr_totals

st.divider()

# ---------- 5) Institutional & Governance Constraints ----------
st.markdown("### 5) Institutional & Governance Constraints")
constraints = st.multiselect("Select constraints relevant to this scenario", GOV_CONSTRAINTS, default=[], key=f"{mode}_{scenario}_constraints")

st.divider()

# ---------- 6) Documentation & Rationale ----------
st.markdown("### 6) Documentation & Rationale")
# Intentionally left blank per your direction.

# ---------- Footer ----------
st.markdown("---")
st.caption("Prototype created for thesis demonstration purposes – not for operational use.")
