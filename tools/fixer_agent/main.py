from __future__ import annotations

import argparse
import os
import pathlib
import sys
from datetime import datetime

from .classifier import classify_failure
from .config import SelfHealingConfig, load_config
from .log_utils import write_json_log
from .patch_planner import build_patch_plan
from .srs_loader import load_srs


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="FixerAgent - self-healing CI helper")
  parser.add_argument("--ci-workflow", required=True, help="Name of the failed workflow.")
  parser.add_argument("--job-name", required=True, help="Name of the failed CI job.")
  parser.add_argument("--run-id", required=True, help="GitHub workflow run id.")
  parser.add_argument("--branch", required=True, help="Branch where the failure occurred.")
  parser.add_argument("--log-dir", default="tmp/ci_logs", help="Directory containing downloaded CI logs.")
  parser.add_argument("--test-command", default="", help="Suggested command to re-run locally.")
  parser.add_argument("--dry-run", action="store_true", help="Only record triage data without proposing a patch.")
  return parser.parse_args()


def read_logs(log_dir: pathlib.Path, max_chars: int = 20000) -> str:
  if not log_dir.exists():
    return ""
  content_parts: list[str] = []
  for file in sorted(log_dir.rglob("*.txt")):
    content = file.read_text(encoding="utf-8", errors="ignore")
    content_parts.append(content)
    if sum(len(part) for part in content_parts) >= max_chars:
      break
  return "\n\n".join(content_parts)[:max_chars]


def main() -> int:
  args = parse_args()
  cfg = load_config()
  cfg.ensure_log_dir()

  if not cfg.auto_fix_enabled:
    print("Auto-fix disabled via configuration; exiting.")
    return 0

  log_dir = pathlib.Path(args.log_dir)
  log_text = read_logs(log_dir)
  failure_type = classify_failure(log_text)
  snippet = log_text[-1000:] if log_text else ""
  patch_plan = build_patch_plan(failure_type, snippet)
  srs_data = load_srs()

  branch_name = f"auto/fix/{failure_type.value}/{args.run_id}"
  pr_title = "[FixerAgent] Auto-fix CI failure"
  triage = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "ci_workflow": args.ci_workflow,
    "job_name": args.job_name,
    "branch": args.branch,
    "run_id": args.run_id,
    "failure_type": failure_type.value,
    "patch_plan": {
      "summary": patch_plan.summary,
      "recommended_actions": patch_plan.recommended_actions,
      "test_commands": patch_plan.test_commands,
    },
    "proposed_branch": branch_name,
    "pr_title": pr_title,
    "srs_sha256": srs_data.sha256,
    "srs_path": str(srs_data.path),
    "dry_run": args.dry_run,
    "max_auto_patch_lines": cfg.max_auto_patch_lines,
    "blocked_paths": cfg.blocked_paths,
    "test_command_override": args.test_command,
  }

  log_path = write_json_log(cfg.log_dir, f"fixer_agent_{args.run_id}", triage)
  print(f"FixerAgent triage recorded at {log_path}")
  print(f"Failure classified as {failure_type.value}. Suggested branch: {branch_name}")
  print(f"Recommended actions:\n- " + "\n- ".join(patch_plan.recommended_actions))
  if args.dry_run:
    print("Dry-run mode enabled; no patch was generated.")

  return 0


if __name__ == "__main__":
  sys.exit(main())
