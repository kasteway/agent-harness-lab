# Agent Harness Lab: build an analytics agent from scratch

[![Offline checks](https://github.com/kasteway/agent-harness-lab/actions/workflows/checks.yml/badge.svg)](https://github.com/kasteway/agent-harness-lab/actions/workflows/checks.yml)

An **explainable Python learning project** inspired by Tech With Tim's [Build Your Own Agentic Harness in Python](https://www.youtube.com/watch?v=H5o1P8RMiMw). The video builds from model calls to tools, an agent loop, MCP, and memory. This lab uses that sequence, then adds **retrieval (RAG), evaluation, and safeguards**. It is original teaching code, not a copy of the creator's project.

**Start here:** [A three-stage beginner route](START_HERE.md) begins with the original fictional case, then runs a real public payments-operations case through the same agent loop.

**Original business scenario:** a support leader asks why SLA attainment dropped. The agent checks ticket-level data, identifies the largest regional contribution to late tickets, retrieves an operating note, and produces a cited investigation brief. All tickets and notes are **fictional**. No customer data, production system, or outbound action is involved.

## Quick start: two offline analytics cases

Requires Python 3.9+ and Git. Run these commands from a terminal; no API key or package installation is needed.

```bash
git clone https://github.com/kasteway/agent-harness-lab.git
cd agent-harness-lab
python3 -m agent_lab.cli --trace
python3 -m agent_lab.payment_case
```

The first case investigates SLA attainment using fictional support tickets. The second uses a [documented public CFPB money-transfer complaint snapshot](data/provenance.json): 7,953 filtered complaints, including 2,929 labeled “Fraud or scam.” These are published complaint counts, not a fraud rate or a representative sample.

Both cases use the same [`run()` loop](agent_lab/harness.py), a scripted decision maker, and read-only tools. The trace shows intermediate tool calls and results. **Offline practice is deterministic; it does not use a language model.** The optional live mode below lets a model choose tools.

To evaluate the lab and run its tests:

```bash
python3 -m agent_lab.evaluate
python3 -m unittest discover -s tests -v
```

Follow [START_HERE.md](START_HERE.md) for the walkthrough, or try another question with `python3 -m agent_lab.cli "What happened to our service level?" --trace`.

## Try real model-selected tools (optional)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[live]'
export OPENAI_API_KEY='your-key-here'
python -m agent_lab.cli --mode live --model gpt-5-mini --trace
```

Use a model available to your account. API usage may have a cost. The live model can choose among the same three read-only tools; Python validates the request and runs the function. The output may vary. Never commit your key or `.env` file. We do not run live mode in automated checks because it requires the user's credential and can incur charges.

## Optional MCP server

Use Python 3.10+ for the MCP SDK. The core practice lab still runs on Python 3.9+.

```bash
pip install -e '.[mcp]'
python -m agent_lab.mcp_server
```

This runs a **real MCP server** exposing the same three tools to a compatible MCP client over stdio. The CLI's agent loop calls the underlying Python functions directly; it does not route through MCP. That distinction is deliberate and visible in the code.

### See an API and MCP side by side

With the MCP dependency installed, run:

```bash
python -m agent_lab.compare_interfaces
```

The script calls the **same `compare_sla()` calculation twice**. First, a direct HTTP client knows `POST /tools/compare_sla` and handles its JSON response. Then an MCP client launches the local MCP server, discovers its tools, calls `compare_sla`, and reads the result. You can inspect [`http_api.py`](agent_lab/http_api.py), [`compare_interfaces.py`](agent_lab/compare_interfaces.py), and [`mcp_server.py`](agent_lab/mcp_server.py) to see who does what. The local HTTP server binds only to `127.0.0.1` and closes when the comparison finishes.

## Study path

Start with [START_HERE.md](START_HERE.md), then continue to [the illustrated, code-linked study guide](STUDY_GUIDE.md), then use the experiment prompts at the end. Each step maps a video chapter to a file you can run and a question you should be able to answer in an interview.

```text
question -> model decision -> validated Python tool -> evidence -> model decision -> answer
                       |                     |
                       |                 local tickets + notes
                       +-- bounded by allowlist and maximum steps

MCP server -> a separate standardized interface to the same tools
```

| Capability | What is actually implemented |
|---|---|
| Agent loop | Python loop that repeatedly asks for a decision, executes a validated tool, and returns evidence |
| Offline practice | Scripted decision maker; deterministic and free |
| Live model | Optional OpenAI Responses API model-chosen function calls |
| RAG | Local lexical retrieval with source IDs; live mode can use retrieved passages in its answer |
| MCP | Optional FastMCP server plus an actual client that discovers and calls its tools |
| Memory | Explicit, local, opt-in JSON Q&A history; not silently injected into model context |
| Evaluation | Reproducible arithmetic, retrieval, tool-sequence, citation, caution, and guardrail checks |
| Safeguards | Tool allowlist, input validation, read-only operations, bounded steps, and no code execution |

This is a learning lab, **not** a production support assistant. The sample is tiny. Lexical retrieval is a useful baseline, not an embeddings/vector database. The deterministic practice answer is not evidence of real-model reliability. Live-model behavior needs its own repeated evaluation before a real deployment.

## Automated checks

GitHub Actions runs the existing offline tests on every push and pull request, using Python 3.9 and 3.13. These checks require no API keys and make no paid model calls. They cover the agent loop, local HTTP interface, payment calculations, and safeguards; optional live-model and MCP integrations are outside this workflow.

## References

- [Original tutorial](https://www.youtube.com/watch?v=H5o1P8RMiMw)
- [OpenAI function calling guide](https://developers.openai.com/api/docs/guides/function-calling)
- [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP vs API video that motivated the comparison](https://www.youtube.com/watch?v=kn6dxL53NkM)
- [Your Applied AI Field Guide](https://github.com/kasteway/applied-ai-learning-lab/blob/main/STUDY_GUIDE.md)
- [Your OpsAtlas project](https://github.com/kasteway/opsatlas-ai)

## License

MIT. See [LICENSE](LICENSE).
