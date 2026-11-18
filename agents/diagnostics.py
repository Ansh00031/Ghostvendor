"""Agent 4: Failure & Diagnostics Agent.
Executes code in isolated context, intercepts exceptions, extracts stack traces,
and generates structured root cause diagnoses.
"""

import sys
import traceback
from typing import Any, Callable, Dict, Optional


class DiagnosticAgent:
    """Safely runs code with chaotic mocks and diagnoses failures."""

    def __init__(self):
        self.name = "Failure & Diagnostic Agent"

    def run_and_diagnose(
        self,
        func: Callable,
        input_arg: Any,
        mock_client: Any,
        active_chaos: list
    ) -> Dict[str, Any]:
        """Executes the entry point function and analyzes the outcome."""
        result = {
            "success": False,
            "output": None,
            "error_type": None,
            "error_message": "",
            "failing_line": None,
            "traceback": "",
            "root_cause": "",
            "chaos_modes_applied": active_chaos
        }

        try:
            output = func(input_arg, mock_client)
            result["success"] = True
            result["output"] = output
            result["root_cause"] = "Execution passed without uncaught exceptions."
        except Exception as e:
            exc_type, exc_val, exc_tb = sys.exc_info()
            tb_lines = traceback.format_exception(exc_type, exc_val, exc_tb)
            full_tb = "".join(tb_lines)

            # Find the line in the target function
            target_tb = exc_tb
            last_lineno = None
            while target_tb:
                last_lineno = target_tb.tb_lineno
                target_tb = target_tb.tb_next

            result["error_type"] = exc_type.__name__
            result["error_message"] = str(exc_val)
            result["failing_line"] = last_lineno
            result["traceback"] = full_tb
            result["root_cause"] = self._synthesize_root_cause(exc_type.__name__, str(exc_val), active_chaos)

        return result

    def _synthesize_root_cause(self, exc_name: str, message: str, active_chaos: list) -> str:
        """Translates technical stack trace into actionable diagnostic insight."""
        if "KeyError" in exc_name:
            return (
                f"Schema Drift Vulnerability: The code attempted direct dictionary lookup on missing key {message}. "
                "The upstream vendor altered response keys or omitted fields, causing an uncaught KeyError."
            )
        elif "IndexError" in exc_name:
            return (
                "Empty Sequence Vulnerability: Code accessed array index directly (e.g. [0]) assuming "
                "the vendor always returns non-empty collections. When empty, an IndexError occurred."
            )
        elif "VendorRateLimit" in exc_name or "429" in message:
            return (
                "Rate-Limiting Flaw: The upstream vendor throttled requests with HTTP 429. "
                "The target service lacks exponential backoff, retry mechanisms, or fallback queuing."
            )
        elif "VendorServer" in exc_name or "500" in message or "503" in message:
            return (
                "Upstream Outage Flaw: The external service encountered an outage or high load. "
                "Without a circuit breaker or fallback cache, the error cascaded directly into the application."
            )
        elif "VendorTimeout" in exc_name or "timed out" in message.lower():
            return (
                "Hanging Socket / Timeout Flaw: The external vendor network was delayed. "
                "The client had no explicit deadline or timeout handling, causing thread exhaustion."
            )
        return f"Unhandled {exc_name}: {message}. External dependency interaction was unguarded."
