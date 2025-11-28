from __future__ import annotations

from dataclasses import dataclass, field
import os
import pathlib
from typing import Any

try:
  import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
  import tomli as tomllib  # type: ignore


CONFIG_PATH = pathlib.Path("self_healing_ci.toml")


@dataclass
class SelfHealingConfig:
  auto_fix_enabled: bool = True
  auto_merge_enabled: bool = False
  max_auto_patch_lines: int = 200
  blocked_paths: list[str] = field(default_factory=list)
  log_dir: pathlib.Path = pathlib.Path("logs/fixer_agent")

  @classmethod
  def from_mapping(cls, data: dict[str, Any]) -> "SelfHealingConfig":
    core = data.get("core", {})
    limits = data.get("limits", {})
    return cls(
      auto_fix_enabled=bool(core.get("auto_fix_enabled", True)),
      auto_merge_enabled=bool(core.get("auto_merge_enabled", False)),
      max_auto_patch_lines=int(limits.get("max_auto_patch_lines", 200)),
      blocked_paths=list(limits.get("blocked_paths", [])),
    )

  def ensure_log_dir(self) -> None:
    self.log_dir.mkdir(parents=True, exist_ok=True)


def load_config(path: pathlib.Path | None = None) -> SelfHealingConfig:
  cfg_path = path or CONFIG_PATH
  if not cfg_path.exists():
    return SelfHealingConfig()

  with cfg_path.open("rb") as handle:
    data = tomllib.load(handle)

  cfg = SelfHealingConfig.from_mapping(data)
  env_override = os.getenv("MAX_AUTO_PATCH_LINES")
  if env_override:
    cfg.max_auto_patch_lines = int(env_override)
  return cfg
