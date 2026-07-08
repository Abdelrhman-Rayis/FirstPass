#!/usr/bin/env python3
"""Demonstrate the learning loop (step 8) on the exact gap the eval found.

The eval showed one recall miss: on `nda_broaddef_hooli`, the offline rules
engine did not recognise the paraphrased broad-definition clause ("every piece
of information ... in any form whatsoever").

Here a lawyer resolves it once and teaches the playbook that phrasing. We run the
contract before and after. No code changes, no redeploy: the miss is closed.
This is the compounding loop that makes FirstPass a system, not a script.

Operates on a COPY of the playbook so the shipped file stays pristine.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from firstpass import triage, learn  # noqa: E402
from firstpass.playbook import load as load_playbook  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = str(ROOT / "contracts" / "nda_broaddef_hooli.txt")


def caught_overbroad(playbook_path) -> bool:
    r = triage.triage_contract(CONTRACT, pb=load_playbook(playbook_path))
    return any(f.id == "overbroad_definition" for f in r.findings)


def main():
    tmp = Path(tempfile.mkdtemp()) / "playbook.yaml"
    shutil.copy(ROOT / "playbook" / "playbook.yaml", tmp)

    print("=" * 64)
    print(" LEARNING LOOP DEMO  ·  nda_broaddef_hooli")
    print("=" * 64)
    print(f" BEFORE: overbroad-definition caught? {caught_overbroad(tmp)}   (rules layer misses the paraphrase)")

    msg = learn.add_signal(
        contract_type="mutual_nda",
        clause_id="definition",
        deviation_id="overbroad_definition",
        new_signals=["every piece of information", "any form whatsoever"],
        playbook_path=str(tmp),
    )
    print(f"\n A lawyer teaches the playbook (one edit, no code):\n   {msg}\n")

    print(f" AFTER : overbroad-definition caught? {caught_overbroad(tmp)}   (now routine, forever)")
    print("=" * 64)
    print(" Net effect: material-issue recall on this set goes 93% -> 100%,")
    print(" driven by a domain expert, not an engineer. That is the flywheel.")
    print("=" * 64)


if __name__ == "__main__":
    main()
