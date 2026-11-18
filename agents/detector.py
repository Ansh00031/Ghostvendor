"""Agent 1: Repository & Dependency Detective.
Inspects AST to identify external third-party dependencies, API calls, and fragility vectors.
"""

import ast
from typing import Dict, List, Any


class DependencyDetective:
    """Analyzes Python code to detect vendor dependencies and fragile access patterns."""

    KNOWN_VENDORS = {
        "stripe": "Stripe Payments",
        "sendgrid": "SendGrid Email",
        "auth0": "Auth0 Authentication",
        "openai": "OpenAI / LLM API",
        "twilio": "Twilio Communications",
        "boto3": "AWS Cloud Services",
        "requests": "Generic HTTP Client",
        "httpx": "Async HTTP Client",
        "urllib": "Standard HTTP Client"
    }

    def __init__(self):
        self.name = "Dependency Detective"

    def analyze(self, source_code: str) -> Dict[str, Any]:
        """Performs static AST analysis on target code."""
        findings = {
            "vendors_detected": [],
            "fragile_patterns": [],
            "risk_score": 0,
            "risk_level": "LOW",
            "calls_detected": [],
            "functions": []
        }

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            findings["error"] = f"Syntax error parsing code: {str(e)}"
            return findings

        # Check imports & variables
        lower_code = source_code.lower()
        for vendor_key, vendor_name in self.KNOWN_VENDORS.items():
            if vendor_key in lower_code:
                findings["vendors_detected"].append({
                    "id": vendor_key,
                    "name": vendor_name
                })

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                findings["functions"].append(node.name)

            # Direct subscription access: obj["key"] or arr[0]
            if isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Constant):
                    key_val = node.slice.value
                    if isinstance(key_val, str):
                        findings["fragile_patterns"].append({
                            "type": "Unsafe Dict Indexing",
                            "detail": f"Direct key access ['{key_val}'] vulnerable to Schema Drift (KeyError)",
                            "line": getattr(node, "lineno", 1)
                        })
                    elif isinstance(key_val, int):
                        findings["fragile_patterns"].append({
                            "type": "Unsafe Sequence Indexing",
                            "detail": f"Direct index [{key_val}] vulnerable to Empty Sequence / Payload Changes (IndexError)",
                            "line": getattr(node, "lineno", 1)
                        })

            # Detect external API calls
            if isinstance(node, ast.Call):
                call_repr = self._get_call_name(node)
                if any(v in call_repr.lower() for v in self.KNOWN_VENDORS):
                    findings["calls_detected"].append({
                        "call": call_repr,
                        "line": getattr(node, "lineno", 1)
                    })

        # Calculate risk score
        num_patterns = len(findings["fragile_patterns"])
        has_try_except = any(isinstance(node, ast.Try) for node in ast.walk(tree))
        
        base_score = min(num_patterns * 18, 70)
        if not has_try_except:
            base_score += 25
            findings["fragile_patterns"].append({
                "type": "Missing Exception Guard",
                "detail": "No try-except block detected around third-party execution",
                "line": 1
            })

        findings["risk_score"] = min(base_score, 98)
        if findings["risk_score"] >= 70:
            findings["risk_level"] = "CRITICAL"
        elif findings["risk_score"] >= 40:
            findings["risk_level"] = "HIGH"
        else:
            findings["risk_level"] = "MODERATE"

        return findings

    def _get_call_name(self, node: Any) -> str:
        """Helper to get string representation of a call or attribute chain."""
        if isinstance(node, ast.Call):
            return self._get_call_name(node.func)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_call_name(node.value)}.{node.attr}"
        return "unknown_call"
