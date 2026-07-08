# Local AI: on-prem by design, simulated here

The production reasoning layer runs on a **local, open-weight model on the
institution's own server**, so no contract text ever leaves the building. Default
is **Hermes 3 (Nous Research)** via Ollama; it is model-agnostic (Llama 3.3,
Qwen, Mistral, gpt-oss also work). The wiring is in `firstpass/llm.py`.

You cannot put a GPU in a zip, so this folder stands in for the on-prem model:

| File | What it is |
|---|---|
| `simulate_local_agent.py` | No-GPU, in-process simulation. Shows the local model catching a paraphrased clause the rules engine misses. `python local_ai/simulate_local_agent.py` |
| `mock_hermes_server.py` | An OpenAI-compatible mock (what Ollama/vLLM expose). Exercises the real `llm.py` path over localhost. |

Run the real path against the mock (nothing leaves the host):

```bash
python local_ai/mock_hermes_server.py            # terminal 1, serves :11500
export FIRSTPASS_LLM=1
export FIRSTPASS_LLM_URL=http://localhost:11500/v1
export FIRSTPASS_LLM_MODEL=hermes3
python run.py contracts/nda_broaddef_hooli.txt   # terminal 2, uses the local model
```

In production you swap the mock for Ollama: `ollama pull hermes3`, point
`FIRSTPASS_LLM_URL` at `http://localhost:11434/v1`, done.

## The agile path: cloud-fast, then local-safe

1. **Day 1, a skill.** Ship the `contract-triage` skill (`skills/contract-triage/SKILL.md`)
   after understanding the business. To move fast it may run in a cloud agent
   **only on synthetic or non-personal test contracts, where there is no GDPR
   issue**.
2. **Day 2, agent memory.** The playbook becomes the agent's persistent memory of
   standard positions and decisions.
3. **Week 1, a system.** The console, routing and evals grow around it.
4. **Week 2, the agentic loop.** The full loop with the learning flywheel, with
   feedback gathered every two weeks.

The moment real client data is involved, the reasoning moves in-house to the
local Hermes model. Value fast, privacy kept.
