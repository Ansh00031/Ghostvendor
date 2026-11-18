#!/usr/bin/env python3
"""GhostVendor Command Line Interface.
Run autonomous dependency chaos engineering & self-healing directly in the terminal.
"""

import argparse
import sys
import os

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


def run_pipeline(scenario_name: str, chaos_vector: str = None):
    if scenario_name not in SCENARIOS:
        print(f"[-] Unknown scenario '{scenario_name}'. Available:")
        for s in SCENARIOS:
            print(f"  - {s}")
        sys.exit(1)

    scenario = SCENARIOS[scenario_name]
    chaos_mode = chaos_vector or scenario["supported_chaos"][0]

    print("\n" + "="*70)
    print("👻 GHOSTVENDOR: Autonomous Dependency Resilience Pipeline")
    print("="*70)
    print(f"Target Scenario: {scenario_name}")
    print(f"Vendor SDK:      {scenario['vendor']}")
    print(f"Chaos Vector:    {chaos_mode}")
    print("-"*70)

    # 1. Detective
    print("\n[Step 1/6] 🕵️  Running Dependency & AST Detective...")
    detective = DependencyDetective()
    det_report = detective.analyze(scenario["code"])
    print(f"   -> Risk Score: {det_report['risk_score']}/100 ({det_report['risk_level']})")
    for pat in det_report["fragile_patterns"]:
        print(f"      * Line {pat['line']}: {pat['type']} ({pat['detail']})")

    # 2 & 3. Impostor & Chaos
    print(f"\n[Step 2/6] 🎭 Impersonating {scenario['vendor']} and Mounting Chaos Engine...")
    chaos = ChaosEngine(active_chaos=[chaos_mode])
    mock_client = VendorImpostorFactory.get_client_for_vendor(
        scenario["vendor"], chaos, scenario["baseline_mock_response"]
    )

    # 4. Diagnostics
    print("\n[Step 3/6] 💥 Executing Target Code Against Chaotic Vendor...")
    scope = {}
    exec(scenario["code"], scope)
    orig_func = scope[scenario["entry_point"]]

    diag_agent = DiagnosticAgent()
    diagnosis = diag_agent.run_and_diagnose(
        orig_func, scenario["sample_input"], mock_client, [chaos_mode]
    )

    if not diagnosis["success"]:
        print(f"   -> [CRASH INTERCEPTED] {diagnosis['error_type']}: {diagnosis['error_message']}")
        print(f"   -> Root Cause: {diagnosis['root_cause']}")
    else:
        print("   -> Target code did not crash under this vector.")

    # 5. Self-Healing Patch
    print("\n[Step 4/6] 🩹 Synthesizing Self-Healing Defensive Patch...")
    healer = SelfHealerAgent()
    patch_meta = healer.generate_patch(scenario_name, scenario["code"], diagnosis, scenario["vendor"])
    print("   -> Applied Defensive Patterns:")
    for pat in patch_meta["defensive_patterns"]:
        print(f"      * {pat}")

    # 6. Verification Battery
    print("\n[Step 5/6] 🧪 Running Comparative Chaos Survival Battery...")
    verifier = VerifierAgent()
    ver_results = verifier.run_verification_battery(
        entry_point=scenario["entry_point"],
        original_code=scenario["code"],
        patched_code=patch_meta["patched_code"],
        vendor_name=scenario["vendor"],
        sample_input=scenario["sample_input"],
        baseline_data=scenario["baseline_mock_response"],
        supported_chaos=scenario["supported_chaos"]
    )

    print(f"   -> Original Survival Rate: {ver_results['original_rate']}")
    print(f"   -> Patched Survival Rate:  {ver_results['patched_rate']} ({ver_results['survival_delta']})")
    print(f"   -> Baseline Preserved:     {ver_results['baseline_preserved']}")
    print(f"   -> Merge Certified:        {'YES' if ver_results['certified_ready'] else 'NO'}")

    # PR Generator
    print("\n[Step 6/6] 📦 Generating Pull Request Artifact...")
    pr_md = generate_pr_markdown(
        scenario_name,
        scenario["vendor"],
        det_report,
        diagnosis,
        patch_meta,
        ver_results
    )
    
    out_file = f"ghostvendor_pr_{scenario['vendor'].lower()}.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(pr_md)
    print(f"   -> Pull Request description written to: {out_file}")

    print("\n" + "="*70)
    print("✅ Run Complete! Launch Streamlit UI with: streamlit run ghostvendor/app.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GhostVendor CLI Runner")
    parser.add_argument(
        "--scenario",
        default="Stripe Payment Processing",
        help="Target scenario name"
    )
    parser.add_argument(
        "--chaos",
        default=None,
        help="Specific chaos vector to test"
    )
    args = parser.parse_args()
    run_pipeline(args.scenario, args.chaos)
