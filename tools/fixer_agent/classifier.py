from __future__ import annotations

from enum import Enum


class FailureType(str, Enum):
  LINT = "lint"
  COMPILATION = "compilation"
  UNIT_TEST = "unit_test"
  INTEGRATION_TEST = "integration_test"
  INFRA = "infra"
  FLAKY = "flaky"
  UNKNOWN = "unknown"


KEYWORDS = {
  FailureType.LINT: ["lint", "markdownlint", "yamllint", "flake8", "black"],
  FailureType.COMPILATION: ["compile", "compilation", "syntax error"],
  FailureType.UNIT_TEST: ["pytest", "unittest", "assert", "FAIL:", "AssertionError"],
  FailureType.INTEGRATION_TEST: ["integration", "e2e", "end-to-end"],
  FailureType.INFRA: ["timeout", "network", "permissions", "infrastructure"],
  FailureType.FLAKY: ["flaky", "rerun"],
}


def classify_failure(log_text: str) -> FailureType:
  lower = log_text.lower()
  for failure_type, markers in KEYWORDS.items():
    for marker in markers:
      if marker.lower() in lower:
        return failure_type
  return FailureType.UNKNOWN
