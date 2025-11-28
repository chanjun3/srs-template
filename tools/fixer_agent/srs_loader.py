from __future__ import annotations

import hashlib
import pathlib
from dataclasses import dataclass


SRS_ROOT = pathlib.Path("docs/spec_os/srs.md")


@dataclass
class SRSData:
  path: pathlib.Path
  content: str
  sha256: str


def load_srs(path: pathlib.Path | None = None) -> SRSData:
  srs_path = path or SRS_ROOT
  content = srs_path.read_text(encoding="utf-8")
  digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
  return SRSData(path=srs_path, content=content, sha256=digest)
