"""Step 8, LEARN: close the loop. This is why FirstPass is a system, not a script.

When a lawyer resolves a RED (a novel clause, or a deviation we had not encoded),
they record the decision here. It is appended to the playbook as a new known
deviation, with the redline they actually used. The next contract carrying that
clause is no longer RED, it is AMBER with the redline pre-drafted.

Every human decision permanently shrinks the future queue. That compounding is
the whole thesis.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from .playbook import DEFAULT_PATH


def record_decision(
    contract_type: str,
    clause_id: str,
    deviation_id: str,
    label: str,
    signal: list[str],
    redline: str,
    rationale: str,
    severity: str = "medium",
    playbook_path: Optional[str] = None,
) -> str:
    """Teach the playbook a new deviation. Returns a human-readable summary."""
    path = Path(playbook_path or DEFAULT_PATH)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    tdef = data["contract_types"][contract_type]
    clause = next((c for c in tdef["clauses"] if c["id"] == clause_id), None)
    if clause is None:
        raise KeyError(f"No clause '{clause_id}' in type '{contract_type}'")

    clause.setdefault("deviations", [])
    if any(d["id"] == deviation_id for d in clause["deviations"]):
        return f"Deviation '{deviation_id}' already known: no change."

    clause["deviations"].append({
        "id": deviation_id,
        "label": label,
        "signal": signal,
        "severity": severity,
        "known": True,
        "redline": redline,
        "rationale": rationale,
    })
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return (
        f"Learned '{deviation_id}' under {contract_type}/{clause_id}. "
        f"Contracts with this clause will now route AMBER with a pre-drafted redline."
    )


def add_signal(
    contract_type: str,
    clause_id: str,
    deviation_id: str,
    new_signals: list[str],
    playbook_path: Optional[str] = None,
) -> str:
    """Teach an EXISTING deviation a new phrasing.

    Used when a lawyer sees the rules layer miss a paraphrase: they add the words
    once, and every future contract that phrases the clause that way is caught.
    """
    path = Path(playbook_path or DEFAULT_PATH)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    clause = next(c for c in data["contract_types"][contract_type]["clauses"] if c["id"] == clause_id)
    dev = next(d for d in clause["deviations"] if d["id"] == deviation_id)
    dev.setdefault("signal", [])
    added = [s for s in new_signals if s not in dev["signal"]]
    dev["signal"].extend(added)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return f"Taught '{deviation_id}' {len(added)} new phrasing(s): {added}"
