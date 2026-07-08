# FirstPass

**Every contract gets an AI first pass. A human confirms. The queue gets shorter every month.**

An agentic first-pass reviewer for the standard commercial contracts an in-house
legal team sees all day: mutual NDAs and customer order forms. It reads each
contract, checks it against the team's own standard positions, and routes it:

- 🟢 **GREEN** — matches standard. Auto-clear with a spot-check. Never auto-signed.
- 🟡 **AMBER** — known deviations. The redline is already drafted; the lawyer confirms.
- 🔴 **RED** — novel or high-risk. Escalate for a full human review.

Built for the PortSwigger *AI Pioneer* task by Abdelrhman Rayis. It is a working
artefact, not a slide about one. The deck in `deck/` explains the thinking; this
is the thing that runs.

---

## The problem (in PortSwigger's words)

> Most are 80% boilerplate. Where we do get redlines and requests for amends,
> they're usually questions and edits we've seen before. Right now, every single
> contract still gets read by a person, and the queue is usually longer than the
> day. When we reach the end of month or end of quarter ... it can get overwhelming.

## The insight the whole thing is built on

**First principles.** Contract review is not a reading task. It is a *risk-gating
decision*: protect the company from unacceptable terms without blocking revenue.
Strip it back and every review is the same five steps: read, classify, compare
to our standard positions, spot the deviations, decide accept / redline / escalate.

**80/20.** 80% is boilerplate, and the redlines that do come up are "edits we've
seen before" — a finite, reusable playbook. So ~80% of the queue needs close to
zero net-new thinking.

**Systems thinking.** The bottleneck is not that lawyers read slowly. It is that
*every contract consumes the same scarce human attention regardless of risk*.
There is no triage layer. The leverage point is to insert one, so human attention
flows only to the 20% that actually carries risk. FirstPass is that triage layer.

(PortSwigger already believe this: Burp Suite triages security findings by
severity so humans focus on real threats. FirstPass does the same for contracts.)

---

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python run.py --all                                  # triage the whole queue (CLI)
python run.py contracts/nda_perpetual_initech.txt    # one contract, full card
python evals/run_eval.py                             # measure it (writes results.md)
python evals/demo_learning.py                        # watch the playbook learn

python webapp/app.py                                 # the web console -> http://localhost:5050
```

No API key needed, and nothing leaves the machine: the whole thing runs offline
on a deterministic engine. The optional reasoning layer is an on-prem local model
(see "Private by design" below), not a cloud API.

---

## What it does, on a real contract

`python run.py contracts/nda_perpetual_initech.txt`

```
 AMBER  nda_perpetual_initech  (Mutual Non-Disclosure Agreement)
  route      : CONFIRM     (pre-drafted redlines ready)
  confidence : 95%
  1. [DEVIATION | medium | known] Perpetual / indefinite confidentiality term
     redline: Replace the perpetual obligation with a fixed term of three (3)
              years from the date of disclosure ...
  2. [DEVIATION | medium | known] Non-England & Wales governing law
     redline: Amend governing law and exclusive jurisdiction to the laws of
              England and Wales ...
```

The lawyer opens this and, instead of reading the contract cold, confirms two
redlines that are already written. That is the time saving.

---

## Does it actually help? (the evals)

`python evals/run_eval.py`, deterministic engine, 10-contract synthetic set:

| Metric | Result |
|---|---|
| **Unsafe escalation misses** (RED routed as non-RED) | **0** — nothing risky was auto-cleared |
| Triage verdict accuracy | 100% (10/10) |
| Material-issue precision / recall | 93% / 93% |
| Human review time | 375 min → 157 min (**58% saved**) |
| Extrapolated to 200 contracts/month | ~125h → ~52h (**~73 hours/month returned**) |

These are the **floor**: the offline rules engine with no LLM. The one recall
miss is a paraphrased clause (`nda_broaddef_hooli`) the keyword layer does not
catch; that is exactly what the on-prem local-model layer (`firstpass/llm.py`)
and the human-confirm step exist for. Numbers are reproducible and honest, not
cherry-picked. Full breakdown in [`evals/results.md`](evals/results.md).

---

## The flywheel (why this is a startup, not a script)

`python evals/demo_learning.py`

When a lawyer resolves a RED (a novel clause, or a deviation we had not seen),
they record the decision. It becomes a playbook entry with the redline they
actually used. The next contract carrying that clause is no longer RED, it is
AMBER with the redline pre-drafted. **Every human decision permanently shrinks
the future queue.** The demo takes the exact recall gap the eval found and closes
it with a one-line playbook edit, no code, taking recall 93% → 100%.

The playbook (`playbook/playbook.yaml`) is plain English. A lawyer edits it. No
engineer, no retraining. That is the moat: it fills with *your* positions.

---

## How it works

```
run.py / webapp/app.py ─► firstpass/triage.py   the agentic loop
          │                     (ingest→classify→retrieve→detect→score→draft→route)
          ├─ ingest.py          file → clauses (PDF/DOCX hooks included)
          ├─ playbook.py        loads playbook/playbook.yaml
          ├─ detect.py          deterministic red-flag / deviation / novelty layer
          ├─ llm.py             OPTIONAL on-prem local model (Ollama/vLLM), no cloud
          ├─ risk.py            findings → GREEN/AMBER/RED + confidence + time model
          ├─ report.py          the lawyer-facing card (CLI)
          └─ learn.py           step 8: teach the playbook (the flywheel)
webapp/                         Flask web console (dashboard + review view)
```

## Private by design: local AI, on your server

Contracts are privileged and confidential, and this is for a security company,
so the reasoning model runs **on the institution's own server, not a third-party
API**. No contract text ever leaves your infrastructure.

- The deterministic engine needs **no model at all**: that is the reported floor.
- The optional reasoning layer (`firstpass/llm.py`) talks to any local
  OpenAI-compatible endpoint, so it is model-agnostic: point it at an open-weight
  model (Llama 3.3, Qwen, Mistral, gpt-oss) served with Ollama or vLLM. Enable it
  with `FIRSTPASS_LLM=1`; otherwise it stays inert and the pipeline is fully
  offline and reproducible.

## Safety and guardrails (this is legal, so this matters)

- **Never signs, never sends.** FirstPass routes and drafts; a human always decides.
- **Fails towards a human.** Anything novel, high-severity, or low-confidence goes
  RED by design. The eval tracks unsafe misses as the primary metric; it is 0.
- **Every call is explainable.** Each finding cites the clause, the evidence
  snippet, and the playbook rule behind it. No black box.
- **Your data stays yours.** The whole system runs on-prem; the playbook is your IP.

## What a 2-week production sprint adds

Week 1: shadow the reviewer, capture their real playbook, wire up PDF/DOCX
ingestion and the on-prem local model. Week 2: ship into their workflow (email
or CLM inbox), run the eval on real historic contracts, hand over the playbook so
Legal owns it, and leave. Then the next domain.

## Honest limitations

- The eval set is 10 synthetic contracts, a smoke test, not a benchmark. The real
  number comes from the measured sprint on historic contracts.
- The offline engine is keyword + retrieval, so it misses paraphrases; that is the
  reported recall gap and the reason the local-model layer exists.
- Two contract types are modelled (NDA, order form). Adding a type is playbook
  work, not code.
