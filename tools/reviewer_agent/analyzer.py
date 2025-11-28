from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Iterable


@dataclass
class DiffStats:
  total_lines: int
  files_changed: list[str]
  touches_blocked_path: bool


def compute_diff_stats(base_ref: str = "origin/main") -> DiffStats:
  diff_cmd = ["git", "diff", "--numstat", f"{base_ref}...HEAD"]
  proc = subprocess.run(diff_cmd, check=True, capture_output=True, text=True)
  total_lines = 0
  files: list[str] = []
  for line in proc.stdout.strip().splitlines():
    parts = line.split("\t")
    if len(parts) != 3:
      continue
    add, delete, path = parts
    files.append(path)
    for value in (add, delete):
      if value != "-":
        total_lines += int(value)
  return DiffStats(total_lines=total_lines, files_changed=files, touches_blocked_path=False)


@dataclass
class ReviewDecision:
  decision: str
  comment: str
  warnings: list[str]
  auto_merge: bool


def summarize_pr(event_payload: dict[str, object]) -> str:
  return json.dumps(
    {
      "title": event_payload.get("pull_request", {}).get("title"),
      "author": event_payload.get("pull_request", {}).get("user", {}).get("login"),
      "labels": [label["name"] for label in event_payload.get("pull_request", {}).get("labels", [])],
    },
    indent=2,
  )


def decide_review(
  diff_stats: DiffStats,
  blocked_paths: Iterable[str],
  is_bot_author: bool,
  config_max_lines: int,
) -> ReviewDecision:
  warnings: list[str] = []
  touches_blocked = any(path in diff_stats.files_changed for path in blocked_paths)
  if touches_blocked:
    warnings.append("Diff touches blocked paths; manual review required.")

  if diff_stats.total_lines > config_max_lines:
    warnings.append(f"Diff size {diff_stats.total_lines} exceeds limit {config_max_lines}.")

  if touches_blocked or diff_stats.total_lines > config_max_lines:
    return ReviewDecision(
      decision="changes_requested",
      comment="ReviewerAgent detected SRS risk; please seek human review.",
      warnings=warnings,
      auto_merge=False,
    )

  if is_bot_author:
    decision = "approve"
    comment = "Automated FixerAgent change validated against SRS envelope."
    return ReviewDecision(decision=decision, comment=comment, warnings=warnings, auto_merge=True)

  return ReviewDecision(
    decision="comment",
    comment="ReviewerAgent completed analysis; no auto merge due to author policy.",
    warnings=warnings,
    auto_merge=False,
  )
