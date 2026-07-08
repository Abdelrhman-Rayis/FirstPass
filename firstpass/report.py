"""Human-facing output: a coloured terminal card and a Markdown version.

The terminal card is what a lawyer sees. Everything is pre-chewed: the verdict,
why, the key terms already extracted, and for every issue the exact redline to
accept, tweak or reject. This is the "artefact someone uses on Monday" surface.
"""
from __future__ import annotations

from typing import List

from .models import TriageResult, GREEN, AMBER, RED

_ANSI = {
    GREEN: "\033[42;30m", AMBER: "\033[43;30m", RED: "\033[41;37m",
    "reset": "\033[0m", "dim": "\033[2m", "bold": "\033[1m",
    "sev_high": "\033[31m", "sev_medium": "\033[33m", "sev_low": "\033[36m",
}
_ROUTE = {
    GREEN: "AUTO-CLEAR  (spot-check queue)",
    AMBER: "CONFIRM     (pre-drafted redlines ready)",
    RED: "ESCALATE    (full human review)",
}


def render_terminal(r: TriageResult, color: bool = True) -> str:
    def c(key):
        return _ANSI.get(key, "") if color else ""

    lines: List[str] = []
    bar = c(r.verdict) + f"  {r.verdict}  " + c("reset")
    lines.append("")
    lines.append(f"{bar} {c('bold')}{r.contract_id}{c('reset')}  {c('dim')}({r.type_label}){c('reset')}")
    lines.append(f"  route      : {_ROUTE[r.verdict]}")
    lines.append(f"  confidence : {int(r.confidence * 100)}%   engine: {r.engine}")
    if r.key_terms:
        terms = "   ".join(f"{c('dim')}{k}{c('reset')}={v}" for k, v in r.key_terms.items())
        lines.append(f"  key terms  : {terms}")
    lines.append(f"  time       : ~{r.manual_minutes} min manual  ->  ~{r.firstpass_minutes} min with FirstPass  ({r.minutes_saved} min saved)")

    if not r.findings:
        lines.append(f"  {c('sev_low')}No deviations from standard positions.{c('reset')}")
    for i, f in enumerate(r.findings, 1):
        sev = c(f"sev_{f.severity}")
        tag = {"red_flag": "RED FLAG", "deviation": "DEVIATION", "missing_clause": "MISSING", "novel_clause": "NOVEL"}[f.kind]
        known = "known" if f.known else "NOVEL / unseen"
        lines.append("")
        lines.append(f"  {i}. {sev}[{tag} | {f.severity} | {known}]{c('reset')} {f.label}")
        if f.evidence:
            lines.append(f"     {c('dim')}evidence: “{f.evidence}”{c('reset')}")
        if f.rationale:
            lines.append(f"     why    : {f.rationale}")
        if f.redline:
            lines.append(f"     {c('bold')}redline{c('reset')}: {f.redline}")
    lines.append("")
    return "\n".join(lines)


def render_markdown(r: TriageResult) -> str:
    badge = {GREEN: "🟢 GREEN", AMBER: "🟡 AMBER", RED: "🔴 RED"}[r.verdict]
    out = [f"### {r.contract_id} — {badge}", ""]
    out.append(f"- **Type:** {r.type_label}")
    out.append(f"- **Route:** {_ROUTE[r.verdict]}")
    out.append(f"- **Confidence:** {int(r.confidence * 100)}%  ·  **Engine:** {r.engine}")
    out.append(f"- **Time:** ~{r.manual_minutes} min manual → ~{r.firstpass_minutes} min ({r.minutes_saved} min saved)")
    if r.key_terms:
        out.append("- **Key terms:** " + ", ".join(f"{k}: {v}" for k, v in r.key_terms.items()))
    out.append("")
    if not r.findings:
        out.append("_No deviations from standard positions._")
    for i, f in enumerate(r.findings, 1):
        out.append(f"{i}. **[{f.kind} · {f.severity} · {'known' if f.known else 'novel'}]** {f.label}")
        if f.rationale:
            out.append(f"   - _Why:_ {f.rationale}")
        if f.redline:
            out.append(f"   - _Redline:_ {f.redline}")
    out.append("")
    return "\n".join(out)
