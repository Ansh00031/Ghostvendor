"""Agent 3: Chaos Injection Engine.
Injects failures, schema mutations, rate-limits, and latencies into vendor responses.
"""

import copy
import time
from typing import Any, Dict, List, Optional


class ChaosException(Exception):
    """Base exception for simulated vendor failures."""
    pass


class VendorRateLimitError(ChaosException):
    """Simulated HTTP 429 Too Many Requests."""
    pass


class VendorServerError(ChaosException):
    """Simulated HTTP 500 / 503 Service Unavailable."""
    pass


class VendorTimeoutError(ChaosException):
    """Simulated Network Timeout."""
    pass


class ChaosEngine:
    """Configurable chaos generator that mutates responses or raises errors."""

    def __init__(self, active_chaos: Optional[List[str]] = None, latency_seconds: float = 0.0):
        self.active_chaos = active_chaos or []
        self.latency_seconds = latency_seconds
        self.mutation_history = []

    def execute(self, baseline_response: Dict[str, Any]) -> Any:
        """Applies configured chaos modes to the baseline response."""
        data = copy.deepcopy(baseline_response)

        # 1. Latency injection
        if self.latency_seconds > 0:
            time.sleep(min(self.latency_seconds, 3.0))

        # Check each chaos mode
        for mode in self.active_chaos:
            mode_lower = mode.lower()

            if "500" in mode_lower or "outage" in mode_lower:
                self.mutation_history.append("Injected HTTP 500 Internal Server Outage")
                raise VendorServerError("HTTP 500: Internal Server Error from upstream vendor service")

            elif "429" in mode_lower or "rate limit" in mode_lower:
                self.mutation_history.append("Injected HTTP 429 Rate Limit Exceeded")
                raise VendorRateLimitError("HTTP 429: Rate limit exceeded. Retry-After: 60s")

            elif "503" in mode_lower or "overloaded" in mode_lower:
                self.mutation_history.append("Injected HTTP 503 Service Unavailable")
                raise VendorServerError("HTTP 503: Service Unavailable. Downstream capacity exhausted.")

            elif "timeout" in mode_lower:
                self.mutation_history.append("Injected Socket / Network Timeout")
                raise VendorTimeoutError("Connection timed out after 10000ms")

            elif "schema drift" in mode_lower or "field renamed" in mode_lower:
                data = self._apply_schema_drift(data)

            elif "missing" in mode_lower:
                data = self._apply_missing_keys(data)

            elif "empty array" in mode_lower:
                data = self._apply_empty_arrays(data)

            elif "type mutation" in mode_lower or "corrupt" in mode_lower:
                data = self._apply_type_corruption(data)

        return data

    def _apply_schema_drift(self, data: Any) -> Any:
        """Mutates standard field names into legacy or drifted names."""
        if not isinstance(data, dict):
            return data

        mutated = {}
        for k, v in data.items():
            if k == "customer" and isinstance(v, dict):
                # Drift: customer renamed to account_holder
                mutated["account_holder"] = v
                self.mutation_history.append("Renamed 'customer' -> 'account_holder'")
            elif k == "billing_details" and isinstance(v, dict):
                # Drift: billing_details renamed to invoice_profile
                mutated["invoice_profile"] = v
                self.mutation_history.append("Renamed 'billing_details' -> 'invoice_profile'")
            elif k == "identities" and isinstance(v, list):
                # Drift: identities renamed to auth_providers
                mutated["auth_providers"] = v
                self.mutation_history.append("Renamed 'identities' -> 'auth_providers'")
            elif k == "choices" and isinstance(v, list):
                # Drift: choices renamed to candidates
                mutated["candidates"] = v
                self.mutation_history.append("Renamed 'choices' -> 'candidates'")
            else:
                mutated[k] = self._apply_schema_drift(v) if isinstance(v, dict) else v

        return mutated

    def _apply_missing_keys(self, data: Any) -> Any:
        """Removes essential nested keys to simulate omissions."""
        if not isinstance(data, dict):
            return data
        
        mutated = copy.deepcopy(data)
        # Drop nested keys if present
        if "customer" in mutated and isinstance(mutated["customer"], dict):
            mutated["customer"].pop("id", None)
            self.mutation_history.append("Omitted 'customer.id' from response")
        if "app_metadata" in mutated:
            mutated.pop("app_metadata", None)
            self.mutation_history.append("Omitted 'app_metadata' object")
        return mutated

    def _apply_empty_arrays(self, data: Any) -> Any:
        """Empties array collections."""
        if not isinstance(data, dict):
            return data
        mutated = copy.deepcopy(data)
        for k, v in mutated.items():
            if isinstance(v, list):
                mutated[k] = []
                self.mutation_history.append(f"Emptied array '{k}'")
            elif isinstance(v, dict):
                mutated[k] = self._apply_empty_arrays(v)
        return mutated

    def _apply_type_corruption(self, data: Any) -> Any:
        """Corrupts data types (e.g. integer to string or null)."""
        if not isinstance(data, dict):
            return data
        mutated = copy.deepcopy(data)
        for k, v in mutated.items():
            if isinstance(v, int):
                mutated[k] = str(v)
                self.mutation_history.append(f"Corrupted int field '{k}' into string")
            elif isinstance(v, dict):
                mutated[k] = self._apply_type_corruption(v)
        return mutated
