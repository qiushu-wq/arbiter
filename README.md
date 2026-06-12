# Arbiter — Multi-Agent Runtime

**Arbiter** is the missing runtime for multi-agent systems. It manages context window allocation, tool scheduling, and state persistence — so your agents don't crash when there are more than 3 of them.

> If LangChain/CrewAI is Express.js, Arbiter is Node.js. It doesn't tell your agents what to do. It keeps them from stepping on each other.

## Why

Multi-agent is great in demos. In production, every framework hits the same walls:

| Problem | Severity | What Happens |
|---------|----------|--------------|
| Context contention | Critical | 3 agents share a 128K window. One overflows, all crash. |
| Swallowed errors | High | `except: pass`. You lose days debugging invisible failures. |
| State conflicts | High | 2 agents write `state.messages` simultaneously. Data silently lost. |
| Token boundary crashes | Critical | Agent hits context limit mid-call. No warning, just a 400 error. |

Arbiter solves these with a 4-layer architecture: **Context Budget → Tool Scheduling → State Persistence → Audit Trail**.

## Arbiter Doctor — Free Diagnostic

Already running agents? Find out what's broken before it breaks.

```bash
pip install git+https://github.com/qiushu-wq/arbiter.git
arbiter-doctor ./my-agent-project
```

Output:
```
Diagnosis: 5 Agents - LangGraph - 23 files
--------------------------------------------------------
[HIGH] Context sharing: 3 agents share one StateGraph, no quota
     -> Your researcher and writer compete for the same 128K window
     -> ~12% of calls near context boundary, risk of overflow
     Fix: arbiter.lite quota manager — see below

[MED] Swallowed errors: agent_timeout caught and print()'d, not logged
     -> At least 7 timeouts silently lost last week
     Fix: Arbiter audit trail records every call status
--------------------------------------------------------
2 high, 1 medium
```

**Doctor is free. No registration. No API key. Just run it.**

## Arbiter Lite — Free Quota Manager (MIT)

40 lines of Python. Fixes the most common multi-agent crash: context contention.

```python
from arbiter_lite import QuotaManager

qm = QuotaManager(max_tokens=128000, agent_names=["researcher", "writer", "reviewer"])

# Before each agent call:
tokens = qm.request("researcher", 30000)  # Researcher gets up to 30K
# If writer is idle for 5min, its quota is reclaimed and given to researcher
```

```bash
pip install arbiter-lite@git+https://github.com/qiushu-wq/arbiter.git
```

**Lite is MIT licensed. Free forever. Use it in your commercial projects.**

## Arbiter Cloud — Managed Runtime

When you grow from 6 agents to 60, Lite isn't enough. Cloud adds:

- **Heal**: Auto-recovery from agent failures
- **Adapt**: Learns usage patterns, pre-allocates quota
- **Guard**: Circuit breaker — 3 failures in 10min → auto-fuse
- **Cap**: Hard token limits per agent per month
- **Drain**: Graceful agent shutdown without losing in-flight tasks
- **Lock**: Per-project state locks to prevent write conflicts

```bash
arbiter cloud login
arbiter cloud deploy ./AGENTS.md
```

**$99-299/month.** [Join waitlist →](https://github.com/qiushu-wq/arbiter)

## Architecture

```
Ring 1 (Now):  budget + audit + status + trace + doctor
Ring 2 (Q3):   heal + adapt + guard + cap + drain + lock
Ring 3 (Q4):   Studio dashboard + enterprise features
```

## License

- `arbiter-doctor` & `arbiter-lite`: MIT
- Arbiter Cloud & Enterprise: Commercial

---

Built with 6 years of multi-agent production scars. [Star to follow →](https://github.com/qiushu-wq/arbiter)
