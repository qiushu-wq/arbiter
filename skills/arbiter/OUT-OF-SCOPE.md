# Out of Scope

Arbiter deliberately does NOT diagnose:

- **Single-agent systems** — Arbiter is for multi-agent. Single-agent issues are a different category.
- **LLM prompt quality** — Arbiter doesn't evaluate whether your prompts are good. It checks whether your agents will stay alive.
- **API costs or rate limits** — Arbiter manages token budgets between agents, not your API bill.
- **Security vulnerabilities** — Not a security scanner. Use dedicated tools for that.
- **Non-Python projects** — Current version is Python-only (LangGraph, CrewAI, AutoGen).
