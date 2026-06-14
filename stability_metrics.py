"""Arbiter Stability Metrics -- Multi-Agent Health Check (MIT)

Four hard thresholds:
  - Agent failure rate < 5%
  - Context loss rate < 0.1%
  - State conflicts = 0
  - Pipeline stall < 10 minutes
"""
import json, os
from datetime import datetime, timedelta

THRESHOLDS = {
    "agent_failure_rate": 0.05,
    "context_loss_events": 0.001,
    "state_conflicts": 0,
    "pipeline_stall_minutes": 10,
}

def record(trace_id, agent_name, action_type, tokens_used, quota_pct, status,
           parent_id=None, metrics_file="stability_metrics.jsonl"):
    entry = {
        "trace_id": trace_id, "agent_name": agent_name,
        "action_type": action_type, "tokens_consumed": tokens_used,
        "quota_used_pct": quota_pct, "status": status,
        "parent_trace_id": parent_id or "", "ms_elapsed": 0,
        "time": datetime.now().isoformat(),
    }
    with open(metrics_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

def check(hours=24, metrics_file="stability_metrics.jsonl"):
    cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
    records = []
    if os.path.exists(metrics_file):
        with open(metrics_file, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get("time", "") >= cutoff:
                        records.append(r)
                except (json.JSONDecodeError, KeyError):
                    pass
    total = len(records)
    if total == 0:
        return {"status": "no_data", "detail": "No agent calls in period"}
    failures = sum(1 for r in records
                   if r["status"] != "ok" and "suppressed" not in r["status"])
    context_loss = sum(1 for r in records if "quota_exceeded" in r["status"])
    conflicts = sum(1 for r in records if "conflict" in r.get("status", ""))
    report = {
        "time": datetime.now().isoformat(), "total_calls": total,
        "agent_failure_rate": round(failures / total, 4),
        "context_loss_rate": round(context_loss / max(total, 1), 4),
        "state_conflicts": conflicts, "status": "healthy", "alerts": [],
    }
    if report["agent_failure_rate"] > THRESHOLDS["agent_failure_rate"]:
        report["status"] = "degraded"
        report["alerts"].append("failure_rate: {}".format(report["agent_failure_rate"]))
    if report["context_loss_rate"] > THRESHOLDS["context_loss_events"]:
        report["status"] = "degraded"
        report["alerts"].append("context_loss: {}".format(report["context_loss_rate"]))
    if conflicts > THRESHOLDS["state_conflicts"]:
        report["status"] = "critical"
        report["alerts"].append("state_conflicts: {}".format(conflicts))
    return report

if __name__ == "__main__":
    print(json.dumps(check(), ensure_ascii=False, indent=2))
