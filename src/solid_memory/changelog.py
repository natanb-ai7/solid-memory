from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


@dataclass
class ChangelogEntry:
    source: str
    url: str
    parser_version: str
    status: str
    fetched_at: datetime


class Changelog:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: ChangelogEntry) -> None:
        record: Dict[str, Any] = asdict(entry)
        record["fetched_at"] = entry.fetched_at.astimezone(timezone.utc).isoformat()
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
