# Arbiter -- Multi-Agent Runtime

**Arbiter** is the missing runtime for multi-agent systems. It manages context window allocation, tool scheduling, and state persistence -- so your agents don't crash when there are more than 3 of them.

> If LangChain/CrewAI is Express.js, Arbiter is Node.js. It doesn't tell your agents what to do. It keeps them from stepping on each other.

## Why

| Problem | Severity | What Happens |
|---------|----------|--------------|
| Context contention | Critical | 3 agents share a 128K window. One overflows, all crash. |
| Swallowed errors | High | `except: pass`. You lose days debugging invisible failures. |
| State conflicts | High | 2 agents write `state.messages` simultaneously. Data silently lost. |
| Token boundary crashes | Critical | Agent hits context limit mid-call. No warning, just a 400 error. |

Arbiter solves these with a 4-layer architecture: **Context Budget -> Tool Scheduling -> State Persistence -> Audit Trail**.

## Install

```bash
# Claude Code skill (recommended)
npx skills@latest add qiushu-wq/arbiter

# Python tools
pip install git+https://github.com/qiushu-wq/arbiter.git
```

## Tools (MIT, Free Forever)

### Arbiter Doctor -- Multi-Agent Diagnostic

Scan any multi-agent project for context contention, blind spots, and state conflicts.

```bash
arbiter-doctor ./my-agent-project
arbiter-doctor --self    # self-check your dev environment
```

### Arbiter Lite -- Context Quota Manager

40 lines of Python. Fixed partition + instant reclamation.

```python
from arbiter_lite import QuotaManager

qm = QuotaManager(max_tokens=128000, agent_names=["researcher", "writer", "reviewer"])
tokens = qm.request("researcher", 30000)  # Researcher gets up to 30K
# Idle for 5min -> half quota reclaimed for active agents
```

### Stability Metrics -- Health Check Framework

Four hard thresholds for production multi-agent systems.

```python
from stability_metrics import record, check

record(trace_id, agent, action, tokens, quota_pct, status)
report = check(hours=24)  # -> {failure_rate, context_loss, conflicts, status}
```

## Architecture (3 Rings)

```
Ring 1 (Now):    budget + audit + status + doctor + stability
                 + dynamic tool registry (MCP protocol)
                 + preflight syntax/memory checker
Ring 2 (Q3):     guard + heal + adapt + cap + drain + lock
Ring 3 (Q4):     Studio dashboard + enterprise features
```

## What's Implemented vs Planned

| Feature | Ring | Status |
|---------|------|--------|
| ContextBudget (fixed partition + reclaim) | 1 | Done |
| AuditTrail (12-field recording) | 1 | Done |
| Stability Report (4 thresholds) | 1 | Done |
| Doctor Diagnostic Tool | 1 | Done |
| Doctor --self mode | 1 | Done |
| MCP Dynamic Tool Registry | 1 | Done |
| Preflight Checker | 1 | Done |
| Guard (circuit breaker) | 2 | Q3 2026 |
| Heal (auto-recovery) | 2 | Q3 2026 |
| Adapt (learn usage patterns) | 2 | Q3 2026 |
| Cap (hard token limits) | 2 | Q3 2026 |
| Drain (graceful shutdown) | 2 | Q3 2026 |
| Lock (per-project state locks) | 2 | Q3 2026 |
| Studio Dashboard | 3 | Q4 2026 |

## Arbiter Cloud (Commercial, Q3 2026)

When you grow from 6 agents to 60, Lite isn't enough. Cloud adds:

- **Guard**: Circuit breaker -- 3 failures/10min -> auto-fuse
- **Heal**: Auto-recovery from agent failures
- **Adapt**: Learns usage patterns, pre-allocates quota
- **Cap**: Hard token limits per agent per month
- **Drain**: Graceful agent shutdown without losing in-flight tasks
- **Lock**: Per-project state locks to prevent write conflicts

**$99-299/month.** [Join waitlist](https://github.com/qiushu-wq/arbiter)

## License

- `arbiter-doctor`, `arbiter-lite`, `stability-metrics`: MIT -- free forever, use in commercial projects
- Arbiter Cloud & Enterprise: Commercial

---

Built with multi-agent production scars. First deployed on our own 66-agent company.
[Star to follow](https://github.com/qiushu-wq/arbiter)
