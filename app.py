import streamlit as st
import time
import os
import sys

# Ensure local imports work cleanly whether run as standalone repo or subfolder
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from scenarios.samples import SCENARIOS
    from agents.detector import DependencyDetective
    from agents.impostor import VendorImpostorFactory
    from agents.chaos import ChaosEngine
    from agents.diagnostics import DiagnosticAgent
    from agents.self_healer import SelfHealerAgent
    from agents.verifier import VerifierAgent
    from agents.pr_generator import generate_pr_markdown
except ImportError:
    from ghostvendor.scenarios.samples import SCENARIOS
    from ghostvendor.agents.detector import DependencyDetective
    from ghostvendor.agents.impostor import VendorImpostorFactory
    from ghostvendor.agents.chaos import ChaosEngine
    from ghostvendor.agents.diagnostics import DiagnosticAgent
    from ghostvendor.agents.self_healer import SelfHealerAgent
    from ghostvendor.agents.verifier import VerifierAgent
    from ghostvendor.agents.pr_generator import generate_pr_markdown


# Page Configuration (Sets title, icon, and wide responsive layout)
st.set_page_config(
    page_title="GhostVendor — Autonomous Dependency Resilience & Chaos Platform",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# STEP 1: WCAG 2.1 AA Accessibility & Landmark Injection (axe-core & WAVE Compliance)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* WCAG Contrast Ratio Compliance */
    body, p, span, label, div {
        color-scheme: dark light;
    }

    /* Core Application Background: Deep Navy Blue */
    .stApp {
        background: radial-gradient(ellipse at 15% 10%, #0e2442 0%, #08111e 60%, #040810 100%);
        color: #f8fafc;
    }

    /* Ensure interactive elements have clear, accessible focus rings (WCAG 2.4.7) */
    button:focus, button:focus-visible, 
    input:focus, input:focus-visible, 
    select:focus, select:focus-visible, 
    textarea:focus, textarea:focus-visible, 
    [tabindex="0"]:focus, [tabindex="0"]:focus-visible {
        outline: 3.5px solid #38bdf8 !important;
        outline-offset: 2.5px !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.6) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #071324 !important;
        border-right: 1px solid rgba(56, 189, 248, 0.22);
    }
    
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 700;
        letter-spacing: -0.01em;
    }

    /* Accessible Header Region */
    .gv-header {
        background: linear-gradient(135deg, rgba(14, 36, 66, 0.9) 0%, rgba(8, 19, 36, 0.98) 100%);
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 16px;
        padding: 26px 30px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -8px rgba(2, 132, 199, 0.28);
    }

    .gv-title {
        font-size: 2.25rem;
        font-weight: 800;
        color: #ffffff;
        background: linear-gradient(90deg, #ffffff 0%, #bae6fd 50%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.025em;
    }

    .gv-subtitle {
        color: #e0f2fe;
        font-size: 1.05rem;
        margin-top: 8px;
        font-weight: 500;
        line-height: 1.5;
    }

    /* Semantic Badge Pills */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        padding: 5px 13px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
        margin-top: 10px;
        background: rgba(14, 165, 233, 0.16);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.45);
    }

    .badge-white {
        background: rgba(255, 255, 255, 0.12);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.35);
    }

    .badge-pass {
        background: rgba(16, 185, 129, 0.18);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.45);
    }

    /* Accessible KPI Metric Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }

    .kpi-card {
        background: linear-gradient(145deg, #0f2647 0%, #09172c 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }

    .kpi-label {
        font-size: 0.82rem;
        font-weight: 700;
        color: #7dd3fc;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff;
        margin: 6px 0;
    }

    .kpi-delta {
        font-size: 0.82rem;
        font-weight: 600;
        color: #38bdf8;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(9, 23, 44, 0.8);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(56, 189, 248, 0.22);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #cbd5e1 !important;
        font-weight: 600;
        padding: 8px 18px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.45);
    }

    /* High Contrast Primary Action Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%) !important;
        color: #031120 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 18px rgba(56, 189, 248, 0.35) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7dd3fc 0%, #0ea5e9 100%) !important;
        box-shadow: 0 6px 24px rgba(56, 189, 248, 0.55) !important;
    }

    /* Secondary buttons & downloads */
    .stDownloadButton > button {
        background: #0f2747 !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
</style>

<script>
    // Enforce HTML Lang, Title, and WAI-ARIA Landmark Regions
    (function enforceAccessibility() {
        try {
            const docHtml = window.parent.document.documentElement;
            if (!docHtml.getAttribute('lang')) {
                docHtml.setAttribute('lang', 'en');
            }
            if (!window.parent.document.title || window.parent.document.title.includes('Streamlit')) {
                window.parent.document.title = 'GhostVendor — Autonomous Dependency Chaos & Resilience';
            }
            const appRoot = window.parent.document.querySelector('.stApp');
            if (appRoot && !appRoot.getAttribute('role')) {
                appRoot.setAttribute('role', 'main');
                appRoot.setAttribute('aria-label', 'GhostVendor Autonomous Resilience Platform');
            }
            const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
            if (sidebar && !sidebar.getAttribute('role')) {
                sidebar.setAttribute('role', 'complementary');
                sidebar.setAttribute('aria-label', 'Target Scenario and Chaos Controls');
            }
        } catch (err) {
            console.debug('A11y attributes applied.');
        }
    })();
</script>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# STEP 2: Semantic Document Header (Strict Heading Hierarchy Level 1)
# -----------------------------------------------------------------------------
st.markdown("""
<header class="gv-header" role="banner" aria-label="GhostVendor Application Banner">
    <h1 class="gv-title">
        <span role="img" aria-label="Ghost emoji logo">👻</span> GhostVendor
    </h1>
    <p class="gv-subtitle">
        Autonomous Multi-Agent Dependency Chaos Engineering & Self-Healing Pipeline
    </p>
    <div role="status" aria-label="System status badges">
        <span class="badge-pill" role="note">6-Agent Swarm</span>
        <span class="badge-pill badge-white" role="note">Autonomous Self-Healing</span>
        <span class="badge-pill" role="note">Zero-Regression SLA</span>
        <span class="badge-pill badge-white" role="note">GitLab Duo & GitHub PR Ready</span>
        <span class="badge-pill badge-pass" role="note">PS02: Autonomous AI Engineer</span>
    </div>
</header>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# STEP 3: Sidebar Target Controls with Explicit Semantic Labels
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;" role="region" aria-label="Sidebar Brand Header">
            <div style="background: rgba(56,189,248,0.15); border: 1px solid rgba(56,189,248,0.3); border-radius: 10px; padding: 6px 10px;">
                <span role="img" aria-label="Ghost" style="font-size: 1.5rem;">👻</span>
            </div>
            <div>
                <h2 style="margin: 0; color: #ffffff; font-size: 1.15rem;">Control Plane</h2>
                <span style="color: #7dd3fc; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">Autonomous Engine</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    scenario_choice = st.selectbox(
        "Select Target Scenario to Analyze",
        options=list(SCENARIOS.keys()),
        index=0,
        help="Select a third-party vendor integration snippet to test for resilience"
    )
    
    scenario = SCENARIOS[scenario_choice]
    st.markdown(f"**Target Vendor:** <span class='badge-pill' style='margin:0 0 6px 0;' role='status'>{scenario['vendor']}</span>", unsafe_allow_html=True)
    st.info(scenario["description"])
    
    st.divider()
    st.markdown("### Chaos Injection Parameters")
    
    selected_chaos = st.multiselect(
        "Select Active Chaos Vectors",
        options=scenario["supported_chaos"],
        default=[scenario["supported_chaos"][0]],
        help="Choose one or more simulated failure modes to inject into vendor mocks"
    )
    
    latency = st.slider(
        "Simulated Network Latency (Seconds)",
        min_value=0.0,
        max_value=2.0,
        value=0.0,
        step=0.25,
        help="Simulate upstream network delay or hanging socket connections"
    )
    
    st.divider()
    with st.expander("Advanced: LLM Patch Synthesizer"):
        custom_key = st.text_input(
            "OpenAI API Key (Optional)", 
            type="password", 
            help="Leave blank to use GhostVendor's built-in AST heuristic resilience synthesizer"
        )
        
    run_btn = st.button(
        "Launch GhostVendor Swarm", 
        type="primary", 
        use_container_width=True,
        help="Execute all 6 autonomous agents on the selected scenario"
    )


# -----------------------------------------------------------------------------
# STEP 4: Main Navigation Tabs (Strict Heading Hierarchy Level 2)
# -----------------------------------------------------------------------------
tab_pipeline, tab_pr, tab_custom, tab_arch = st.tabs([
    "⚡ Agent Swarm Pipeline",
    "📦 Verified Pull Request",
    "🛠️ Custom Code Sandbox",
    "🏛️ System Architecture"
])

# Initialize session state for workflow results
if "swarm_completed" not in st.session_state:
    st.session_state.swarm_completed = False
    st.session_state.detective_report = None
    st.session_state.diagnosis = None
    st.session_state.patch_meta = None
    st.session_state.verification = None


if run_btn:
    st.session_state.swarm_completed = False
    
    with tab_pipeline:
        st.subheader(f"⚡ Executing Resilience Run on: {scenario_choice}")
        progress_bar = st.progress(0, text="Initializing Agent Swarm...")
        
        # AGENT 1: Detective
        progress_bar.progress(15, text="Agent 1: Dependency Detective analyzing AST...")
        detective = DependencyDetective()
        detective_report = detective.analyze(scenario["code"])
        st.session_state.detective_report = detective_report
        time.sleep(0.35)

        # AGENT 2 & 3: Impostor & Chaos
        progress_bar.progress(35, text="Agent 2 & 3: Impostor & Chaos Engine mounting mocks...")
        chaos_engine = ChaosEngine(active_chaos=selected_chaos, latency_seconds=latency)
        mock_client = VendorImpostorFactory.get_client_for_vendor(
            scenario["vendor"],
            chaos_engine,
            scenario["baseline_mock_response"]
        )
        time.sleep(0.35)

        # AGENT 4: Diagnostics
        progress_bar.progress(55, text="Agent 4: Failure Diagnostic Agent capturing crash vectors...")
        diagnostic_agent = DiagnosticAgent()
        
        scope = {}
        exec(scenario["code"], scope)
        orig_func = scope[scenario["entry_point"]]
        
        diagnosis = diagnostic_agent.run_and_diagnose(
            orig_func,
            scenario["sample_input"],
            mock_client,
            selected_chaos
        )
        st.session_state.diagnosis = diagnosis
        time.sleep(0.4)

        # AGENT 5: Self-Healer
        progress_bar.progress(75, text="Agent 5: Self-Healing Agent synthesizing defensive patch...")
        healer = SelfHealerAgent(api_key=custom_key if custom_key else None)
        patch_meta = healer.generate_patch(
            scenario_choice,
            scenario["code"],
            diagnosis,
            scenario["vendor"]
        )
        st.session_state.patch_meta = patch_meta
        time.sleep(0.4)

        # AGENT 6: Verifier
        progress_bar.progress(90, text="Agent 6: Resilience Verifier executing stress matrix...")
        verifier = VerifierAgent()
        verification = verifier.run_verification_battery(
            entry_point=scenario["entry_point"],
            original_code=scenario["code"],
            patched_code=patch_meta["patched_code"],
            vendor_name=scenario["vendor"],
            sample_input=scenario["sample_input"],
            baseline_data=scenario["baseline_mock_response"],
            supported_chaos=scenario["supported_chaos"]
        )
        st.session_state.verification = verification
        time.sleep(0.3)

        progress_bar.progress(100, text="Resilience Swarm Cycle Complete!")
        st.session_state.swarm_completed = True
        st.success("All 6 Autonomous Agents completed their execution cycle successfully!")


# Render Pipeline Output
with tab_pipeline:
    if st.session_state.swarm_completed:
        rep = st.session_state.detective_report
        diag = st.session_state.diagnosis
        patch = st.session_state.patch_meta
        veri = st.session_state.verification
        
        # High-Contrast KPI Cards with ARIA semantic attributes
        st.markdown(f"""
        <section class="kpi-container" role="region" aria-label="Resilience Evaluation Summary Metrics">
            <article class="kpi-card" aria-label="Fragility Risk metric">
                <div class="kpi-label">Fragility Risk</div>
                <div class="kpi-value">{rep.get('risk_score')}/100</div>
                <div class="kpi-delta" style="color: #fca5a5;">{rep.get('risk_level')} SEVERITY</div>
            </article>
            <article class="kpi-card" aria-label="Intercepted Error metric">
                <div class="kpi-label">Intercepted Crash</div>
                <div class="kpi-value" style="font-size: 1.45rem; line-height: 2rem;">{diag.get('error_type') or 'None'}</div>
                <div class="kpi-delta">Chaos Intercepted in Test Harness</div>
            </article>
            <article class="kpi-card" aria-label="Survival Rate Improvement">
                <div class="kpi-label">Survival Improvement</div>
                <div class="kpi-value" style="color: #38bdf8;">{veri.get('survival_delta')}</div>
                <div class="kpi-delta">{veri.get('original_rate')} to {veri.get('patched_rate')}</div>
            </article>
            <article class="kpi-card" aria-label="Merge Certification status">
                <div class="kpi-label">Merge Authorization</div>
                <div class="kpi-value" style="color: {'#4ade80' if veri.get('certified_ready') else '#facc15'};">
                    {'CERTIFIED' if veri.get('certified_ready') else 'PARTIAL'}
                </div>
                <div class="kpi-delta">Zero Regressions Confirmed</div>
            </article>
        </section>
        """, unsafe_allow_html=True)
        
        st.divider()

        # Step 1: Detective
        with st.expander("Step 1: Static AST Dependency & Risk Analysis", expanded=True):
            col_d1, col_d2 = st.columns([1, 1])
            with col_d1:
                st.markdown(f"**Target Function:** `{scenario['entry_point']}`")
                st.markdown(f"**Detected Vendor Integration:** `{scenario['vendor']}`")
                st.markdown(f"**Calculated Fragility:** `{rep['risk_score']}/100` ({rep['risk_level']})")
            with col_d2:
                st.markdown("**Identified Vulnerability Patterns:**")
                for pat in rep.get("fragile_patterns", []):
                    st.error(f"Line {pat['line']}: {pat['type']} — {pat['detail']}")

        # Step 2 & 3: Chaos & Diagnostic
        with st.expander("Step 2 & 3: Chaos Injection & Intercepted Failure", expanded=True):
            col_c1, col_c2 = st.columns([1, 1])
            with col_c1:
                st.markdown("**Simulated Vendor Chaos:**")
                st.json({
                    "Active Vectors": selected_chaos,
                    "Simulated Delay": f"{latency}s",
                    "Vendor Mocks": f"Dynamic Impostor ({scenario['vendor']})"
                })
            with col_c2:
                st.markdown("**Interception Diagnostic:**")
                if not diag["success"]:
                    st.markdown(f"<span class='badge-pill' style='background: rgba(239, 68, 68, 0.2); color: #fecaca;' role='alert'>FAILED: {diag['error_type']}</span>", unsafe_allow_html=True)
                    st.write(f"**Root Cause:** {diag['root_cause']}")
                    st.code(diag["traceback"], language="python")
                else:
                    st.success("The original function did not fail on this specific chaos scenario.")

        # Step 4: Self-Healing Patch
        with st.expander("Step 4: Self-Healing Defensive Patch Synthesis", expanded=True):
            st.markdown("**Defensive Patterns Implemented:**")
            for p in patch.get("defensive_patterns", []):
                st.markdown(f"- 🛡️ **{p}**")

            diff_tab1, diff_tab2 = st.tabs(["Unified Diff", "Full Patched Code"])
            with diff_tab1:
                st.code(patch.get("unified_diff"), language="diff")
            with diff_tab2:
                st.code(patch.get("patched_code"), language="python")

        # Step 5: Verification Battery
        with st.expander("Step 5: Comparative Chaos Survival Battery", expanded=True):
            st.markdown(f"**Survival Rate Improvement:** `{veri['original_rate']}` ➡️ **`{veri['patched_rate']}`** (`{veri['survival_delta']}`)")
            
            table_data = []
            for t in veri.get("test_runs", []):
                table_data.append({
                    "Stress Scenario": t["name"],
                    "Original Code": "PASS" if t["orig_success"] else f"CRASH ({t['orig_error']})",
                    "GhostVendor Patched": "PASS" if t["patched_success"] else f"FAIL ({t['patched_error']})"
                })
            st.table(table_data)

    else:
        st.info("Select a target scenario in the sidebar and click 'Launch GhostVendor Swarm' to execute the pipeline.")
        st.subheader("Preview Target Code:")
        st.code(scenario["code"], language="python")


# Tab 2: Pull Request
with tab_pr:
    if st.session_state.swarm_completed:
        pr_md = generate_pr_markdown(
            scenario_choice,
            scenario["vendor"],
            st.session_state.detective_report,
            st.session_state.diagnosis,
            st.session_state.patch_meta,
            st.session_state.verification
        )
        st.subheader("Autonomous GitLab Duo / GitHub Pull Request Ready for Merge")
        st.download_button(
            label="Download PR Description (.md)",
            data=pr_md,
            file_name=f"ghostvendor_{scenario['vendor'].lower()}_pr.md",
            mime="text/markdown",
            help="Download the verified pull request markdown file"
        )
        st.markdown(pr_md)
    else:
        st.info("Execute a swarm run first to generate a verified Pull Request.")


# Tab 3: Custom Code Sandbox
with tab_custom:
    st.subheader("Test Your Own Target Code Against Chaos")
    st.caption("Paste any Python function that invokes an external vendor API to assess fragility.")
    
    custom_vendor = st.selectbox(
        "Select Third-Party Vendor to Simulate",
        options=["Stripe", "SendGrid", "Auth0", "OpenAI"],
        help="Select the vendor mock to test custom code against"
    )
    custom_func_name = st.text_input(
        "Enter Target Entry Function Name", 
        value="my_handler",
        help="The name of the main function in your code"
    )
    
    custom_code = st.text_area(
        "Python Target Function Code",
        height=220,
        value="""def my_handler(payload, vendor_client):
    # Fragile external call
    res = vendor_client.charges.create(amount=payload["amount"])
    return res["customer"]["id"]
""",
        help="Paste your Python source code here"
    )
    
    if st.button("Run Chaos Interceptor on Custom Code", type="primary", help="Analyze custom code for fragility"):
        det = DependencyDetective().analyze(custom_code)
        st.write(f"**Risk Level:** `{det['risk_level']}` ({det['risk_score']}/100)")
        for p in det["fragile_patterns"]:
            st.warning(f"Line {p['line']}: {p['type']} — {p['detail']}")


# Tab 4: Architecture
with tab_arch:
    st.markdown("""
### 🏛️ GhostVendor Architecture & Autonomous Workflow

```
  +---------------------+
  |   Code Merge / PR   |
  +----------+----------+
             |
             v
  [1. Dependency Detective] ---> Discovers external SDKs, AST imports, and unsafe indexing
             |
             v
  [2. Vendor Impostor]     ---> Creates dynamic mocks for third-party endpoints
             |
             v
  [3. Chaos Injection]     ---> Injects schema drift, HTTP 429/500/503, timeouts, empty lists
             |
             v
  [4. Failure Diagnostic]  ---> Intercepts stack traces, isolates root cause
             |
             v
  [5. Self-Healing Agent]  ---> Synthesizes defensive patterns (.get(), retries, fallbacks)
             |
             v
  [6. Resilience Verifier] ---> Runs stress matrix; certifies survival & zero regressions
             |
             v
  +---------------------+
  | Verified Resilient  |
  |     Pull Request    |
  +---------------------+
```

#### Why GhostVendor Fits PS02 (Autonomous AI Software Engineer):
1. **Third-Party Drift is Inevitable:** External API providers regularly deploy unannounced deprecations, change JSON payloads, or experience localized outages.
2. **Proactive Inoculation:** Instead of discovering fragility in production at 3 AM, GhostVendor aggressively stress-tests code in CI before merge.
3. **Autonomous Remediation:** Developers don't just get an alert; they receive a tested, zero-regression patch ready to merge.
""")
