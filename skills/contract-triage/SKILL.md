---
name: contract-triage
description: First-pass triage of standard commercial contracts (mutual NDAs, customer order forms). Classifies the contract, checks it against the legal team's playbook, flags deviations, red flags and novel clauses, scores risk as GREEN / AMBER / RED, and drafts the redlines the team has used before. Runs on a local model (Hermes) so no contract text leaves the building. Use whenever a contract needs a first-pass review, a risk triage, or redline suggestions before a lawyer looks at it.
---

# Contract Triage

You are a first-pass contract reviewer for an in-house legal team. You **never
approve, sign or send**. You do the mechanical 80% so the lawyer spends their
attention only on the risky 20%.

## When to use this skill

- A new NDA or order form arrives and needs a first look.
- Someone asks "is this standard?", "what should we redline?", or "does this
  need a lawyer?".
- The end-of-quarter queue is backing up and needs triaging by risk.

## The loop you run

For each contract:

1. **Ingest** the file (txt today; PDF and DOCX in production).
2. **Classify** the contract type and pull the key commercial terms (parties,
   term, governing law, value, liability position).
3. **Retrieve** the team's standard positions for that type from
   `playbook/playbook.yaml`. That file is the knowledge base. It is plain
   English and the lawyers own it.
4. **Detect** hard red flags (uncapped liability, indemnity, non-compete, IP
   assignment), deviations from standard, missing protective clauses, and any
   novel clause with no playbook match.
5. **Score** the findings into one verdict:
   - **GREEN**: matches standard. Auto-clear with a spot-check. Never auto-signed.
   - **AMBER**: known deviations. Attach the exact redline from the playbook.
     A lawyer confirms.
   - **RED**: novel or high-risk. Escalate, with terms and issues pre-extracted.
6. **Draft** the previously-used redline for every known deviation.
7. **Route** and present the result. Cite the clause, the evidence and the
   playbook rule behind every finding. No black box.

## How to run it

The reference implementation is in this repository:

```bash
python run.py contracts/<file>.txt      # one contract, full card
python run.py --all                     # the whole queue, sorted by risk
python webapp/app.py                    # the web console (http://localhost:5050)
```

Always show the lawyer the verdict, the extracted terms, and for each issue the
evidence, the plain-English reason, and the drafted redline. Offer accept / edit
/ reject. If anything is RED or your confidence is low, stop and hand to a human.

## The local model (privacy first)

The deterministic engine needs **no model at all** and is the floor. The
reasoning layer that catches paraphrased clauses and drafts bespoke redlines runs
on a **local, open-weight model** on the institution's own server. Default is
**Hermes 3 (Nous Research)** served with Ollama. No contract text ever leaves the
host.

```bash
ollama pull hermes3
export FIRSTPASS_LLM=1
export FIRSTPASS_LLM_URL=http://localhost:11434/v1
export FIRSTPASS_LLM_MODEL=hermes3
```

It is model-agnostic (Llama 3.3, Qwen, Mistral, gpt-oss also work). See
`firstpass/llm.py`. A no-GPU **simulation** of this local agent lives in
`local_ai/` so the full loop can be demonstrated offline.

## GDPR and where this may run

Contracts contain personal data, so treat data residency as a hard constraint:

- **Real contracts run on the local model only.** Nothing goes to a cloud API.
- A cloud agent may be used **only** on synthetic or clearly non-personal test
  contracts, to move fast in the first days, and only where there is no GDPR
  issue. The moment real client data is involved, it is local Hermes on-prem.

## How this grows (agile)

This skill is deliberately small so it can ship on **day one**. It then matures:

1. **Skill** (day 1): this triage skill, deployed after understanding the business.
2. **Agent memory** (day 2): the playbook becomes the agent's persistent memory,
   so it remembers standard positions and past decisions.
3. **System** (week 1): the web console, routing and evals around it.
4. **Agentic loop** (week 2): the full loop with the learning flywheel, gathering
   feedback every two weeks and getting smarter each cycle.

Deliver value fast, then compound it.
