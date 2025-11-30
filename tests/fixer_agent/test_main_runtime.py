from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tools.fixer_agent import main as fixer_main


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _prepare_artifacts(tmp_path: Path, fixture_name: str) -> Path:
    log_dir = tmp_path / "ci_artifacts"
    log_dir.mkdir()
    summary_text = (FIXTURE_DIR / fixture_name).read_text(encoding="utf-8")
    (log_dir / "ci-summary.log").write_text(summary_text, encoding="utf-8")
    return log_dir


def _invoke_cli(monkeypatch: pytest.MonkeyPatch, workspace: Path, log_dir: Path, run_id: str) -> int:
    monkeypatch.chdir(workspace)
    monkeypatch.setenv("AUTO_FIX_ENABLED", "true")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    argv = [
        "fixer-agent",
        "--ci-workflow",
        "ci-lint",
        "--job-name",
        "markdownlint",
        "--run-id",
        run_id,
        "--branch",
        "main",
        "--log-dir",
        str(log_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    return fixer_main.main()


def _load_latest_log(workspace: Path) -> dict:
    log_root = workspace / "logs" / "fixer_agent"
    log_files = sorted(log_root.glob("*.json"))
    assert log_files, "Expected FixerAgent to emit triage logs."
    with log_files[-1].open(encoding="utf-8") as handle:
        return json.load(handle)


def test_main_runtime_applies_auto_fix_and_emits_patch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    log_dir = _prepare_artifacts(tmp_path, "source_markdownlint_MD047.log")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("content missing newline", encoding="utf-8")

    exit_code = _invoke_cli(monkeypatch, workspace, log_dir, run_id="run-auto-fix")

    assert exit_code == 0
    triage_log = _load_latest_log(workspace)
    assert triage_log["run_id"] == "run-auto-fix"
    assert triage_log["decision"] == "auto_fix"
    assert triage_log["auto_fix_applied"] is True
    assert triage_log["diff_hash"]
    patch = triage_log["patch_proposal"]
    assert patch["passes_safety_checks"] is True
    assert Path(patch["files_changed"][0]).name == "README.md"
    assert patch["diff_text"].startswith("*** Begin Patch")
    assert triage_log["pr_body"].startswith("## FixerAgent Review")
    assert "Proposed Minimal Patch" in triage_log["pr_body"]
    assert "```diff" in triage_log["pr_body"]


def test_main_runtime_triage_only_when_spec_drift_detected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    log_dir = _prepare_artifacts(tmp_path, "spec_drift_detected.log")
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    exit_code = _invoke_cli(monkeypatch, workspace, log_dir, run_id="run-spec-drift")

    assert exit_code == 0
    triage_log = _load_latest_log(workspace)
    assert triage_log["run_id"] == "run-spec-drift"
    assert triage_log["decision"] == "triage_only"
    assert triage_log["auto_fix_applied"] is False
    assert "patch_proposal" not in triage_log
    assert triage_log["drift_flag"] is True
    assert triage_log["required_srs_update"] is True
    assert "Auto-fix was not attempted" in triage_log["pr_body"]


def test_main_runtime_handles_missing_artifacts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    missing_log_dir = tmp_path / "missing_artifacts"

    exit_code = _invoke_cli(monkeypatch, workspace, missing_log_dir, run_id="run-missing-artifact")

    assert exit_code == 0
    triage_log = _load_latest_log(workspace)
    assert triage_log["run_id"] == "run-missing-artifact"
    assert triage_log["fault_category"] == "infrastructure_fault"
    assert triage_log["severity"] == "critical"
    assert triage_log["decision"] == "triage_only"
    assert triage_log["auto_fix_applied"] is False
    assert triage_log["blocked_reasons"] == []
    assert "patch_proposal" not in triage_log
    assert "Auto-fix was not attempted" in triage_log["pr_body"]


@pytest.mark.parametrize(
    "fixture_name,run_id,expected_category,expected_severity",
    [
        ("infrastructure_missing_artifact.log", "run-infra", "infrastructure_fault", "critical"),
        ("ci_config_invalid_workflow.log", "run-ci-config", "ci_configuration_fault", "critical"),
        ("spec_drift_detected.log", "run-spec-drift-fixture", "specification_srs_drift", "warning"),
        ("unknown_unmatched_stacktrace.log", "run-unknown", "unknown_fault", "warning"),
    ],
)
def test_main_runtime_triage_only_for_non_source_faults(
    fixture_name: str,
    run_id: str,
    expected_category: str,
    expected_severity: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    log_dir = _prepare_artifacts(tmp_path, fixture_name)
    workspace = tmp_path / f"workspace-{run_id}"
    workspace.mkdir()

    exit_code = _invoke_cli(monkeypatch, workspace, log_dir, run_id=run_id)

    assert exit_code == 0
    triage_log = _load_latest_log(workspace)
    assert triage_log["run_id"] == run_id
    assert triage_log["fault_category"] == expected_category
    assert triage_log["severity"] == expected_severity
    assert triage_log["decision"] != "auto_fix"
    assert triage_log["auto_fix_applied"] is False
    assert triage_log.get("patch_proposal") is None
    assert not triage_log.get("diff_hash")
    assert triage_log["pr_body"].startswith("## FixerAgent Review")
