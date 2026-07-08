"""The agentic loop: ingest -> classify -> retrieve -> detect -> score -> draft
-> route. One contract in, one routed, explained, redlined decision out.

    1. INGEST      read the file, split into clauses
    2. CLASSIFY    what kind of contract is this, and pull key commercial terms
    3. RETRIEVE    load the playbook positions for this contract type
    4. DETECT      red flags, deviations from standard, missing clauses, novelty
    5. SCORE       roll findings into GREEN / AMBER / RED + a confidence
    6. DRAFT       attach the previously-used redline to each known deviation
    7. ROUTE       auto-clear, send with pre-drafted redlines, or escalate

Step 8, LEARN, closes the loop across contracts and lives in ``learn.py``: a
human decision on a RED becomes a playbook entry, so next time it is AMBER.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from . import detect, risk
from .ingest import load as load_doc
from .models import Finding, TriageResult  # re-exported for convenience
from .playbook import Playbook, load as load_playbook


def triage_contract(
    path: str,
    pb: Optional[Playbook] = None,
    llm=None,
) -> TriageResult:
    pb = pb or load_playbook()

    # 1. INGEST
    doc = load_doc(path)

    # 2. CLASSIFY
    type_key, type_label, type_conf = detect.classify_type(doc, pb)
    key_terms = detect.extract_key_terms(doc)

    # 3. RETRIEVE  (implicit: pb.type_def(type_key), used inside detect)
    # 4. DETECT
    findings: List[Finding] = []
    findings += detect.scan_red_flags(doc, pb)
    findings += detect.check_clauses(doc, pb, type_key)
    findings += detect.detect_novel(doc, pb)

    # 4b. (optional) lift recall with the local model on anything the rules
    #     layer left unmatched. No-op unless a key is present; keeps the demo
    #     reproducible.
    if llm is not None and llm.available():  # pragma: no cover
        findings = _augment_with_llm(doc, pb, type_key, findings, llm)

    # 5. SCORE
    verdict, reasons = risk.decide(findings)
    conf = risk.confidence(doc, type_conf, verdict, findings)

    # 6. DRAFT is already done: known deviations carry their redline from the
    #    playbook. (The LLM path drafts bespoke language for near-misses.)

    # 7. ROUTE + timing model
    manual = int(pb.type_def(type_key).get("typical_manual_minutes", 30))
    fp_minutes = risk.firstpass_minutes(verdict, manual)

    return TriageResult(
        contract_id=Path(path).stem,
        path=str(path),
        contract_type=type_key,
        type_label=type_label,
        verdict=verdict,
        confidence=conf,
        reasons=reasons,
        key_terms=key_terms,
        findings=findings,
        manual_minutes=manual,
        firstpass_minutes=fp_minutes,
        engine="local-model" if (llm is not None and llm.available()) else "deterministic",
    )


def triage_queue(paths: List[str], pb: Optional[Playbook] = None, llm=None) -> List[TriageResult]:
    pb = pb or load_playbook()
    return [triage_contract(p, pb=pb, llm=llm) for p in paths]


def _augment_with_llm(doc, pb, type_key, findings, llm):  # pragma: no cover
    """Give the local model the clauses the rules layer did not flag and let it
    catch paraphrased deviations. Only adds findings; never removes a rules hit."""
    seen = {f.clause_id for f in findings}
    for clause in pb.type_def(type_key).get("clauses", []):
        if clause["id"] in seen or not clause.get("deviations"):
            continue
        section_text = doc.text
        match = llm.semantic_match(section_text, clause["deviations"])
        if match:
            findings.append(
                Finding(
                    kind="deviation",
                    clause_id=clause["id"],
                    id=match["id"],
                    label=match["label"] + " (semantic match)",
                    severity=match.get("severity", "medium"),
                    known=True,
                    redline=match.get("redline"),
                    rationale=match.get("rationale", ""),
                    evidence="matched by local-model semantic layer",
                )
            )
    return findings
