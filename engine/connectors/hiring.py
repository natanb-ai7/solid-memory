from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HiringSignalsStub:
    """Stub connector for hiring signals."""

    def fetch(self, company: str) -> dict:
        return {
            "company": company,
            "hiring_change_30d": None,
            "note": "Manual input required.",
        }
