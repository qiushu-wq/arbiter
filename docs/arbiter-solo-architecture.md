# Arbiter Solo · Personal Agent Runtime

> A pip-installable personal agent runtime. From solo developer to enterprise.
> Built on insights from Claude Agent SDK, OpenAI Agents SDK, and Google ADK.
> 
> 2026-06 · Design Overview

---

## What It Is

Arbiter Solo gives individual developers a lightweight agent runtime — handle context window allocation, tool scheduling, state persistence, and audit trail. No infrastructure. No vector database. One config file.

```
pip install arbiter-solo
arbiter solo run "find me projects on V2EX"
```

---

## Architecture (5 Layers)

```
Interface → Agent Loop → Model Routing → Memory → Tools & Sandbox
```

Each agent call passes through three gates: Safety → Quota → Audit. Not a framework — a runtime that sits between agents and LLMs.

---

## Solo vs Cloud

| | Solo | Cloud |
|------|------|-------|
| Agents | 3-10 | 10-50 |
| Pricing | Free (MIT) | $99-299/month |
| Quota | Fixed partition | Adaptive (learns patterns) |
| Recovery | Manual | Auto-heal + circuit breaker |
| Memory | 3-tier file-based | Same + shared context |

---

## Upgrade Path

```
Arbiter Solo (free, MIT)
    → Arbiter Cloud ($99-299/month)
        → Arbiter Enterprise (custom pricing)
```

Upgrade triggers are pain-driven, not agent-count-driven. When you hit context overflow 3 times in a week, you know it's time.

---

## Competitive Position

| | Claude | OpenAI | Google | Arbiter |
|------|--------|--------|--------|---------|
| Agent loop | Yes | Yes | Yes | Yes |
| Per-agent quota | No | No | No | **Yes** |
| Audit trail | No | No | No | **Yes** |
| Upgrade path | No | No | No | **Solo→Cloud→Enterprise** |
| Single command install | CLI | Needs sandbox | Needs Cloud Run | **pip install** |

---

## Open Source

- `arbiter-doctor`, `arbiter-lite`, `stability-metrics`: MIT — free forever
- Arbiter Solo: MIT
- Arbiter Cloud & Enterprise: Commercial

GitHub: [qiushu-wq/arbiter](https://github.com/qiushu-wq/arbiter)
