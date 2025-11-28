from __future__ import annotations

import datetime as dt
import json
import pathlib
from typing import Any


def write_json_log(log_dir: pathlib.Path, stem: str, payload: dict[str, Any]) -> pathlib.Path:
  timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
  path = log_dir / f"{stem}_{timestamp}.json"
  path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
  return path
