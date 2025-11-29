from __future__ import annotations

from pathlib import Path

import pytest

from tools.fixer_agent import ArtifactBundle, TriageEngine
from tools.fixer_agent.diff_generator import DiffGenerator
from tools.fixer_agent.models import FaultCategory, TriageResult


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_bundle(name: str) -> ArtifactBundle:
    path = FIXTURE_DIR / name
    return ArtifactBundle(
        run_id="test-run",
        root_path=FIXTURE_DIR,
        ci_summary_path=path,
        ci_summary_text=path.read_text(encoding="utf-8"),
        raw_logs={},
    )


def triage_from_fixture(engine: TriageEngine, fixture_name: str) -> TriageResult:
    return engine.classify(load_bundle(fixture_name))


@pytest.fixture(scope="module")
def triage_engine() -> TriageEngine:
    return TriageEngine()


def test_diff_generator_md047_creates_minimal_patch(tmp_path: Path, triage_engine: TriageEngine) -> None:
    workspace = tmp_path
    target_file = workspace / "README.md"
    target_file.write_text("Content without trailing newline", encoding="utf-8")

    triage = triage_from_fixture(triage_engine, "source_markdownlint_MD047.log")
    diff_gen = DiffGenerator()

    proposal = diff_gen.generate_minimal_patch(triage, workspace)

    assert proposal is not None
    assert proposal.passes_safety_checks is True
    assert proposal.files_changed == [workspace / "README.md"]
    assert proposal.diff_text.startswith("*** Begin Patch")
    assert "README.md" in proposal.diff_text
    assert "\t" not in proposal.diff_text
    assert proposal.diff_text.encode("ascii")


@pytest.mark.parametrize(
    "fixture_name,expected_category",
    [
        ("infrastructure_missing_artifact.log", FaultCategory.INFRASTRUCTURE),
        ("ci_config_invalid_workflow.log", FaultCategory.CI_CONFIGURATION),
        ("spec_drift_detected.log", FaultCategory.SPEC_DRIFT),
        ("unknown_unmatched_stacktrace.log", FaultCategory.UNKNOWN),
    ],
)
def test_diff_generator_no_patch_for_non_source_faults(
    fixture_name: str,
    expected_category: FaultCategory,
    tmp_path: Path,
    triage_engine: TriageEngine,
) -> None:
    (tmp_path / "README.md").write_text("content\n", encoding="utf-8")
    triage = triage_from_fixture(triage_engine, fixture_name)
    assert triage.fault_category == expected_category

    diff_gen = DiffGenerator()
    proposal = diff_gen.generate_minimal_patch(triage, tmp_path)

    assert proposal is None


@pytest.mark.parametrize(
    "fixture_name",
    [
        "source_yamllint_error.log",
        "source_flake8_E302.log",
    ],
)
def test_diff_generator_no_patch_for_other_source_faults(
    fixture_name: str,
    tmp_path: Path,
    triage_engine: TriageEngine,
) -> None:
    (tmp_path / "README.md").write_text("content\n", encoding="utf-8")
    triage = triage_from_fixture(triage_engine, fixture_name)

    diff_gen = DiffGenerator()
    proposal = diff_gen.generate_minimal_patch(triage, tmp_path)

    assert proposal is None
