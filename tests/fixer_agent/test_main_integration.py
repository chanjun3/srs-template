from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tools.fixer_agent import main as fixer_main


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _prepare_artifact_dir(tmp_path: Path, fixture_name: str) -> Path:
    artifact_dir = tmp_path / f"artifact_{fixture_name}"
    artifact_dir.mkdir()
    summary_text = (FIXTURE_DIR / fixture_name).read_text(encoding="utf-8")
    (artifact_dir / "ci-summary.log").write_text(summary_text, encoding="utf-8")
    return artifact_dir


def _invoke_runtime(
    monkeypatch: pytest.MonkeyPatch,
    workspace: Path,
    artifact_dir: Path,
    run_id: str,
) -> int:
    monkeypatch.chdir(workspace)
    monkeypatch.setenv("AUTO_FIX_ENABLED", "true")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    argv = [
        "fixer-agent",
        "--ci-workflow",
        "ci-lint",
        "--job-name",
        "lint",
        "--run-id",
        run_id,
        "--branch",
        "main",
        "--log-dir",
        str(artifact_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    return fixer_main.main()


def _load_latest_triage_log(workspace: Path) -> dict:
    log_dir = workspace / "logs" / "fixer_agent"
    log_files = sorted(log_dir.glob("*.json"))
    assert log_files, "FixerAgent did not emit any triage logs."
    with log_files[-1].open(encoding="utf-8") as handle:
        return json.load(handle)


def _run_with_fixture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    fixture_name: str,
    run_id: str,
    setup_workspace=None,
) -> dict:
    artifact_dir = _prepare_artifact_dir(tmp_path, fixture_name)
    workspace = tmp_path / f"workspace_{run_id}"
    workspace.mkdir()
    if setup_workspace:
        setup_workspace(workspace)
    exit_code = _invoke_runtime(monkeypatch, workspace, artifact_dir, run_id)
    assert exit_code == 0
    return _load_latest_triage_log(workspace)


def test_main_integration_infrastructure_no_autofix(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    triage_log = _run_with_fixture(
        monkeypatch,
        tmp_path,
        "infrastructure_missing_artifact.log",
        run_id="infra-run",
    )

    assert triage_log["fault_category"] == "infrastructure_fault"
    assert triage_log["severity"] == "critical"
    assert triage_log["decision"] != "auto_fix"
    assert triage_log["auto_fix_applied"] is False
    assert "patch_proposal" not in triage_log
    assert triage_log["summary"]


def test_main_integration_ci_config_no_autofix(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    triage_log = _run_with_fixture(
        monkeypatch,
        tmp_path,
        "ci_config_invalid_workflow.log",
        run_id="ci-config-run",
    )

    assert triage_log["fault_category"] == "ci_configuration_fault"
    assert triage_log["severity"] == "critical"
    assert triage_log["decision"] != "auto_fix"
    assert triage_log["auto_fix_applied"] is False
    assert "patch_proposal" not in triage_log
    assert triage_log["summary"]


def test_main_integration_spec_drift_no_autofix(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    triage_log = _run_with_fixture(
        monkeypatch,
        tmp_path,
        "spec_drift_detected.log",
        run_id="spec-drift-run",
    )

    assert triage_log["fault_category"] == "specification_srs_drift"
    assert triage_log["severity"] == "warning"
    assert triage_log["decision"] == "triage_only"
    assert triage_log["auto_fix_applied"] is False
    assert "patch_proposal" not in triage_log
    assert triage_log["drift_flag"] is True
    assert triage_log["required_srs_update"] is True
    assert triage_log["summary"]


def test_main_integration_unknown_no_autofix(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    triage_log = _run_with_fixture(
        monkeypatch,
        tmp_path,
        "unknown_unmatched_stacktrace.log",
        run_id="unknown-run",
    )

    assert triage_log["fault_category"] == "unknown_fault"
    assert triage_log["decision"] != "auto_fix"
    assert triage_log["auto_fix_applied"] is False
    assert "patch_proposal" not in triage_log
    assert triage_log["summary"]


def test_main_integration_md047_behaves_consistently(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def setup_md(workspace: Path) -> None:
        (workspace / "README.md").write_text("no newline at end", encoding="utf-8")

    triage_log = _run_with_fixture(
        monkeypatch,
        tmp_path,
        "source_markdownlint_MD047.log",
        run_id="md047-run",
        setup_workspace=setup_md,
    )

    assert triage_log["fault_category"] == "source_content_fault"
    assert triage_log["decision"] == "auto_fix"
    assert triage_log["auto_fix_applied"] is True
    assert triage_log["diff_hash"]
    assert "patch_proposal" in triage_log
    assert triage_log["patch_proposal"]["passes_safety_checks"] is True
    assert triage_log["summary"]


@pytest.mark.parametrize(
    "fixture_name",
    [
        "source_yamllint_error.log",
        "source_flake8_E302.log",
    ],
)
def test_main_integration_source_lints_no_patch_by_default(
    fixture_name: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    triage_log = _run_with_fixture(
        monkeypatch,
        tmp_path,
        fixture_name,
        run_id=f"source-{fixture_name}",
    )

    assert triage_log["fault_category"] == "source_content_fault"
    assert triage_log["decision"] == "triage_only"
    assert triage_log["auto_fix_applied"] is False
    assert "patch_proposal" not in triage_log
    assert triage_log["summary"]
