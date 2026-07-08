"""Shared data structures for the triage pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

# Verdicts, in ascending order of "a human must look at this".
GREEN = "GREEN"   # standard: auto-clear with a spot-check, never auto-signed
AMBER = "AMBER"   # known deviations, redlines pre-drafted, lawyer confirms
RED = "RED"       # novel or high-risk, escalate for full human review


@dataclass
class Finding:
    kind: str            # red_flag | deviation | missing_clause | novel_clause
    clause_id: str
    id: str
    label: str
    severity: str        # low | medium | high
    known: bool          # have we seen and encoded this before?
    redline: Optional[str]
    rationale: str
    evidence: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TriageResult:
    contract_id: str
    path: str
    contract_type: str
    type_label: str
    verdict: str
    confidence: float
    reasons: List[str]
    key_terms: Dict[str, str]
    findings: List[Finding] = field(default_factory=list)
    manual_minutes: int = 0
    firstpass_minutes: int = 0
    engine: str = "deterministic"

    @property
    def minutes_saved(self) -> int:
        return max(0, self.manual_minutes - self.firstpass_minutes)

    @property
    def known_issue_ids(self) -> List[str]:
        return [f.id for f in self.findings]

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["minutes_saved"] = self.minutes_saved
        return d
