from __future__ import annotations

from pathlib import Path

import pytest

from tools.fixer_agent import ArtifactBundle, FaultCategory, TriageEngine
from tools.fixer_agent.models import TriageResult, Severity


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_summary(name: str) -> ArtifactBundle:
    path = FIXTURE_DIR / name
    return ArtifactBundle(
        run_id="run-001",
        root_path=FIXTURE_DIR,
        ci_summary_path=path,
        ci_summary_text=path.read_text(encoding="utf-8"),
        raw_logs={},
    )


@pytest.mark.parametrize(
    "fixture_name,expected_category,auto_fix_expected",
    [
        ("infrastructure_missing_artifact.log", FaultCategory.INFRASTRUCTURE, False),
        ("ci_config_invalid_workflow.log", FaultCategory.CI_CONFIGURATION, False),
        ("source_markdownlint_MD047.log", FaultCategory.SOURCE_CONTENT, None),
        ("source_yamllint_error.log", FaultCategory.SOURCE_CONTENT, None),
        ("source_flake8_E302.log", FaultCategory.SOURCE_CONTENT, None),
        ("spec_drift_detected.log", FaultCategory.SPEC_DRIFT, False),
        ("unknown_unmatched_stacktrace.log", FaultCategory.UNKNOWN, False),
    ],
)
def test_triage_engine_classifications(
    fixture_name: str,
    expected_category: FaultCategory,
    auto_fix_expected: bool | None,
) -> None:
    engine = TriageEngine()
    bundle = load_summary(fixture_name)

    result = engine.classify(bundle)

    assert isinstance(result, TriageResult)
    assert result.fault_category == expected_category
    assert isinstance(result.severity, Severity)
    assert isinstance(result.summary, str) and result.summary
    assert "summary_excerpt" in result.evidence
    assert result.evidence["summary_excerpt"]
    assert "impacted_files" in result.evidence
    assert isinstance(result.evidence["impacted_files"], list)

    if auto_fix_expected is False:
        assert result.auto_fix_allowed is False
    elif auto_fix_expected is True:
        assert result.auto_fix_allowed is True
    else:
        assert isinstance(result.auto_fix_allowed, bool)
