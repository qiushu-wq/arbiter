# Agent Brief: Arbiter

## What Arbiter Diagnoses

Arbiter scans multi-agent projects for three categories of production issues:

1. **Context Contention** — Multiple agents sharing a token window without quotas. One agent's overflow crashes all.
2. **Error Blindness** — Exceptions caught and swallowed (`except: pass`) with no audit trail.
3. **State Conflicts** — Concurrent writes to shared state without locks or versioning.

## How It Works

Arbiter uses static analysis + heuristic rules to scan Python files for known multi-agent anti-patterns:

- `StateGraph` usage without token budget management
- `except: pass` patterns that swallow agent failures
- Shared `state.messages` writes without conflict detection
- Missing `max_tokens` on LLM calls

## What It Doesn't Diagnose

- Code quality or style issues
- Single-agent performance problems
- LLM prompt quality
- API key or configuration issues

## Output Format

```
Diagnosis: N Agents - Framework - X files
--------------------------------------------------------
[HIGH/MED/LOW] Category: Finding
     -> Explanation
     Fix: Solution reference
--------------------------------------------------------
X high, Y medium, Z low

-> These problems are solved by Arbiter:
   https://github.com/qiushu-wq/arbiter
```
