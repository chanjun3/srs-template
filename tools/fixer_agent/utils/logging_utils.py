from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json_log(log_dir: Path, stem: str, data: Dict[str, Any]) -> Path:
    _ensure_dir(log_dir)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = log_dir / f"{stem}_{timestamp}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
    return path


def _emit(level: str, message: str, **fields: Any) -> None:
    payload = {"timestamp": datetime.now(tz=timezone.utc).isoformat(), "level": level, "message": message}
    if fields:
        payload["fields"] = fields
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")


def log_info(message: str, **fields: Any) -> None:
    _emit("INFO", message, **fields)


def log_warning(message: str, **fields: Any) -> None:
    _emit("WARNING", message, **fields)


def log_error(message: str, **fields: Any) -> None:
    _emit("ERROR", message, **fields)
