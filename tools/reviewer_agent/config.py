from __future__ import annotations

from dataclasses import dataclass
import pathlib
from typing import Any

from ..fixer_agent.config import SelfHealingConfig, load_config as load_base_config


@dataclass
class ReviewerConfig(SelfHealingConfig):
  log_dir: pathlib.Path = pathlib.Path("logs/reviewer_agent")

  def ensure_log_dir(self) -> None:  # type: ignore[override]
    self.log_dir.mkdir(parents=True, exist_ok=True)


def load_config() -> ReviewerConfig:
  base = load_base_config()
  cfg = ReviewerConfig(
    auto_fix_enabled=base.auto_fix_enabled,
    auto_merge_enabled=base.auto_merge_enabled,
    max_auto_patch_lines=base.max_auto_patch_lines,
    blocked_paths=base.blocked_paths,
  )
  cfg.ensure_log_dir()
  return cfg
