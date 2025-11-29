from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Dict, Optional
import hashlib

from .artifact_loader import ArtifactLoader
from .diff_generator import DiffGenerator
from .models import PatchProposal, TriageResult, FaultCategory
from .pr_builder import PRBuilder
from .triage_engine import TriageEngine
from .utils.logging_utils import log_info, log_warning, log_error, write_json_log
from .utils.srs_validator import get_srs_digest

GLOBAL_SRS = Path("docs/spec_os/srs.md")
FIXER_SRS = Path("docs/spec_agents/FixerAgent_SRS.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FixerAgent runtime")
    parser.add_argument("--ci-workflow", required=True)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--log-dir", default="tmp/ci_logs")
    parser.add_argument("--test-command", default="")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _auto_fix_enabled() -> bool:
    return os.getenv("AUTO_FIX_ENABLED", "true").lower() == "true"


def _srs_metadata() -> Dict[str, str]:
    return {
        "global": get_srs_digest(GLOBAL_SRS),
        "fixer": get_srs_digest(FIXER_SRS),
    }


def _triage_from_artifacts(loader: ArtifactLoader) -> TriageResult:
    bundle, fault = loader.load()
    if fault is not None:
        return fault

    engine = TriageEngine()
    return engine.classify(bundle)


def _maybe_generate_patch(
    triage: TriageResult, workspace: Path, dry_run: bool, auto_fix_ready: bool
) -> Optional[PatchProposal]:
    if not auto_fix_ready or dry_run:
        return None
    generator = DiffGenerator()
    return generator.generate_minimal_patch(triage, workspace)


def _build_triage_log(
    args: argparse.Namespace,
    triage: TriageResult,
    patch: Optional[PatchProposal],
    srs_metadata: Dict[str, str],
) -> Dict[str, object]:
    decision = "triage_only"
    if patch and patch.passes_safety_checks and not args.dry_run:
        decision = "auto_fix"
    elif patch and not patch.passes_safety_checks:
        decision = "blocked"

    diff_hash = ""
    if patch and patch.passes_safety_checks:
        diff_hash = hashlib.sha256(patch.diff_text.encode("utf-8")).hexdigest()

    log = {
        "run_id": args.run_id,
        "workflow": args.ci_workflow,
        "job_name": args.job_name,
        "branch": args.branch,
        "fault_category": triage.fault_category.value,
        "severity": triage.severity.value,
        "auto_fix_allowed": triage.auto_fix_allowed,
        "auto_fix_applied": bool(patch and patch.passes_safety_checks and not args.dry_run),
        "summary": triage.summary,
        "srs_references": triage.srs_references,
        "srs_digests": srs_metadata,
        "evidence": triage.evidence,
        "blocked_reasons": triage.blockers,
        "decision": decision,
        "violated_invariants": triage.blockers,
        "rationale": triage.summary,
        "diff_hash": diff_hash,
        "drift_flag": triage.fault_category == FaultCategory.SPEC_DRIFT,
        "required_srs_update": triage.fault_category == FaultCategory.SPEC_DRIFT,
    }
    if patch:
        log["patch_proposal"] = {
            "files_changed": [str(p) for p in patch.files_changed],
            "passes_safety_checks": patch.passes_safety_checks,
            "notes": patch.notes,
        }
        if patch.passes_safety_checks:
            log["patch_proposal"]["diff_text"] = patch.diff_text
    return log


def main() -> int:
    args = parse_args()

    loader = ArtifactLoader(run_id=args.run_id, log_dir=Path(args.log_dir))
    triage = _triage_from_artifacts(loader)

    auto_fix_ready = _auto_fix_enabled() and triage.auto_fix_allowed
    patch = _maybe_generate_patch(triage, Path("."), args.dry_run, auto_fix_ready)

    pr_builder = PRBuilder()
    pr_body = pr_builder.build_pr(args.run_id, triage, patch)

    triage_log = _build_triage_log(args, triage, patch, _srs_metadata())
    triage_log["pr_body"] = pr_body

    log_path = write_json_log(Path("logs") / "fixer_agent", args.run_id, triage_log)

    log_info(
        "FixerAgent triage complete",
        run_id=args.run_id,
        fault_category=triage.fault_category.value,
        severity=triage.severity.value,
        auto_fix_applied=triage_log["auto_fix_applied"],
    )
    if not triage.auto_fix_allowed:
        log_warning("Auto-fix not permitted for this fault.", reason=triage.summary)
    if patch and not patch.passes_safety_checks:
        log_error("Patch failed safety checks", notes=patch.notes)
    log_info("Triage log written", path=str(log_path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
