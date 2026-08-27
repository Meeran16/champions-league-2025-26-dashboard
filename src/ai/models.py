from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EvidenceResult:
    question: str
    intent: str
    title: str
    answer: str
    facts: list[dict[str, str]] = field(default_factory=list)
    table: list[dict[str, Any]] = field(default_factory=list)
    scope: str = ""
    caveats: list[str] = field(default_factory=list)
    followups: list[str] = field(default_factory=list)
    chart: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def llm_payload(self, max_rows: int = 12) -> dict[str, Any]:
        """Return a bounded evidence payload suitable for a future LLM prompt."""
        payload = self.to_dict()
        payload["table"] = payload["table"][:max_rows]
        return payload
