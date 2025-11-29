from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .models import PatchProposal, TriageResult
from .utils.srs_validator import validate_patch_scope

MD047_PATTERN = re.compile(r"MD047|no newline at end of file", re.IGNORECASE)
FILE_LINE_PATTERN = re.compile(
    r"(?P<file>[^\s:]+?\.(?:md|markdown|rst|txt)):(?P<line>\d+)", re.IGNORECASE
)


@dataclass
class DiffGenerator:
    """Produces minimal diffs that respect FixerAgent SRS constraints."""

    max_diff_lines: int = 20

    def generate_minimal_patch(
        self, triage: TriageResult, workspace: Path
    ) -> Optional[PatchProposal]:
        if not triage.auto_fix_allowed:
            return None

        summary_excerpt = triage.evidence.get("summary_excerpt", "")
        if not MD047_PATTERN.search(summary_excerpt):
            return None

        match = FILE_LINE_PATTERN.search(summary_excerpt)
        if not match:
            return None

        candidate = workspace / match.group("file")
        patch_text = self._ensure_newline(candidate)
        if patch_text is None:
            return None

        validation_error = validate_patch_scope(patch_text, [candidate])
        if validation_error:
            return PatchProposal(
                files_changed=[],
                diff_text="",
                passes_safety_checks=False,
                notes=validation_error,
            )

        return PatchProposal(
            files_changed=[candidate],
            diff_text=patch_text,
            passes_safety_checks=True,
            notes="Ensure newline at EOF (MD047).",
        )

    def _ensure_newline(self, path: Path) -> Optional[str]:
        try:
            data = path.read_text(encoding="utf-8")
        except OSError:
            return None
        if data.endswith("\n"):
            return None
        new_data = data + "\n"
        return (
            f"*** Begin Patch\n*** Update File: {path}\n@@\n-{data[-50:]}\n+{new_data[-50:]}\n*** End Patch"
        )
