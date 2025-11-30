from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(PROJECT_ROOT))

from tools.reviewer_agent.analyzer import compute_diff_stats, decide_review, summarize_pr
from tools.reviewer_agent.config import load_config
from tools.reviewer_agent.srs_loader import load_srs
from tools.fixer_agent.log_utils import write_json_log


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="ReviewerAgent - automated PR review")
  parser.add_argument("--event-path", required=True, help="Path to pull_request event payload.")
  parser.add_argument("--base-ref", default="origin/main", help="Base reference for diff computation.")
  parser.add_argument("--bot-author", default="FixerAgent", help="Bot author name for auto approvals.")
  parser.add_argument("--dry-run", action="store_true", help="Do not attempt merge operations.")
  return parser.parse_args()


def load_event(path: pathlib.Path) -> dict[str, object]:
  content = path.read_text(encoding="utf-8")
  return json.loads(content)


def main() -> int:
  args = parse_args()
  cfg = load_config()
  srs = load_srs()
  event = load_event(pathlib.Path(args.event_path))

  diff_stats = compute_diff_stats(base_ref=args.base_ref)
  pr_info = event.get("pull_request", {})
  author = pr_info.get("user", {}).get("login", "")
  is_bot_author = isinstance(author, str) and args.bot_author.lower() in author.lower()

  decision = decide_review(
    diff_stats=diff_stats,
    blocked_paths=cfg.blocked_paths,
    is_bot_author=is_bot_author,
    config_max_lines=cfg.max_auto_patch_lines,
  )

  payload = {
    "diff_lines": diff_stats.total_lines,
    "files_changed": diff_stats.files_changed,
    "warnings": decision.warnings,
    "decision": decision.decision,
    "auto_merge": decision.auto_merge and cfg.auto_merge_enabled and not args.dry_run,
    "srs_sha256": srs.sha256,
    "pr_summary": summarize_pr(event),
  }
  log_path = write_json_log(cfg.log_dir, f"reviewer_agent_{pr_info.get('number', 'unknown')}", payload)
  print(f"ReviewerAgent decision recorded at {log_path}")
  print(f"Decision: {decision.decision}")
  for warning in decision.warnings:
    print(f"Warning: {warning}")

  if decision.auto_merge and cfg.auto_merge_enabled and not args.dry_run:
    print("Auto-merge would be executed here (GH CLI/API).")

  return 0


if __name__ == "__main__":
  sys.exit(main())
