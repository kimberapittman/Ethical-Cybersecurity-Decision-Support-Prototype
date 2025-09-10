import streamlit as st
from datetime import datetime
import pandas as pd

# ---------- Page config ----------
st.set_page_config(page_title="Municipal Ethical Cyber Decision-Support", layout="wide", initial_sidebar_state="expanded")

# ---------- Minimal styling + Dark Mode hook ----------
st.markdown("""
<style>
.listbox{background:#f9fbff;border-left:4px solid #4C8BF5;padding:10px 14px;border-radius:8px;margin:6px 0 14px;}
.section-note{color:#6b7280;font-size:0.9rem;margin:-4px 0 10px 0;}
.tight-list{margin:0.25rem 0 0 1.15rem;padding:0;}
.tight-list li{margin:6px 0;}
.sub{color:#6b7280;font-size:0.95rem;}
/* Stepper */
.stepper{display:flex;gap:12px;align-items:center;margin:8px 0 18px;}
.step{display:flex;align-items:center;gap:8px;}
.step .dot{width:10px;height:10px;border-radius:999px;background:#cbd5e1;border:2px solid #94a3b8;}
.step.done .dot{background:#4C8BF5;border-color:#3B82F6;}
.step .label{font-size:0.92rem;color:#374151;}
/* Dark mode (toggle-able) */
.dark body, .dark [data-testid="stAppViewContainer"]{ background:#0b1020 !important; color:#e5e7eb !important; }
.dark .listbox{ background:#0f172a; border-left-color:#60a5fa; }
.dark .sub, .dark .section-note, .dark .label{ color:#9ca3af !important; }
.dark .stProgress > div > div{ background:#172554 !important; }
.tooltip{cursor:help;border-bottom:1px dotted #9ca3af;}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar (UI controls) ----------
st.sidebar.header("Options")
mode = st.sidebar.radio("Mode", ["Thesis scenarios", "Open-ended"])
st.sidebar.markdown("---")
ui_dark = st.sidebar.toggle("Dark mode", value=False)
ui_guided = st.sidebar.toggle("Guided mode (show steps)", value=True)
ui_heatmap = st.sidebar.toggle("Heatmap view for matrix", value=True)
ui_celebrate = st.sidebar.toggle("Celebrate on complete 🎉", value=False)

# Apply dark mode CSS class
if ui_dark:
    st.markdown("<script>document.documentElement.classList.add('dark')</script>", unsafe_allow_html=True)
else:
    st.markdown("<script>document.documentElement.classList.remove('dark')</script>", unsafe_allow_html=True)

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
    "ai": ["Autonomy", "Explicability", "Non-maleficence"]
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
    "Ransomware disrupting city services": (
        "Malware encrypts key systems (e.g., permitting, payroll, 311). Teams must balance rapid recovery, ransom decisions, and public communication."
    ),
    "Business email compromise (finance)": (
        "Spoofed or compromised mailbox targets treasury/AP workflows, risking fraudulent payments and vendor trust."
    ),
    "Data breach of resident information": (
        "PII from utility billing/library systems is exfiltrated. Decisions on disclosure, notification, and containment carry legal and trust implications."
    ),
    "OT/SCADA disruption (water/wastewater)": (
        "Operational systems show anomalous behavior. Teams must prioritize safety and service continuity while investigating root cause."
    ),
    "Vendor/SaaS compromise": (
        "Third-party platform used by the city is breached. Limited visibility and contractual gaps complicate response."
    ),
    "Smart-city surveillance overreach": (
        "Sensors/cameras are repurposed for law enforcement without adequate oversight, raising privacy and equity issues."
    ),
    "Phishing campaigns targeting staff": (
        "Wide staff phishing wave degrades trust and threatens credential/endpoint compromise."
    ),
    "DDoS on public-facing portals": (
        "Web services (tax payment, council streaming) go offline during civic events. Pressure to restore availability quickly."
    ),
    "Insider misuse of access": (
        "An employee abuses legitimate access for personal or political purposes; audit and accountability are central."
    ),
    "AI-enabled decision/triage risks": (
        "Automated systems used for resource allocation or fraud detection show bias or opaque behavior under attack."
    ),
}

PRINCIPLES = ["Beneficence", "Non-maleficence", "Autonomy", "Justice", "Explicability"]

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

def suggest_principles(description: str):
    hits = []
    text = description.lower()
    for k, plist in ETHICAL_HINTS.items():
        if k in text:
            hits.extend(plist)
    if not hits:
        hits = PRINCIPLES[:]
    seen, ordered = set(), []
    for p in hits:
        if p not in seen:
            ordered.append(p); seen.add(p)
    return ordered

def score_tension(selected_principles, selected_nist, constraints, stakeholders, values):
    # Retained function (unused now) to preserve your code structure
    base = 10
    base += 5 * len(selected_principles)
    base += 3 * len(selected_nist)
    base += 6 * len(constraints)
    base += 3 * len(stakeholders)
    base += 4 * len(values)
    return min(base, 100)

# ---------- ETHICAL TENSIONS mapped to Principlist ----------
ETHICAL_TENSIONS_BY_SCENARIO = {
    "Ransomware disrupting city services": [
        ("Paying ransom vs. refusing payment (speed vs. long-term harm/precedent)", ["Justice", "Non-maleficence", "Beneficence"]),
        ("Public transparency vs. operational confidentiality during recovery", ["Explicability", "Non-maleficence"]),
        ("Restoring critical services first vs. equal treatment", ["Justice", "Beneficence"]),
    ],
    "Business email compromise (finance)": [
        ("Immediate fund freezes vs. continuity of vendor payments", ["Beneficence", "Justice"]),
        ("Disclosing suspected fraud vs. reputational damage", ["Explicability", "Non-maleficence"]),
    ],
    "Data breach of resident information": [
        ("Rapid disclosure vs. investigative integrity", ["Explicability", "Non-maleficence"]),
        ("Protecting vulnerable populations vs. blanket notifications", ["Justice", "Beneficence"]),
    ],
    "OT/SCADA disruption (water/wastewater)": [
        ("Automated control vs. human oversight and explainability", ["Beneficence", "Autonomy", "Explicability"]),
        ("Immediate shutoff vs. risk of service impact", ["Non-maleficence", "Beneficence"]),
    ],
    "Vendor/SaaS compromise": [
        ("Contractual NDAs vs. public accountability", ["Explicability", "Justice"]),
        ("Rapid migration vs. operational stability", ["Non-maleficence", "Beneficence"]),
    ],
    "Smart-city surveillance overreach": [
        ("Secondary use for policing vs. original civic purpose", ["Autonomy", "Justice", "Explicability"]),
        ("Privacy protections vs. public safety claims", ["Non-maleficence", "Autonomy", "Justice"]),
    ],
    "Phishing campaigns targeting staff": [
        ("Strict sanctions vs. just-culture learning", ["Justice", "Beneficence"]),
        ("Mandatory training vs. accessibility and autonomy", ["Autonomy", "Explicability"]),
    ],
    "DDoS on public-facing portals": [
        ("Aggressive filtering vs. risk of blocking legitimate users", ["Justice", "Non-maleficence"]),
        ("Public updates vs. attacker signaling", ["Explicability", "Non-maleficence"]),
    ],
    "Insider misuse of access": [
        ("Rapid disablement vs. due process protections", ["Autonomy", "Justice"]),
        ("Public disclosure vs. staff privacy", ["Explicability", "Non-maleficence"]),
    ],
    "AI-enabled decision/triage risks": [
        ("Performance under pressure vs. bias/opacity", ["Beneficence", "Justice", "Explicability"]),
        ("Vendor secrecy vs. accountability", ["Explicability", "Justice"]),
    ],
}

# ---------- Intro ----------
st.markdown(
    """
    <div style='text-align: center;'>
        <h1>🛡️ Municipal Ethical Cyber Decision-Support Prototype</h1>
        <h4 style='color:#4C8BF5;'>Because what's secure isn't always what's right.</h4>
    </div>
    """,
    unsafe_allow_html=True
)

# Guided stepper (visual only)
if ui_guided:
    steps = [
        ("Scenario", True),
        ("Technical", True),
        ("Ethical", True),
        ("Matrix", True),
        ("Constraints", True),
        ("Rationale", True),
    ]
    st.markdown("<div class='stepper'>" + "".join(
        [f"<div class='step {'done' if done else ''}'><div class='dot'></div><div class='label'>{name}</div></div>"
         for name, done in steps]) + "</div>", unsafe_allow_html=True)

with st.expander("About this prototype"):
    st.markdown(
        """
- **Purpose:** Support municipal cybersecurity practitioners in navigating complex ethical dilemmas. This tool is designed to guide users through high-stakes decisions in real time - aligning actions with technical standards, clarifying value conflicts, and documenting justifiable outcomes under institutional and governance constraints.  
- **Backbone:** This prototype draws on the NIST Cybersecurity Framework, guiding users through six core functions: Govern, Identity, Protect, Detect, Respond, and Recover. These are integrated with Principlist ethical values: Beneficence, Non-maleficence, Autonomy, Justice, and Explicability - to help users weigh trade-offs and make morally defensible decisions.  
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
pd_defaults = dict(description="", stakeholders=[], values=[], constraints=[])

# Sticky summary in sidebar (live)
with st.sidebar:
    st.markdown("### Live Summary")
    st.caption(f"**Scenario**: {scenario}")
    # placeholders; filled later after selections exist
    sel_fn_ph = st.empty()
    sel_pr_ph = st.empty()
    sel_c_ph = st.empty()

st.divider()

# ---------- 2) Technical Evaluation (NIST CSF) ----------
st.markdown("### 2) Technical Evaluation (NIST CSF)")
with st.expander("About the NIST CSF"):
    st.markdown("""
The **NIST Cybersecurity Framework (CSF) 2.0** is a risk-based framework created by the 
National Institute of Standards and Technology to help organizations manage and reduce 
cybersecurity risks. It is organized into six core functions, which together provide a 
comprehensive approach to managing cyber risk:

- **Govern (GV):** Establish and communicate organizational context, roles, policies, and oversight for managing cybersecurity risk.  
- **Identify (ID):** Develop an organizational understanding of systems, people, assets, data, and capabilities to manage risk.  
- **Protect (PR):** Develop and implement safeguards to ensure delivery of critical services.  
- **Detect (DE):** Develop and implement activities to identify the occurrence of a cybersecurity event.  
- **Respond (RS):** Take appropriate action regarding a detected cybersecurity incident.  
- **Recover (RC):** Maintain plans for resilience and restore capabilities impaired by incidents.  

In this prototype, the CSF provides the **technical backbone**.  
Relevant CSF functions are highlighted for each scenario, and notes explain how they 
apply in that specific situation—ensuring that ethical reasoning (via the Principlist 
Framework) is grounded in recognized technical standards.
    """)

suggested_nist = suggest_nist(incident_type, description)

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
    if "ai" in t or "water" in t:
        notes["Identify (ID)"] = "Assess critical dependencies and AI decision points in the water system."
        notes["Detect (DE)"] = "Watch for model drift/adversarial behavior; expand telemetry at interfaces."
        notes["Respond (RS)"] = "Decide on disable vs. retrain; ensure safety-first rollback options."
        notes["Recover (RC)"] = "Validate safe operations before full return; document model/controls changes."
    return notes

scenario_tips = scenario_csfs_explanations(description)

# ---- Bullet list display with checkmarks for Thesis scenarios; checkboxes for Open-ended ----
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
    cols_fn = st.columns(3)
    for i, fn in enumerate(NIST_FUNCTIONS):
        with cols_fn[i % 3]:
            checked = st.checkbox(fn, value=(fn in suggested_nist), key=f"fn_{fn}")
            if checked:
                selected_nist.append(fn)
            st.caption(scenario_tips.get(fn, "—"))

st.divider()

# ---------- 3) Ethical Evaluation (Principlist) ----------
st.markdown("### 3) Ethical Evaluation (Principlist)")
with st.expander("About the Principlist Framework"):
    st.markdown("""
The **Principlist Framework for Cybersecurity Ethics** is a practical approach to ethical 
reasoning that balances multiple values when making decisions under pressure. It is 
organized into five core principles, which together provide a comprehensive approach 
to identifying, weighing, and justifying ethical trade-offs:

- **Beneficence:** Promote public well-being and the delivery of essential services.  
- **Non-maleficence:** Avoid foreseeable harm from actions taken or omitted (e.g., over-collection, rash shutdowns).  
- **Autonomy:** Respect legal rights, due process, and meaningful choice for affected people.  
- **Justice:** Distribute burdens and benefits fairly; avoid disproportionate impact on specific communities.  
- **Explicability:** Ensure transparency, accountability, and the ability to explain decisions and system behavior.  

In this prototype, the Principlist Framework provides the **ethical backbone**.  
Relevant principles are highlighted for each scenario, making value tensions explicit 
so that technical standards (via the NIST CSF) are always considered in light of 
ethical reasoning.
    """)

auto_principles = suggest_principles(description)
if mode == "Thesis scenarios":
    selected_principles = auto_principles[:]
else:
    selected_principles = st.multiselect("Select relevant ethical principles (optional)", PRINCIPLES, default=auto_principles)

# ---------- Ethical tensions in this scenario ----------
st.markdown("#### Ethical tensions in this scenario")
st.caption("Key value trade-offs in this case framed in Principlist terms.")
tensions = ETHICAL_TENSIONS_BY_SCENARIO.get(scenario, [])
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
The matrix is designed to help practitioners **consider technical and ethical dimensions together** when making high-stakes cybersecurity decisions.  

- **Rows = NIST CSF functions** — the technical steps needed to manage the incident.  
- **Columns = Principlist ethical principles** — the values that should guide how those steps are carried out.  
- **Cells = points of integration** — reminders to ensure that each technical action is considered in light of relevant ethical principles.  

This approach does not assume conflict between technical and ethical concerns. Instead, it ensures **completeness of reasoning**, so that municipal practitioners act in ways that are both technically sound and ethically defensible under real-world constraints.  
    """)

# Tooltips for headers (hover)
NIST_HEADER = "NIST CSF functions structure technical work."
PRINCIPLE_TIPS = {
    "Beneficence": "Promote public well-being and service continuity.",
    "Non-maleficence": "Avoid foreseeable harm from actions/inaction.",
    "Autonomy": "Respect rights, due process, informed choice.",
    "Justice": "Fair distribution of burdens/benefits.",
    "Explicability": "Transparency, accountability, explainability."
}

st.write("")
cols = st.columns([1.1] + [1]*len(PRINCIPLES))
with cols[0]:
    st.markdown(f"**<span class='tooltip' title='{NIST_HEADER}'>Function \\ Principle</span>**", unsafe_allow_html=True)
for i, p in enumerate(PRINCIPLES, start=1):
    with cols[i]:
        tip = PRINCIPLE_TIPS.get(p, "")
        st.markdown(f"**<span class='tooltip' title='{tip}'>{p}</span>**", unsafe_allow_html=True)

# Pre-highlights (kept from your structure; used only in Thesis scenarios)
PREHIGHLIGHT = {
    "Ransomware disrupting city services": [
        ("Respond (RS)", "Justice"),
        ("Protect (PR)", "Non-maleficence"),
        ("Recover (RC)", "Beneficence"),
        ("Govern (GV)", "Explicability"),
        ("Identify (ID)", "Justice"),
    ],
    "Business email compromise (finance)": [
        ("Identify (ID)", "Explicability"),
        ("Protect (PR)", "Non-maleficence"),
        ("Respond (RS)", "Justice"),
    ],
    "Data breach of resident information": [
        ("Identify (ID)", "Justice"),
        ("Respond (RS)", "Explicability"),
        ("Recover (RC)", "Beneficence"),
    ],
    "OT/SCADA disruption (water/wastewater)": [
        ("Detect (DE)", "Non-maleficence"),
        ("Respond (RS)", "Beneficence"),
        ("Identify (ID)", "Beneficence"),
        ("Govern (GV)", "Explicability"),
    ],
    "Vendor/SaaS compromise": [
        ("Govern (GV)", "Explicability"),
        ("Respond (RS)", "Justice"),
        ("Recover (RC)", "Beneficence"),
    ],
    "Smart-city surveillance overreach": [
        ("Govern (GV)", "Autonomy"),
        ("Govern (GV)", "Justice"),
        ("Govern (GV)", "Explicability"),
        ("Identify (ID)", "Autonomy"),
        ("Protect (PR)", "Non-maleficence"),
        ("Respond (RS)", "Justice"),
    ],
    "Phishing campaigns targeting staff": [
        ("Protect (PR)", "Non-maleficence"),
        ("Detect (DE)", "Beneficence"),
        ("Respond (RS)", "Explicability"),
    ],
    "DDoS on public-facing portals": [
        ("Protect (PR)", "Justice"),
        ("Respond (RS)", "Explicability"),
        ("Recover (RC)", "Beneficence"),
    ],
    "Insider misuse of access": [
        ("Identify (ID)", "Justice"),
        ("Respond (RS)", "Autonomy"),
        ("Govern (GV)", "Explicability"),
    ],
    "AI-enabled decision/triage risks": [
        ("Detect (DE)", "Non-maleficence"),
        ("Respond (RS)", "Explicability"),
        ("Recover (RC)", "Justice"),
        ("Identify (ID)", "Beneficence"),
    ],
}

matrix_state = {}
pre = set(PREHIGHLIGHT.get(scenario, []))
for fn in NIST_FUNCTIONS:
    row_cols = st.columns([1.1] + [1]*len(PRINCIPLES))
    with row_cols[0]:
        st.markdown(f"**{fn}**")
    for j, p in enumerate(PRINCIPLES, start=1):
        key = f"mx_{fn}_{p}"
        default_marked = (fn, p) in pre if mode == "Thesis scenarios" else False
        with row_cols[j]:
            mark = st.checkbox(" ", value=default_marked, key=key, label_visibility="collapsed")
            matrix_state[(fn, p)] = 1 if mark else 0

# Optional heatmap view (visual only)
if ui_heatmap:
    st.markdown("##### Matrix heatmap (visual emphasis)")
    df = pd.DataFrame(0, index=NIST_FUNCTIONS, columns=PRINCIPLES)
    for (fn, p), v in matrix_state.items():
        df.loc[fn, p] = v
    st.dataframe(df.style.background_gradient(axis=None), use_container_width=True)

# Celebrate if any cell is selected
any_selected = any(matrix_state.values())
if ui_celebrate and any_selected:
    st.balloons()

st.divider()

# ---------- 4) Institutional & Governance Constraints ----------
st.markdown("### 4) Institutional & Governance Constraints")
constraints = st.multiselect("Select constraints relevant to this scenario", GOV_CONSTRAINTS, default=pd_defaults.get("constraints", []))

# Update live summary now that we have selections
with st.sidebar:
    sel_fn_ph.markdown("**NIST functions selected:** " + (", ".join(selected_nist) if ('selected_nist' in locals() and selected_nist) else "_none_"))
    sel_pr_ph.markdown("**Ethical principles (active):** " + (", ".join(selected_principles) if ('selected_principles' in locals() and selected_principles) else "_none_"))
    sel_c_ph.markdown("**Constraints picked:** " + (", ".join(constraints) if constraints else "_none_"))

st.divider()

# ---------- 5) Documentation & Rationale ----------
st.markdown("### 5) Documentation & Rationale")
st.caption("_Header retained intentionally. You said you’ll decide on layout later; no input controls are shown here yet._")

st.divider()

# ---------- Export snapshot (nice polished touch) ----------
report_md = []
report_md.append(f"# Decision Snapshot — {scenario}\n")
report_md.append("## Technical considerations (NIST)\n")
if 'selected_nist' in locals() and selected_nist:
    for fn in selected_nist:
        report_md.append(f"- {fn} — {scenario_csfs_explanations(description).get(fn, '')}")
else:
    report_md.append("- _None selected_")
report_md.append("\n## Ethical tensions (Principlist)\n")
if tensions:
    for label, tags in tensions:
        report_md.append(f"- {label} _(lens: {', '.join(tags)})_")
else:
    report_md.append("- _None listed_")
report_md.append("\n## Matrix (checked cells)\n")
checked_pairs = [f"- {fn} × {p}" for (fn, p), v in matrix_state.items() if v == 1]
report_md.extend(checked_pairs if checked_pairs else ["- _No cells checked_"])
report_md.append("\n## Constraints\n")
report_md.append("- " + ("\n- ".join(constraints) if constraints else "_None_"))
snapshot = "\n".join(report_md)

st.download_button(
    "📄 Export decision snapshot (Markdown)",
    data=snapshot.encode("utf-8"),
    file_name=f"decision_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
    mime="text/markdown",
)
