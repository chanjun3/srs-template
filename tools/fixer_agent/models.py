from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class FaultCategory(str, Enum):
    INFRASTRUCTURE = "infrastructure_fault"
    CI_CONFIGURATION = "ci_configuration_fault"
    SOURCE_CONTENT = "source_content_fault"
    SPEC_DRIFT = "specification_srs_drift"
    UNKNOWN = "unknown_fault"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class ArtifactBundle:
    run_id: str
    root_path: Path
    ci_summary_path: Path
    ci_summary_text: str
    raw_logs: Dict[str, str] = field(default_factory=dict)


@dataclass
class TriageResult:
    fault_category: FaultCategory
    severity: Severity
    auto_fix_allowed: bool
    summary: str
    srs_references: List[str]
    evidence: Dict[str, object] = field(default_factory=dict)
    blockers: List[str] = field(default_factory=list)


@dataclass
class PatchProposal:
    files_changed: List[Path]
    diff_text: str
    passes_safety_checks: bool
    notes: str


@dataclass
class TriageFinding:
    fault_category: FaultCategory
    severity: Severity
    auto_fix_allowed: bool
    summary: str
    srs_references: List[str]
    evidence: Dict[str, object] = field(default_factory=dict)
