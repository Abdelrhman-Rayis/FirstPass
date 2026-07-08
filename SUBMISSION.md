# PortSwigger AI Pioneer, task submission

**Abdelrhman Rayis** · the brief: show how AI could help the in-house legal team
clear its contract-review queue.

I built a working thing, not a slide about one. This zip has both: a running
prototype **and** a deck that presents it.

## What is in here

| | |
|---|---|
| **The pitch** | `deck/FirstPass_PortSwigger.pdf` (open this first) and the editable `.pptx` |
| **The prototype** | `firstpass/`, `run.py`, the `playbook/` and `contracts/` |
| **The web console** | `webapp/` (Flask). `assets/` holds the screenshots used in the deck |
| **The day-one skill** | `skills/contract-triage/SKILL.md` (runs on a local Hermes model) |
| **The local-AI sim** | `local_ai/` (no-GPU stand-in for the on-prem model) |
| **The evals** | `evals/run_eval.py`, `evals/results.md` |
| **The full write-up** | `README.md` |

## See it run in 30 seconds

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python run.py --all                      # triage the whole contract queue (CLI)
python webapp/app.py                     # the web console -> http://localhost:5050
python evals/run_eval.py                 # measure it: safety, accuracy, time saved
python evals/demo_learning.py            # watch the playbook learn and improve
python local_ai/simulate_local_agent.py  # the local (Hermes) model, simulated offline
```

## How I would deliver it: agile, value from day one

Day 1 a **skill**, day 2 the skill becomes the agent's **memory**, week 1 a
**system**, week 2 the full **agentic loop**, with feedback every two weeks. It
starts cloud-fast on synthetic test data where there is no GDPR issue, then moves
fully in-house to a **local Hermes model** the moment real client data is
involved. Value fast, privacy kept.

No API key needed, and nothing leaves the machine. The reasoning layer is an
**on-prem local model** (Ollama / vLLM), not a cloud API, so contract text never
leaves your infrastructure.

## The one-line idea

Contract review is a risk gate, not a reading task. Today every contract costs
the same scarce human attention regardless of risk. **FirstPass** is a triage
layer that auto-clears the standard 80%, pre-drafts the redlines it has seen
before, and escalates only the novel or risky 20%, the same way Burp Suite
triages security findings by severity so humans focus on what matters. And every
human decision is written back to the playbook, so the queue gets shorter every
month.

Measured on a labelled set: **0 unsafe misses, 100% triage accuracy, 58% of
review time removed**, about 73 legal hours a month back at 200 contracts/month.
It runs entirely **on-prem with a local model**, so confidential contracts never
touch the cloud.
