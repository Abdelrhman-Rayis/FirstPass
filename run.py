#!/usr/bin/env python3
"""FirstPass CLI.

    python run.py contracts/nda_oneway_globex.txt      # one contract, full card
    python run.py --all                                # triage the whole queue
    python run.py --all --json                         # machine-readable
"""
from __future__ import annotations

import argparse
import glob
import json
import sys

from firstpass import triage
from firstpass.llm import LLMEngine
from firstpass.models import GREEN, AMBER, RED
from firstpass.playbook import load as load_playbook
from firstpass.report import render_terminal

_ORDER = {RED: 0, AMBER: 1, GREEN: 2}
_ICON = {GREEN: "\033[42;30m 🟢 \033[0m", AMBER: "\033[43;30m 🟡 \033[0m", RED: "\033[41;37m 🔴 \033[0m"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="FirstPass contract triage")
    ap.add_argument("paths", nargs="*", help="contract file(s)")
    ap.add_argument("--all", action="store_true", help="triage every contract in contracts/")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args(argv)

    paths = args.paths
    if args.all:
        paths = sorted(glob.glob("contracts/*.txt"))
    if not paths:
        ap.print_help()
        return 1

    pb = load_playbook()
    llm = LLMEngine()  # inert unless FIRSTPASS_LLM=1 and a local model is reachable
    results = triage.triage_queue(paths, pb=pb, llm=llm)

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2, default=str))
        return 0

    if args.all or len(results) > 1:
        _print_dashboard(results)
    for r in results:
        print(render_terminal(r, color=not args.no_color))
    return 0


def _print_dashboard(results):
    results = sorted(results, key=lambda r: _ORDER[r.verdict])
    n = len(results)
    counts = {v: sum(1 for r in results if r.verdict == v) for v in (RED, AMBER, GREEN)}
    manual = sum(r.manual_minutes for r in results)
    fp = sum(r.firstpass_minutes for r in results)
    saved = manual - fp
    print("\n" + "=" * 72)
    print(f" FIRSTPASS QUEUE  ·  {n} contracts")
    print("=" * 72)
    for r in results:
        issues = len(r.findings)
        print(f" {_ICON[r.verdict]} {r.contract_id:<28} {r.type_label:<28} {issues} issue(s)")
    print("-" * 72)
    print(f" Triage: {counts[GREEN]} auto-clear · {counts[AMBER]} confirm · {counts[RED]} escalate")
    auto = counts[GREEN] + counts[AMBER]
    print(f" {auto}/{n} ({100*auto//n}%) handled without a cold human read.")
    print(f" Human minutes: {manual} manual  ->  {fp} with FirstPass   ({saved} saved, {100*saved//manual}%)")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    sys.exit(main())
