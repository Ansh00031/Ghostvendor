"""Pull Request / Merge Request Markdown Generator.
Packages GhostVendor resilience diagnostics, verification results, and code diffs into a production PR.
"""

from typing import Any, Dict


def generate_pr_markdown(
    scenario_name: str,
    vendor_name: str,
    detective_report: Dict[str, Any],
    diagnosis: Dict[str, Any],
    patch_meta: Dict[str, Any],
    verification: Dict[str, Any]
) -> str:
    """Formats a complete production-ready Merge Request / Pull Request description."""
    survival_badge = "🟢 CERTIFIED RESILIENT" if verification.get("certified_ready") else "🟡 PARTIALLY PROTECTED"

    patterns_md = "\n".join([f"- [x] **{p}**" for p in patch_meta.get("defensive_patterns", [])])
    
    test_rows = []
    for t in verification.get("test_runs", []):
        orig_icon = "✅ Pass" if t["orig_success"] else f"❌ Crashed ({t['orig_error']})"
        patch_icon = "✅ Passed" if t["patched_success"] else f"⚠️ Error ({t['patched_error']})"
        test_rows.append(f"| `{t['name']}` | {orig_icon} | {patch_icon} |")

    tests_table = "\n".join(test_rows)

    markdown = f"""## 👻 GhostVendor Autonomous Remediation: {scenario_name}
> **Status:** `{survival_badge}` | **Survival Delta:** `{verification.get('survival_delta')}` | **Target Vendor:** `{vendor_name}`

---

### 📋 Executive Summary
GhostVendor's autonomous multi-agent swarm intercepted potential vendor vulnerabilities during static analysis. Through targeted chaos simulation, the original implementation crashed under unexpected upstream failure modes. 

A self-healing defensive patch has been synthesized, verified, and certified to survive upstream disruptions without downtime or unhandled exceptions.

### 🔍 Vulnerability & Fragility Findings
- **Detected Vendor SDK:** `{vendor_name}`
- **Initial Risk Score:** `{detective_report.get('risk_score', 'N/A')}/100` (`{detective_report.get('risk_level', 'UNKNOWN')}`)
- **Failure Mode Intercepted:** `{diagnosis.get('error_type', 'Unhandled Exception')}`
- **Root Cause:** {diagnosis.get('root_cause', 'N/A')}

### 🛡️ Defensive Patterns Implemented
{patterns_md}

### 📊 Verification & Chaos Survival Battery
| Stress Scenario | Original Code | GhostVendor Patched |
| :--- | :--- | :--- |
{tests_table}

- **Baseline Survival:** `{verification.get('original_rate')}` ➡️ `{verification.get('patched_rate')}`
- **Zero-Regression Guarantee:** {'Passed (Normal operations fully preserved)' if verification.get('baseline_preserved') else 'Check required'}

---

### 📝 Unified Patch Diff
```diff
{patch_meta.get('unified_diff', '# No diff available')}
```

---
*Generated autonomously by **GhostVendor Agent Swarm**.*
"""
    return markdown
