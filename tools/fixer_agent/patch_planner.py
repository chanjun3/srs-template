from __future__ import annotations

from dataclasses import dataclass

from .classifier import FailureType


@dataclass
class PatchPlan:
  summary: str
  recommended_actions: list[str]
  test_commands: list[str]


def build_patch_plan(failure_type: FailureType, log_snippet: str) -> PatchPlan:
  if failure_type == FailureType.LINT:
    actions = [
      "Run markdownlint locally using `npm run lint:md`.",
      "Fix formatting issues reported by lint tools (Markdown, YAML, Python).",
    ]
    tests = ["npm run lint:md"]
    summary = "Address markdown/YAML/python lint violations detected in CI."
  elif failure_type == FailureType.UNIT_TEST:
    actions = ["Reproduce failing unit tests locally.", "Add targeted fix and regression tests."]
    tests = ["npm test"]
    summary = "Investigate and correct failing unit tests."
  elif failure_type == FailureType.COMPILATION:
    actions = ["Inspect syntax errors reported in logs.", "Apply minimal fixes to failing files."]
    tests = []
    summary = "Resolve compilation or syntax failure."
  elif failure_type == FailureType.INFRA:
    actions = ["Review CI infrastructure status.", "Retry workflow or adjust runner configuration."]
    tests = []
    summary = "CI infrastructure issue detected; requires operator input."
  elif failure_type == FailureType.FLAKY:
    actions = ["Re-run workflow to confirm reproducibility.", "Stabilize flaky tests if reproducible."]
    tests = []
    summary = "Failure appears flaky."
  else:
    actions = ["Inspect CI logs manually.", "Narrow down failing component before patching."]
    tests = []
    summary = "Unclassified failure; manual triage required."

  snippet = log_snippet.strip()
  if snippet:
    actions.append(f"Relevant log excerpt: {snippet[:240]}")

  return PatchPlan(summary=summary, recommended_actions=actions, test_commands=tests)
