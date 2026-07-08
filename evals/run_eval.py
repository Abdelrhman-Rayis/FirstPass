#!/usr/bin/env python3
"""Evaluate FirstPass against the gold labels and write evals/results.md.

Three questions, the ones that matter for a legal team:

  1. Is it SAFE?      Does anything that should be escalated (RED) slip through
                      as auto-clear or confirm? This is the only error that can
                      actually hurt you. We report it separately and it must be 0.
  2. Is it ACCURATE?  Triage-verdict accuracy, and material-issue precision/recall.
  3. Is it WORTH IT?  Human minutes with vs without FirstPass, and the monthly
                      extrapolation.

Everything here runs on the deterministic (offline, no-LLM) engine, so the
numbers are the floor and are fully reproducible: `python evals/run_eval.py`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from firstpass import triage  # noqa: E402
from firstpass.models import GREEN, AMBER, RED  # noqa: E402
from firstpass.playbook import load as load_playbook  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GOLD = yaml.safe_load((ROOT / "evals" / "gold.yaml").read_text())
VERDICTS = [GREEN, AMBER, RED]


def is_material(f) -> bool:
    if f.kind in ("red_flag", "deviation", "novel_clause"):
        return True
    if f.kind == "missing_clause" and f.severity == "high":
        return True
    return False


def main():
    pb = load_playbook()
    rows = []
    confusion = {a: {b: 0 for b in VERDICTS} for a in VERDICTS}
    tp = fp = fn = 0
    unsafe = []          # gold RED, predicted not RED  (the dangerous miss)
    manual_total = fp_total = 0

    for cid, g in GOLD.items():
        r = triage.triage_contract(str(ROOT / "contracts" / f"{cid}.txt"), pb=pb)
        gold_v, pred_v = g["verdict"], r.verdict
        confusion[gold_v][pred_v] += 1
        if gold_v == RED and pred_v != RED:
            unsafe.append(cid)

        gold_issues = set(g.get("issues", []))
        pred_issues = {f.id for f in r.findings if is_material(f)}
        c_tp = len(gold_issues & pred_issues)
        c_fp = len(pred_issues - gold_issues)
        c_fn = len(gold_issues - pred_issues)
        tp += c_tp; fp += c_fp; fn += c_fn

        manual_total += g["manual_minutes"]
        # recompute firstpass minutes against the GOLD manual time for a fair model
        from firstpass.risk import firstpass_minutes
        fp_min = firstpass_minutes(pred_v, g["manual_minutes"])
        fp_total += fp_min

        rows.append((cid, gold_v, pred_v, "OK" if gold_v == pred_v else "MISS",
                     sorted(gold_issues), sorted(pred_issues), c_fp, c_fn))

    n = len(GOLD)
    verdict_acc = sum(confusion[v][v] for v in VERDICTS) / n
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    saved = manual_total - fp_total
    saved_pct = saved / manual_total

    # ---- monthly extrapolation (stated assumptions, easy to argue with) ----
    monthly_volume = 200
    scale = monthly_volume / n
    monthly_manual_h = manual_total * scale / 60
    monthly_fp_h = fp_total * scale / 60
    monthly_saved_h = monthly_manual_h - monthly_fp_h

    md = _render_md(rows, confusion, verdict_acc, precision, recall, f1, unsafe,
                    manual_total, fp_total, saved, saved_pct, n,
                    monthly_volume, monthly_manual_h, monthly_fp_h, monthly_saved_h)
    (ROOT / "evals" / "results.md").write_text(md, encoding="utf-8")

    # ---- console summary ----
    print("=" * 60)
    print("FIRSTPASS EVAL  (deterministic engine, offline)")
    print("=" * 60)
    print(f"Contracts              : {n}")
    print(f"Triage verdict accuracy: {verdict_acc:.0%}  ({sum(confusion[v][v] for v in VERDICTS)}/{n})")
    print(f"Unsafe escalation miss : {len(unsafe)}   (gold RED routed as non-RED)  <- must be 0")
    print(f"Issue precision / recall: {precision:.0%} / {recall:.0%}   (F1 {f1:.0%})")
    print(f"Human time             : {manual_total} min  ->  {fp_total} min  ({saved} saved, {saved_pct:.0%})")
    print(f"Extrapolated @ {monthly_volume}/mo  : {monthly_manual_h:.0f}h  ->  {monthly_fp_h:.0f}h "
          f"({monthly_saved_h:.0f}h/month saved)")
    print("=" * 60)
    print(f"Full report written to evals/results.md")


def _render_md(rows, confusion, acc, prec, rec, f1, unsafe, manual, fpt, saved,
               saved_pct, n, mvol, mman, mfp, msav):
    L = ["# FirstPass evaluation results", "",
         "_Deterministic engine, run fully offline. These are the floor; the "
         "local-model semantic layer lifts issue recall further._", "",
         "## 1. Is it safe?", ""]
    if unsafe:
        L.append(f"**{len(unsafe)} unsafe miss(es):** {', '.join(unsafe)} were escalation-worthy but not routed RED.")
    else:
        L.append("**0 unsafe misses.** Every contract that a lawyer would escalate was routed RED. "
                 "No high-risk contract was auto-cleared. This is the metric that matters most.")
    L += ["", "## 2. Is it accurate?", "",
          f"- **Triage verdict accuracy:** {acc:.0%} ({sum(confusion[v][v] for v in VERDICTS)}/{n})",
          f"- **Material-issue precision:** {prec:.0%}",
          f"- **Material-issue recall:** {rec:.0%}",
          f"- **F1:** {f1:.0%}", "",
          "### Triage confusion matrix (rows = gold, cols = predicted)", "",
          "| gold \\ pred | GREEN | AMBER | RED |", "|---|---|---|---|"]
    for a in VERDICTS:
        L.append(f"| **{a}** | {confusion[a][GREEN]} | {confusion[a][AMBER]} | {confusion[a][RED]} |")
    L += ["", "### Per-contract detail", "",
          "| contract | gold | pred | | gold issues | predicted (material) | FP | FN |",
          "|---|---|---|---|---|---|---|---|"]
    for cid, gv, pv, ok, gi, pi, cfp, cfn in rows:
        L.append(f"| {cid} | {gv} | {pv} | {ok} | {', '.join(gi) or '-'} | {', '.join(pi) or '-'} | {cfp} | {cfn} |")
    L += ["", "## 3. Is it worth it?", "",
          f"- Human review time on the {n}-contract set: **{manual} min → {fpt} min** "
          f"(**{saved} min saved, {saved_pct:.0%}**).",
          f"- Extrapolated to **{mvol} contracts/month** (same mix): "
          f"**{mman:.0f}h → {mfp:.0f}h**, about **{msav:.0f} hours/month** of legal time returned.",
          "",
          "_Assumptions: manual minutes per contract are in `gold.yaml`; FirstPass "
          "minutes are 2 (GREEN spot-check), 8 (AMBER confirm redlines), 60% of manual "
          "(RED, human-led with a running start). The monthly figure assumes the same "
          "GREEN/AMBER/RED mix at 200 contracts/month; the real number comes from a "
          "2-week measured sprint, not this model._", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
