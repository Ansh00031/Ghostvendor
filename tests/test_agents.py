"""Unit and integration tests for GhostVendor multi-agent pipeline."""

import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from scenarios.samples import SCENARIOS
    from agents.detector import DependencyDetective
    from agents.chaos import ChaosEngine, VendorServerError, VendorRateLimitError
    from agents.impostor import VendorImpostorFactory
    from agents.diagnostics import DiagnosticAgent
    from agents.self_healer import SelfHealerAgent
    from agents.verifier import VerifierAgent
except ImportError:
    from ghostvendor.scenarios.samples import SCENARIOS
    from ghostvendor.agents.detector import DependencyDetective
    from ghostvendor.agents.chaos import ChaosEngine, VendorServerError, VendorRateLimitError
    from ghostvendor.agents.impostor import VendorImpostorFactory
    from ghostvendor.agents.diagnostics import DiagnosticAgent
    from ghostvendor.agents.self_healer import SelfHealerAgent
    from ghostvendor.agents.verifier import VerifierAgent


def test_detector_finds_fragile_patterns():
    detective = DependencyDetective()
    sample_code = SCENARIOS["Stripe Payment Processing"]["code"]
    report = detective.analyze(sample_code)
    
    assert report["risk_score"] > 50
    assert len(report["fragile_patterns"]) > 0
    assert any("Unsafe Dict Indexing" in p["type"] for p in report["fragile_patterns"])


def test_chaos_outage_injection():
    chaos = ChaosEngine(active_chaos=["HTTP 500 Outage"])
    with pytest.raises(VendorServerError):
        chaos.execute({"status": "ok"})


def test_chaos_rate_limit_injection():
    chaos = ChaosEngine(active_chaos=["Rate Limit (429)"])
    with pytest.raises(VendorRateLimitError):
        chaos.execute({"status": "ok"})


def test_chaos_schema_drift():
    chaos = ChaosEngine(active_chaos=["Schema Drift: Field Renamed"])
    baseline = {"customer": {"id": "cus_123"}, "billing_details": {"email": "test@test.com"}}
    mutated = chaos.execute(baseline)
    
    assert "account_holder" in mutated
    assert "customer" not in mutated
    assert "invoice_profile" in mutated


def test_full_pipeline_verification():
    scenario = SCENARIOS["Stripe Payment Processing"]
    
    # 1. Intercept failure on original
    chaos = ChaosEngine(active_chaos=["Schema Drift: Field Renamed"])
    mock_client = VendorImpostorFactory.get_client_for_vendor("Stripe", chaos, scenario["baseline_mock_response"])
    
    scope = {}
    exec(scenario["code"], scope)
    orig_func = scope[scenario["entry_point"]]
    
    diag_agent = DiagnosticAgent()
    diag = diag_agent.run_and_diagnose(
        orig_func, scenario["sample_input"], mock_client, ["Schema Drift: Field Renamed"]
    )
    assert diag["success"] is False
    assert "KeyError" in diag["error_type"]
    
    # 2. Heal
    healer = SelfHealerAgent()
    patch = healer.generate_patch("Stripe Payment Processing", scenario["code"], diag, "Stripe")
    assert patch["patched_code"] is not None
    assert len(patch["defensive_patterns"]) > 0
    
    # 3. Verify
    verifier = VerifierAgent()
    ver_results = verifier.run_verification_battery(
        entry_point=scenario["entry_point"],
        original_code=scenario["code"],
        patched_code=patch["patched_code"],
        vendor_name="Stripe",
        sample_input=scenario["sample_input"],
        baseline_data=scenario["baseline_mock_response"],
        supported_chaos=scenario["supported_chaos"]
    )
    assert ver_results["certified_ready"] is True
    assert ver_results["patched_passed"] > ver_results["original_passed"]
