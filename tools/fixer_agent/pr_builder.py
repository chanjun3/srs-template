from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .models import PatchProposal, TriageResult


@dataclass
class PRBuilder:
    """Constructs PR bodies that follow FixerAgent SRS requirements."""

    def build_pr(self, run_id: str, triage: TriageResult, patch: Optional[PatchProposal]) -> str:
        lines = [
            f"## FixerAgent Review for Run #{run_id}",
            "",
            f"- Fault Category: `{triage.fault_category.value}`",
            f"- Severity: `{triage.severity.value}`",
            "- FixerAgent does **not** merge to `main`; ReviewerAgent or humans must approve.",
            "",
            "### Summary",
            triage.summary,
            "",
            "### SRS References",
        ]
        for ref in triage.srs_references:
            lines.append(f"- {ref}")

        if patch and patch.passes_safety_checks:
            lines.extend(
                [
                    "",
                    "### Proposed Minimal Patch",
                    patch.notes,
                    "",
                    "```diff",
                    patch.diff_text,
                    "```",
                ]
            )
        elif patch and not patch.passes_safety_checks:
            lines.extend(
                [
                    "",
                    "### Patch Status",
                    "Auto-fix proposed but blocked by safety checks. ReviewerAgent MUST reject.",
                    patch.notes,
                ]
            )
        else:
            lines.extend(
                [
                    "",
                    "### Patch Status",
                    "Auto-fix was not attempted. ReviewerAgent should inspect triage logs.",
                ]
            )

        return "\n".join(lines)
