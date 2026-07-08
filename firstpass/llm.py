"""Optional reasoning layer: a LOCAL, on-prem model. Nothing leaves the host.

Design decision (privacy and security first):
Contracts are confidential and this is being built for a security company, so the
reasoning model runs ON THE INSTITUTION'S OWN SERVER, not in the cloud. No
contract text is ever sent to a third-party API. The deterministic engine
(``detect.py``) already does the whole job offline; this layer only lifts recall
on paraphrased clauses and drafts bespoke redlines, and it does so against a
local model served on localhost.

It talks to any OpenAI-compatible endpoint, so it is model-agnostic. Point it at:
  * Ollama            (http://localhost:11434/v1)   e.g. llama3.3:70b, qwen2.5:32b
  * vLLM / TGI        (http://localhost:8000/v1)     any open-weight model
  * LM Studio / llamafile, etc.

Modern open-weight models (Llama 3.3, Qwen2.5/Qwen3, Mistral, gpt-oss) in the
30B to 70B range run comfortably on a single server GPU and are more than capable
of clause classification and redline drafting.

It is inert by default: with no reachable local endpoint, ``available()`` is
False and the pipeline stays fully deterministic, so the demo and the eval remain
reproducible with zero model.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Dict, List, Optional

# On-prem endpoint. Defaults to a local Ollama server. No egress, ever.
BASE_URL = os.environ.get("FIRSTPASS_LLM_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("FIRSTPASS_LLM_MODEL", "qwen2.5:32b-instruct")
TIMEOUT = float(os.environ.get("FIRSTPASS_LLM_TIMEOUT", "30"))

_SYSTEM = (
    "You are FirstPass, a first-pass contract reviewer for an in-house legal "
    "team. You never approve or sign. You compare a clause against the team's "
    "standard position, decide if it deviates, classify severity as low/medium/"
    "high, and if it is a known pattern draft the exact redline the team uses. "
    "You always defer novel or high-severity clauses to a human."
)


class LocalLLMEngine:
    """Thin client for a local OpenAI-compatible chat endpoint (stdlib only)."""

    def __init__(self, base_url: str = BASE_URL, model: str = MODEL) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def available(self) -> bool:
        """True only if a local model server is actually reachable.

        Explicitly opt-in via FIRSTPASS_LLM=1 so the offline demo never tries to
        reach a server that is not there.
        """
        if os.environ.get("FIRSTPASS_LLM") not in ("1", "true", "yes"):
            return False
        try:
            urllib.request.urlopen(self.base_url.replace("/v1", "") + "/", timeout=2)
            return True
        except Exception:
            try:  # some servers only answer on /v1/models
                urllib.request.urlopen(self.base_url + "/models", timeout=2)
                return True
            except Exception:
                return False

    def _chat(self, user: str, max_tokens: int = 300) -> str:  # pragma: no cover - needs a server
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0,
        }).encode()
        req = urllib.request.Request(
            self.base_url + "/chat/completions", data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"].strip()

    def semantic_match(self, clause_text: str, known_deviations: List[Dict]) -> Optional[Dict]:  # pragma: no cover
        """Best-matching known deviation for a clause, or None.

        Where paraphrase robustness comes from: the rules layer needs the words,
        a local model understands the meaning, all without leaving the host.
        """
        catalogue = "\n".join(f"- {d['id']}: {d['label']}" for d in known_deviations)
        out = self._chat(
            f"Clause:\n{clause_text}\n\nKnown deviations:\n{catalogue}\n\n"
            "Reply with the single matching deviation id, or NONE.", max_tokens=40,
        )
        return next((d for d in known_deviations if d["id"] in out), None)

    def draft_redline(self, clause_text: str, standard_position: str) -> str:  # pragma: no cover
        return self._chat(
            f"Standard position: {standard_position}\n\nCounterparty clause:\n{clause_text}\n\n"
            "Draft a concise redline moving this clause to our standard position, "
            "plus one sentence of rationale for the salesperson.", max_tokens=300,
        )


# Backwards-compatible alias used by run.py.
LLMEngine = LocalLLMEngine
