#!/usr/bin/env python3
"""A no-GPU mock of the local Hermes model, as an OpenAI-compatible server.

This is what Ollama or vLLM would expose on-prem. It lets you exercise the REAL
reasoning path in firstpass/llm.py without a GPU or any cloud call:

    # terminal 1
    python local_ai/mock_hermes_server.py            # serves on :11500

    # terminal 2
    export FIRSTPASS_LLM=1
    export FIRSTPASS_LLM_URL=http://localhost:11500/v1
    export FIRSTPASS_LLM_MODEL=hermes3
    python run.py contracts/nda_broaddef_hooli.txt   # now uses the local model

Every request stays on localhost. Nothing leaves the machine.
"""
from __future__ import annotations

import time

from flask import Flask, jsonify, request

app = Flask(__name__)

# Same meaning-level cues as the simulation, so the mock behaves like a small
# local model that understands paraphrase.
_CUES = {
    "overbroad_definition": ["every piece of information", "any form", "whether or not", "regardless of"],
    "one_way": ["receiving party shall", "recipient shall", "unilateral"],
    "perpetual_term": ["in perpetuity", "shall not expire", "indefinitely"],
    "foreign_law": ["state of", "laws of the state", "republic of"],
    "foreign_law_of": ["state of", "laws of the state"],
    "extended_payment": ["net 60", "net 90", "within 60 days", "within 90 days"],
    "long_autorenew": ["automatically renew", "auto-renew", "unless terminated"],
}


def _answer(prompt: str) -> str:
    low = prompt.lower()
    if "known deviations:" in low:  # semantic_match request
        for dev_id, cues in _CUES.items():
            if dev_id in low and any(c in low for c in cues):
                return dev_id
        return "NONE"
    if "draft a concise redline" in low:  # draft_redline request
        return ("Amend this clause to our standard position, and flag to Legal if the "
                "counterparty pushes back. (drafted locally by Hermes, on-prem)")
    return "NONE"


@app.route("/v1/models")
def models():
    return jsonify({"data": [{"id": "hermes3", "object": "model"}]})


@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    body = request.get_json(force=True)
    user = ""
    for m in body.get("messages", []):
        if m.get("role") == "user":
            user = m.get("content", "")
    content = _answer(user)
    return jsonify({
        "id": "chatcmpl-local",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.get("model", "hermes3"),
        "choices": [{"index": 0, "finish_reason": "stop",
                     "message": {"role": "assistant", "content": content}}],
    })


if __name__ == "__main__":
    print("Mock local Hermes model on http://127.0.0.1:11500/v1  (nothing leaves the host)")
    app.run(host="127.0.0.1", port=11500, debug=False)
