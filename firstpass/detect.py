"""Detection: the deterministic, offline reasoning layer.

This is a rules-and-retrieval engine over the playbook. It runs with no network
and no LLM, which is exactly why it is the number we report: it is the FLOOR.
Production plugs the local model in (see :mod:`firstpass.llm`) for semantic clause
matching, which lifts recall on paraphrased clauses the keyword layer misses.
Everything here returns structured ``Finding`` objects so the LLM layer and the
rules layer are interchangeable and comparable.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from .ingest import Document
from .playbook import Playbook
from .models import Finding


def _norm(text: str) -> str:
    """Lower-case and reduce to alphanumerics + single spaces.

    Stripping punctuation on both the text and the patterns is what lets
    '"Confidential Information" means ...' match the keyword
    'confidential information means' despite the quotes.
    """
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text.lower())).strip()


def contains_any(haystack: str, patterns: List[str]) -> Optional[str]:
    """Return the first (original) pattern whose normalised form is present."""
    h = _norm(haystack)
    for pat in patterns:
        if _norm(pat) in h:
            return pat
    return None


def snippet(text: str, pattern: str, width: int = 90) -> str:
    m = re.search(pattern.lower(), text.lower())
    if not m:
        return ""
    start = max(0, m.start() - width // 2)
    end = min(len(text), m.end() + width // 2)
    frag = re.sub(r"\s+", " ", text[start:end]).strip()
    return ("... " if start > 0 else "") + frag + (" ..." if end < len(text) else "")


def classify_type(doc: Document, pb: Playbook) -> tuple[str, str, float]:
    """Pick the contract type with the strongest keyword signal."""
    norm = _norm(doc.text)
    best_key, best_score = "unknown", 0
    for key, tdef in pb.contract_types.items():
        score = sum(1 for kw in tdef.get("detect", []) if _norm(kw) in norm)
        if score > best_score:
            best_key, best_score = key, score
    label = pb.type_def(best_key).get("label", "Unrecognised document") if best_key != "unknown" else "Unrecognised document"
    # crude confidence in the classification itself
    conf = min(1.0, best_score / 2.0) if best_score else 0.0
    return best_key, label, conf


def scan_red_flags(doc: Document, pb: Playbook) -> List[Finding]:
    norm = _norm(doc.text)
    out: List[Finding] = []
    for rf in pb.red_flags:
        hit = contains_any(norm, rf.get("patterns", []))
        if hit:
            out.append(
                Finding(
                    kind="red_flag",
                    clause_id=rf["id"],
                    id=rf["id"],
                    label=rf["label"],
                    severity="high",
                    known=True,
                    redline=None,
                    rationale=rf.get("rationale", ""),
                    evidence=snippet(doc.text, hit),
                )
            )
    return out


def check_clauses(doc: Document, pb: Playbook, type_key: str) -> List[Finding]:
    """Deviation-first clause check.

    For each expected clause: if a known deviation fires, report it (the clause
    exists but is non-standard). Otherwise, if the clause's own keywords are
    present, it is standard: no finding. Otherwise the clause is missing.
    """
    norm = _norm(doc.text)
    out: List[Finding] = []
    tdef = pb.type_def(type_key)
    for clause in tdef.get("clauses", []):
        fired_dev = False
        for dev in clause.get("deviations", []) or []:
            hit = contains_any(norm, dev.get("signal", []))
            if hit:
                fired_dev = True
                out.append(
                    Finding(
                        kind="deviation",
                        clause_id=clause["id"],
                        id=dev["id"],
                        label=dev["label"],
                        severity=dev.get("severity", "medium"),
                        known=bool(dev.get("known", True)),
                        redline=_clean(dev.get("redline")),
                        rationale=dev.get("rationale", ""),
                        evidence=snippet(doc.text, hit),
                    )
                )
        if fired_dev:
            continue
        present = contains_any(norm, clause.get("detect", []))
        if not present:
            sev = clause.get("missing_severity", "medium")
            out.append(
                Finding(
                    kind="missing_clause",
                    clause_id=clause["id"],
                    id=f"{clause['id']}_missing",
                    label=f"Missing: {clause['title']}",
                    severity=sev,
                    known=True,
                    redline=None,
                    rationale=clause.get("missing_note", ""),
                    evidence="",
                )
            )
    return out


def detect_novel(doc: Document, pb: Playbook) -> List[Finding]:
    """Flag section headings we do not recognise as ordinary contract furniture.

    'We have not seen this before' is exactly the signal a human should look at,
    so a novel material clause always escalates.
    """
    recognised = pb.recognised_headings
    red_patterns = [p for rf in pb.red_flags for p in rf.get("patterns", [])]
    out: List[Finding] = []
    for sec in doc.sections:
        h = sec.heading.lower().strip()
        if any(r in h or h in r for r in recognised):
            continue
        # Already escalated for a known reason (e.g. indemnity, non-compete):
        # don't also cry "novel" about the same section.
        if contains_any(sec.body, red_patterns):
            continue
        out.append(
            Finding(
                kind="novel_clause",
                clause_id=f"section_{sec.number}",
                id="novel_material_clause",
                label=f"Novel clause: '{sec.heading}'",
                severity="high",
                known=False,
                redline=None,
                rationale="This clause has no match in the playbook. Escalate to a human, then teach the playbook so it becomes routine next time.",
                evidence=snippet(sec.body, r"\S", width=140) or sec.body[:140],
            )
        )
    return out


def extract_key_terms(doc: Document) -> Dict[str, str]:
    text = doc.text
    terms: Dict[str, str] = {}
    m = re.search(r"between\s+(.+?)\s+and\s+(.+?)[,.\n(]", text, re.IGNORECASE)
    if m:
        terms["parties"] = f"{m.group(1).strip()} / {m.group(2).strip()}"
    m = re.search(r"laws of (?:the )?([A-Za-z ]+?)(?:[.,\n]| and)", text, re.IGNORECASE)
    if m:
        terms["governing_law"] = m.group(1).strip()
    m = re.search(r"(perpetu\w+|(?:one|two|three|four|five|\d+)\s*\(?\d*\)?\s*(?:year|month)s?)", text, re.IGNORECASE)
    if m:
        terms["term"] = m.group(1).strip()
    m = re.search(r"(GBP|USD|£|\$)\s?[\d,]+", text)
    if m:
        terms["value"] = m.group(0).strip()
    m = re.search(r"net\s?(\d+)", text, re.IGNORECASE)
    if m:
        terms["payment"] = f"net {m.group(1)}"
    return terms


def _clean(s: Optional[str]) -> Optional[str]:
    if not s:
        return s
    return re.sub(r"\s+", " ", s).strip()
