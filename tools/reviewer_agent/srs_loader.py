from __future__ import annotations

from ..fixer_agent.srs_loader import load_srs as base_load_srs, SRSData

__all__ = ["load_srs", "SRSData"]


def load_srs() -> SRSData:
  return base_load_srs()
