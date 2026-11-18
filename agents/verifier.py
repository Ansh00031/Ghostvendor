"""Agent 6: Resilience Verifier Agent.
Runs comparative test batteries on original code vs self-healed patch across baseline and chaotic conditions.
Computes survival rates, zero-regression confirmation, and final resilience scores.
"""

from typing import Any, Callable, Dict, List, Optional
try:
    from agents.chaos import ChaosEngine
    from agents.impostor import VendorImpostorFactory
except ImportError:
    from ghostvendor.agents.chaos import ChaosEngine
    from ghostvendor.agents.impostor import VendorImpostorFactory


class VerifierAgent:
    """Executes comparative stress tests to confirm patch survival."""

    def __init__(self):
        self.name = "Resilience Verifier Agent"

    def run_verification_battery(
        self,
        entry_point: str,
        original_code: str,
        patched_code: str,
        vendor_name: str,
        sample_input: Any,
        baseline_data: Dict[str, Any],
        supported_chaos: List[str]
    ) -> Dict[str, Any]:
        """Runs test battery comparing original vs patched implementation."""
        # Compile both functions safely
        orig_func = self._compile_function(original_code, entry_point)
        patch_func = self._compile_function(patched_code, entry_point)

        results = {
            "test_runs": [],
            "original_passed": 0,
            "patched_passed": 0,
            "total_tests": 0,
            "survival_delta": "+0%",
            "baseline_preserved": False,
            "certified_ready": False
        }

        # 1. Baseline Test (Clean vendor, no chaos)
        baseline_test = self._run_single_case(
            name="Baseline Normal Operation",
            chaos_modes=[],
            vendor_name=vendor_name,
            baseline_data=baseline_data,
            sample_input=sample_input,
            orig_func=orig_func,
            patch_func=patch_func
        )
        results["test_runs"].append(baseline_test)
        if baseline_test["patched_success"]:
            results["baseline_preserved"] = True

        # 2. Individual Chaos Cases
        for c_mode in supported_chaos:
            case_res = self._run_single_case(
                name=f"Chaos: {c_mode}",
                chaos_modes=[c_mode],
                vendor_name=vendor_name,
                baseline_data=baseline_data,
                sample_input=sample_input,
                orig_func=orig_func,
                patch_func=patch_func
            )
            results["test_runs"].append(case_res)

        # 3. Compound Chaos (Chaos Cocktail)
        if len(supported_chaos) >= 2:
            cocktail = self._run_single_case(
                name="Compound Chaos (Multi-Failure Scenario)",
                chaos_modes=supported_chaos[:2],
                vendor_name=vendor_name,
                baseline_data=baseline_data,
                sample_input=sample_input,
                orig_func=orig_func,
                patch_func=patch_func
            )
            results["test_runs"].append(cocktail)

        # Tally metrics
        results["total_tests"] = len(results["test_runs"])
        results["original_passed"] = sum(1 for t in results["test_runs"] if t["orig_success"])
        results["patched_passed"] = sum(1 for t in results["test_runs"] if t["patched_success"])

        orig_rate = (results["original_passed"] / results["total_tests"]) * 100
        patch_rate = (results["patched_passed"] / results["total_tests"]) * 100
        delta = patch_rate - orig_rate

        results["original_rate"] = f"{orig_rate:.1f}%"
        results["patched_rate"] = f"{patch_rate:.1f}%"
        results["survival_delta"] = f"+{delta:.1f}%"
        results["certified_ready"] = (patch_rate >= 80.0 and results["baseline_preserved"])

        return results

    def _run_single_case(
        self,
        name: str,
        chaos_modes: List[str],
        vendor_name: str,
        baseline_data: Dict[str, Any],
        sample_input: Any,
        orig_func: Optional[Callable],
        patch_func: Optional[Callable]
    ) -> Dict[str, Any]:
        """Runs one scenario against both implementations."""
        # Setup chaos engine and mock client for original
        chaos_orig = ChaosEngine(active_chaos=chaos_modes)
        client_orig = VendorImpostorFactory.get_client_for_vendor(vendor_name, chaos_orig, baseline_data)

        orig_ok = False
        orig_err = ""
        try:
            if orig_func:
                orig_func(sample_input, client_orig)
                orig_ok = True
        except Exception as e:
            orig_err = f"{type(e).__name__}: {str(e)[:60]}"

        # Setup chaos engine and mock client for patch
        chaos_patch = ChaosEngine(active_chaos=chaos_modes)
        client_patch = VendorImpostorFactory.get_client_for_vendor(vendor_name, chaos_patch, baseline_data)

        patch_ok = False
        patch_err = ""
        try:
            if patch_func:
                patch_func(sample_input, client_patch)
                patch_ok = True
        except Exception as e:
            patch_err = f"{type(e).__name__}: {str(e)[:60]}"

        return {
            "name": name,
            "chaos_modes": chaos_modes,
            "orig_success": orig_ok,
            "orig_error": orig_err,
            "patched_success": patch_ok,
            "patched_error": patch_err
        }

    def _compile_function(self, code_str: str, func_name: str) -> Optional[Callable]:
        """Safely executes code string and retrieves the target function."""
        try:
            scope = {}
            exec(code_str, scope)
            return scope.get(func_name)
        except Exception:
            return None
