"""The agentic loop: ask model -> validate tool -> run tool -> return evidence -> repeat."""

from .tools import execute


def run(question, model, max_steps=5, execute_tool=execute):
    if not isinstance(question, str) or not question.strip() or len(question) > 500:
        raise ValueError("question must be 1-500 characters")
    if not 1 <= max_steps <= 10:
        raise ValueError("max_steps must be 1-10")
    history = []
    for step in range(max_steps):
        decision = model.decide(question, history)
        if decision.answer is not None:
            answer = decision.answer.strip()
            if not answer:
                raise RuntimeError("model returned an empty answer")
            return {"answer": answer, "trace": history, "steps": step + 1}
        if not decision.tool or not isinstance(decision.arguments, dict):
            raise RuntimeError("model returned neither an answer nor a valid tool request")
        # The model does not execute its own request. This code remains in control.
        result = execute_tool(decision.tool, decision.arguments)
        history.append({"name": decision.tool, "arguments": decision.arguments,
                        "result": result, "call_id": decision.call_id})
    raise RuntimeError(f"Stopped after {max_steps} steps; no final answer")
