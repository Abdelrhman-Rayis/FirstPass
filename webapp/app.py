#!/usr/bin/env python3
"""FirstPass web console.

A local, single-process Flask app that runs the same triage engine as the CLI
and presents it as the queue a lawyer would actually work from. Nothing leaves
the machine: the engine is offline, and the optional reasoning layer is an
on-prem local model (see firstpass/llm.py). Designed to be hosted on the
institution's own server.
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

from flask import Flask, abort, render_template

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from firstpass import triage  # noqa: E402
from firstpass.models import GREEN, AMBER, RED, TriageResult  # noqa: E402
from firstpass.playbook import load as load_playbook  # noqa: E402

app = Flask(__name__)
PB = load_playbook()
CONTRACT_DIR = ROOT / "contracts"

VERDICT = {
    GREEN: {"label": "GREEN", "cls": "green", "route": "Auto-clear", "sub": "spot-check only"},
    AMBER: {"label": "AMBER", "cls": "amber", "route": "Confirm", "sub": "redlines pre-drafted"},
    RED: {"label": "RED", "cls": "red", "route": "Escalate", "sub": "full human review"},
}
ORDER = {RED: 0, AMBER: 1, GREEN: 2}
KIND_LABEL = {"red_flag": "RED FLAG", "deviation": "DEVIATION",
              "missing_clause": "MISSING", "novel_clause": "NOVEL"}


def _queue():
    paths = sorted(glob.glob(str(CONTRACT_DIR / "*.txt")))
    results = triage.triage_queue(paths, pb=PB)
    return sorted(results, key=lambda r: (ORDER[r.verdict], -len(r.findings)))


@app.route("/")
def index():
    results = _queue()
    n = len(results)
    counts = {v: sum(1 for r in results if r.verdict == v) for v in (RED, AMBER, GREEN)}
    manual = sum(r.manual_minutes for r in results)
    fp = sum(r.firstpass_minutes for r in results)
    handled = counts[GREEN] + counts[AMBER]
    return render_template(
        "index.html", results=results, verdict=VERDICT, n=n, counts=counts,
        handled=handled, handled_pct=round(100 * handled / n) if n else 0,
        manual=manual, fp=fp, saved=manual - fp,
        saved_pct=round(100 * (manual - fp) / manual) if manual else 0,
        hours_saved=round((manual - fp) / 60, 1),
    )


@app.route("/contract/<cid>")
def detail(cid):
    path = CONTRACT_DIR / f"{cid}.txt"
    if not path.exists():
        abort(404)
    r: TriageResult = triage.triage_contract(str(path), pb=PB)
    return render_template("detail.html", r=r, v=VERDICT[r.verdict], kinds=KIND_LABEL)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
