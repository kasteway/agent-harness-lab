# Start here: understand the agent before the code gets big

An agent harness is the ordinary Python around a model: **ask what to do → run an allowed tool → return the result → repeat → stop**. This repository lets you see that loop in three small stages.

## Stage 1 — Watch the loop

```bash
python3 -m agent_lab.cli --trace
```

This uses 12 fictional support tickets and a **scripted practice model**. Follow the three calls: compare SLA, find a driver, retrieve a note. It is free and repeatable. Read the 20-line [`run()` function](agent_lab/harness.py) afterward. You do not need to understand every file yet.

## Stage 2 — Run a real financial-services case

```bash
python3 -m agent_lab.payment_case
```

This uses a **real public CFPB money-transfer complaint snapshot**, aggregated to monthly issue counts. The same loop calls three different read-only tools: an overview, a monthly fraud/scam series, and a source note. It answers what an operations lead should review. The decision maker is still scripted so the sequence is easy to study; the calculations use real data.

The standout finding is **2,929 Fraud or scam-labeled complaints out of 7,953 in the filtered January–June 2024 slice (36.8%)**. These are published complaint counts, not a fraud incidence rate. Source and filters are in [`data/provenance.json`](data/provenance.json).

## Stage 3 — Isolate the two building blocks

- [Payments Operations MCP Lab](https://github.com/kasteway/payments-mcp-lab) shows the client discovering and calling the server. It uses the same public data snapshot.
- [Payments Operations RAG Lab](https://github.com/kasteway/payments-rag-lab) shows documents, chunks, vectors, retrieval, citations, and an optional local model.

Then return to the full [`STUDY_GUIDE.md`](STUDY_GUIDE.md) for the original video chapter mapping, deeper code explanation, evaluation, and safeguards.

**Interview sentence:** “I first built an agent loop I can trace step by step, then applied the same loop to a real public financial-services operations question. I separated deterministic data calculations from model decisions and added specific source and safety boundaries.”
