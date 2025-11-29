from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Sequence

from .models import ArtifactBundle, FaultCategory, Severity, TriageResult, TriageFinding

FILE_PATTERN = re.compile(
    r"(?P<file>[A-Za-z0-9_\-./]+?\.(?:md|markdown|py|yml|yaml|json|toml|txt))"
)


def _extract_impacted_files(summary_text: str) -> List[str]:
    files = {match.group("file") for match in FILE_PATTERN.finditer(summary_text)}
    return sorted(files)


@dataclass
class TriageEngine:
    """Rule-based classifier aligned with the FixerAgent SRS fault taxonomy."""

    lint_patterns: Sequence[re.Pattern] = field(
        default_factory=lambda: (
            re.compile(r"markdownlint|MD\d{3}", re.IGNORECASE),
            re.compile(r"yamllint", re.IGNORECASE),
            re.compile(r"flake8|E\d{3}", re.IGNORECASE),
        )
    )
    ci_config_patterns: Sequence[re.Pattern] = field(
        default_factory=lambda: (
            re.compile(r"Invalid workflow file", re.IGNORECASE),
            re.compile(r"Unrecognized named-value", re.IGNORECASE),
            re.compile(r"workflow syntax", re.IGNORECASE),
        )
    )
    spec_drift_patterns: Sequence[re.Pattern] = field(
        default_factory=lambda: (
            re.compile(r"artifact name.+srs-ci-logs", re.IGNORECASE),
            re.compile(r"SRS drift", re.IGNORECASE),
            re.compile(r"Spec Update Required", re.IGNORECASE),
        )
    )

    def classify(self, artifact: ArtifactBundle) -> TriageResult:
        summary = artifact.ci_summary_text
        impacted_files = _extract_impacted_files(summary)
        excerpt = summary[:2000]

        for pattern in self.ci_config_patterns:
            if pattern.search(summary):
                return self._finalize(
                    TriageFinding(
                        fault_category=FaultCategory.CI_CONFIGURATION,
                        severity=Severity.CRITICAL,
                        auto_fix_allowed=False,
                        summary="CI configuration violates syntax invariants.",
                        srs_references=[
                            "FixerAgent SRS: FR-2",
                            "Global SRS: Syntax Invariants",
                        ],
                        evidence={
                            "summary_excerpt": excerpt,
                            "impacted_files": impacted_files,
                        },
                    )
                )

        for pattern in self.lint_patterns:
            if pattern.search(summary):
                return self._finalize(
                    TriageFinding(
                        fault_category=FaultCategory.SOURCE_CONTENT,
                        severity=Severity.WARNING,
                        auto_fix_allowed=True,
                        summary="Detected lint/static analysis failure.",
                        srs_references=["FixerAgent SRS: Fault Taxonomy"],
                        evidence={
                            "summary_excerpt": excerpt,
                            "impacted_files": impacted_files,
                        },
                    )
                )

        for pattern in self.spec_drift_patterns:
            if pattern.search(summary):
                return self._finalize(
                    TriageFinding(
                        fault_category=FaultCategory.SPEC_DRIFT,
                        severity=Severity.WARNING,
                        auto_fix_allowed=False,
                        summary="Specification/SRS drift indicated by logs.",
                        srs_references=[
                            "FixerAgent SRS: Spec Drift Handling",
                            "Global SRS: Observability & Critical Fault Definitions",
                        ],
                        evidence={
                            "summary_excerpt": excerpt,
                            "impacted_files": impacted_files,
                        },
                    )
                )

        if "artifact" in summary.lower() and "missing" in summary.lower():
            return self._finalize(
                TriageFinding(
                    fault_category=FaultCategory.INFRASTRUCTURE,
                    severity=Severity.CRITICAL,
                    auto_fix_allowed=False,
                    summary="Infrastructure/Artifact fault encountered.",
                    srs_references=["FixerAgent SRS: Fault Taxonomy"],
                    evidence={
                        "summary_excerpt": excerpt,
                        "impacted_files": impacted_files,
                    },
                )
            )

        return self._finalize(
            TriageFinding(
                fault_category=FaultCategory.UNKNOWN,
                severity=Severity.WARNING,
                auto_fix_allowed=False,
                summary="Unable to classify failure deterministically.",
                srs_references=[
                    "FixerAgent SRS: Unknown fault handling",
                    "Global SRS: Observability & Critical Fault Definitions",
                ],
                evidence={
                    "summary_excerpt": excerpt,
                    "impacted_files": impacted_files,
                },
            )
        )

    def _finalize(self, finding: TriageFinding) -> TriageResult:
        return TriageResult(
            fault_category=finding.fault_category,
            severity=finding.severity,
            auto_fix_allowed=finding.auto_fix_allowed,
            summary=finding.summary,
            srs_references=finding.srs_references,
            evidence=finding.evidence,
        )
