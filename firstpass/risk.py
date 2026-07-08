"""Risk scoring: turn a list of findings into a single routing decision.

The whole point of the system is here. Contract review is not a reading task,
it is a risk-gating decision. This module encodes the gate.
"""
from __future__ import annotations

from typing import List, Tuple

from .ingest import Document
from .models import Finding, GREEN, AMBER, RED

# How much human time each verdict actually costs, in minutes. These are the
# assumptions behind every ROI number and they are meant to be argued with.
#   GREEN  -> a quick spot-check, the lawyer trusts the auto-clear
#   AMBER  -> confirm the pre-drafted redlines, accept / tweak / reject
#   RED    -> human leads, but starts from extracted terms + flagged issues
FIRSTPASS_MINUTES = {GREEN: 2, AMBER: 8}
RED_MANUAL_FRACTION = 0.6  # RED still needs a human, with a running start


def decide(findings: List[Finding]) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    verdict = GREEN

    if any(f.kind == "red_flag" for f in findings):
        verdict = RED
        reasons.append("Hard escalation trigger present (see red flags).")
    if any(f.kind == "novel_clause" for f in findings):
        verdict = RED
        reasons.append("Contains a clause with no playbook match (novel).")
    if any(f.severity == "high" for f in findings if f.kind != "red_flag"):
        verdict = RED
        reasons.append("A high-severity issue was found.")

    if verdict != RED:
        if findings:
            verdict = AMBER
            reasons.append("Only known, lower-severity deviations: redlines pre-drafted for confirmation.")
        else:
            verdict = GREEN
            reasons.append("Matches standard positions. Auto-clear with a spot-check.")

    return verdict, reasons


def confidence(doc: Document, type_conf: float, verdict: str, findings: List[Finding]) -> float:
    """How sure the system is about its own read of the document.

    Driven by how much of the document it actually recognised. Low recognition
    or an unknown type pulls confidence down and would raise the spot-check rate.
    """
    total = max(1, len(doc.sections))
    novel = sum(1 for f in findings if f.kind == "novel_clause")
    recognised_fraction = (total - novel) / total
    base = 0.55 + 0.4 * recognised_fraction
    base *= 0.6 + 0.4 * type_conf  # penalise weak type classification
    if verdict == RED:
        base = min(base, 0.9)  # we escalate precisely because we are less sure
    return round(min(0.99, base), 2)


def firstpass_minutes(verdict: str, manual_minutes: int) -> int:
    if verdict == RED:
        return int(round(manual_minutes * RED_MANUAL_FRACTION))
    return FIRSTPASS_MINUTES[verdict]
