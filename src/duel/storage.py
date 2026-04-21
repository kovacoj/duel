from __future__ import annotations

import json
import re
from pathlib import Path

from .models import RunArtifact


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "run"


def save_run_artifact(artifact: RunArtifact, output_dir: str | Path) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = artifact.created_at.replace(":", "-").replace("+00-00", "z")
    filename = (
        f"{timestamp}-{artifact.provider}-{_slugify(artifact.model)}-"
        f"{artifact.source['mode']}-{artifact.run_id}.json"
    )
    destination = directory / filename
    destination.write_text(
        json.dumps(artifact.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination
