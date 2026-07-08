#!/usr/bin/env python3
"""Simulate the on-prem local agent, with no GPU and no cloud.

The production reasoning layer is a local open-weight model (Hermes 3, served
with Ollama) running on the institution's own server. You cannot ship a GPU in a
zip, so this file stands in for it: a deterministic ``SimulatedHermes`` that
implements the same interface as ``firstpass.llm.LocalLLMEngine`` and mimics what
a local model adds over the pure rules engine, namely catching PARAPHRASED
clauses that keyword matching misses.

Run it to see the difference the local model makes, entirely offline:

    python local_ai/simulate_local_agent.py

For the real wiring (an OpenAI-compatible endpoint like Ollama or vLLM would
expose), see ``mock_hermes_server.py`` in this folder.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from firstpass import triage  # noqa: E402
from firstpass.playbook import load as load_playbook  # noqa: E402

# Expanded, meaning-level cues per known deviation. A real local model derives
# these from understanding; here they are hand-listed to simulate that the model
# recognises the clause even when the exact keywords are absent.
_SEMANTIC_CUES = {
    "overbroad_definition": ["every piece of information", "any form", "whether or not",
                             "regardless of", "all copies", "in any form whatsoever"],
    "one_way": ["receiving party shall", "recipient shall", "unilateral", "the recipient agrees"],
    "perpetual_term": ["in perpetuity", "shall not expire", "indefinitely", "no expiry", "survive forever"],
    "foreign_law": ["state of", "laws of the state", "republic of", "courts of new york"],
    "extended_payment": ["net 60", "net 90", "within 60 days", "within 90 days"],
    "long_autorenew": ["automatically renew", "auto-renew", "unless terminated"],
    "foreign_law_of": ["state of", "laws of the state"],
}


class SimulatedHermes:
    """Stand-in for a local Hermes model. Same interface as LocalLLMEngine."""

    model = "hermes3-simulated"

    def available(self) -> bool:
        return True

    def semantic_match(self, clause_text: str, known_deviations: List[Dict]) -> Optional[Dict]:
        text = clause_text.lower()
        for dev in known_deviations:
            cues = _SEMANTIC_CUES.get(dev["id"], dev.get("signal", []))
            if any(cue.lower() in text for cue in cues):
                return dev
        return None

    def draft_redline(self, clause_text: str, standard_position: str) -> str:
        return (f"Bring this clause into line with our standard position: "
                f"{standard_position} (drafted locally by Hermes, on-prem).")


def _material(f):
    return f.kind in ("red_flag", "deviation", "novel_clause") or \
        (f.kind == "missing_clause" and f.severity == "high")


def main():
    pb = load_playbook()
    contract = str(ROOT / "contracts" / "nda_broaddef_hooli.txt")

    print("=" * 68)
    print(" LOCAL AGENT SIMULATION  ·  no GPU, no cloud")
    print("=" * 68)
    print(" Contract: nda_broaddef_hooli  (has a paraphrased broad-definition clause)\n")

    base = triage.triage_contract(contract, pb=pb)  # deterministic, no model
    base_ids = {f.id for f in base.findings if _material(f)}
    print(f" 1) Rules engine only        engine={base.engine:<12} caught: {sorted(base_ids)}")
    print("    -> misses 'overbroad_definition': the wording is paraphrased.\n")

    local = triage.triage_contract(contract, pb=pb, llm=SimulatedHermes())
    local_ids = {f.id for f in local.findings if _material(f)}
    print(f" 2) With local Hermes (sim)   engine={local.engine:<12} caught: {sorted(local_ids)}")
    gained = local_ids - base_ids
    if gained:
        print(f"    -> the local model understands the meaning and adds: {sorted(gained)}")
    print()
    print(" Same verdict routing, higher recall, and not one byte left the host.")
    print(" In production this is Hermes 3 on your server via Ollama (see SKILL.md).")
    print("=" * 68)


if __name__ == "__main__":
    main()
