from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Iterable, Optional

CI_ALLOWED_EXTENSIONS = {".md", ".markdown", ".yml", ".yaml", ".json", ".py", ".txt"}
TAB_PATTERN = re.compile(r"\t")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:  # pragma: no cover - binary path
        while chunk := handle.read(8192):
            digest.update(chunk)
    return digest.hexdigest()


def get_srs_digest(path: Path) -> str:
    if not path.exists():
        return "missing"
    return sha256_file(path)


def validate_patch_scope(patch_text: str, impacted_files: Iterable[Path]) -> Optional[str]:
    if TAB_PATTERN.search(patch_text):
        return "Patch contains TAB characters, violating CI Syntax Invariants."

    for path in impacted_files:
        if path.suffix.lower() not in CI_ALLOWED_EXTENSIONS:
            return f"File '{path}' is outside FixerAgent's allowed scope."
        normalized = path.as_posix()
        if normalized.startswith("../") or normalized.startswith("/"):
            return "Patch references paths outside the repository workspace."
    return None
