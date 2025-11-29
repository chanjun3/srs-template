from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from .models import ArtifactBundle, FaultCategory, Severity, TriageResult

SUMMARY_FILENAME = "ci-summary.log"
ARTIFACT_NAME = "srs-ci-logs"


class ArtifactLoader:
    """Loads FixerAgent artifacts and enforces Global SRS interface contracts."""

    def __init__(self, run_id: str, log_dir: Path) -> None:
        self.run_id = run_id
        self.log_dir = log_dir

    def _gather_logs(self) -> Dict[str, str]:
        logs: Dict[str, str] = {}
        for path in sorted(self.log_dir.rglob("*")):
            if path.is_dir():
                continue
            suffix = path.suffix.lower()
            if suffix not in {".log", ".txt", ".json"}:
                continue
            if path.name == SUMMARY_FILENAME:
                continue
            try:
                text = path.read_text(encoding="utf-8")
                if suffix == ".json":
                    json.loads(text)
                logs[str(path)] = text
            except (OSError, json.JSONDecodeError):
                continue
        return logs

    def load(self) -> Tuple[Optional[ArtifactBundle], Optional[TriageResult]]:
        if not self.log_dir.exists():
            return (
                None,
                TriageResult(
                    fault_category=FaultCategory.INFRASTRUCTURE,
                    severity=Severity.CRITICAL,
                    auto_fix_allowed=False,
                    summary=f"Artifact '{ARTIFACT_NAME}' directory {self.log_dir} missing.",
                    srs_references=["Global SRS: CIFixerAgent Interface Contract"],
                    evidence={"log_dir": str(self.log_dir)},
                ),
            )

        summary_path = self.log_dir / SUMMARY_FILENAME
        if not summary_path.exists():
            return (
                None,
                TriageResult(
                    fault_category=FaultCategory.INFRASTRUCTURE,
                    severity=Severity.CRITICAL,
                    auto_fix_allowed=False,
                    summary=f"Required file '{SUMMARY_FILENAME}' missing in artifact '{ARTIFACT_NAME}'.",
                    srs_references=["Global SRS: CIFixerAgent Interface Contract"],
                    evidence={"log_dir": str(self.log_dir)},
                ),
            )

        try:
            summary_text = summary_path.read_text(encoding="utf-8")
        except OSError as exc:
            return (
                None,
                TriageResult(
                    fault_category=FaultCategory.INFRASTRUCTURE,
                    severity=Severity.CRITICAL,
                    auto_fix_allowed=False,
                    summary=f"Unable to read ci-summary.log: {exc}",
                    srs_references=["Global SRS: Observability & Critical Fault Definitions"],
                    evidence={"summary_path": str(summary_path)},
                ),
            )

        bundle = ArtifactBundle(
            run_id=self.run_id,
            root_path=self.log_dir,
            ci_summary_path=summary_path,
            ci_summary_text=summary_text,
            raw_logs=self._gather_logs(),
        )
        return bundle, None
