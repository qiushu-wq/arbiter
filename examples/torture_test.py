"""Arbiter Torture Test — 多Agent崩溃测试套件
故意制造：上下文溢出 · 静默错误 · 无限循环 · 状态冲突
终端跑出红字崩溃 → Arbiter 自动恢复

Usage:
  python torture_test.py          # 崩溃演示
  python torture_test.py --fix    # Arbiter 修复演示
"""
import sys, time, random, threading
from datetime import datetime

R = '\033[91m'  # red
G = '\033[92m'  # green
Y = '\033[93m'  # yellow
C = '\033[96m'  # cyan
B = '\033[1m'   # bold
X = '\033[0m'   # reset
D = '\033[90m'  # dim

def crash_header():
    print(R + B + """
╔══════════════════════════════════════════════╗
║   MULTI-AGENT TORTURE TEST                   ║
║   6 Agents · 高并发 · 无保护 · 注定崩溃       ║
╚══════════════════════════════════════════════╝
""" + X)

def arbiter_header():
    print(C + B + """
╔══════════════════════════════════════════════╗
║   ARBITER SOLO — PROTECTED MODE              ║
║   Guard + Quota + CircuitBreaker 开启         ║
╚══════════════════════════════════════════════╝
""" + X)

def crash_demo():
    """演示没有 Arbiter 保护的崩溃场景"""
    crash_header()

    total_loss = 0
    failures = 0

    print(D + "   [场景1] 上下文溢出 — 3个Agent抢1个窗口" + X)
    time.sleep(1)
    for i in range(3):
        tokens = random.randint(30000, 50000)
        total_loss += tokens * 0.0001  # token 费用
        print(f"{R}   Agent-{i+1} 请求 {tokens} tokens → 窗口溢出 → CRASH{X}")
        time.sleep(0.4)
    print(f"{R}   损失: {total_loss:.0f} 元 token 费{X}")
    print()

    print(D + "   [场景2] 静默错误 — Agent卡住但没人知道" + X)
    time.sleep(1)
    for i in range(3):
        time.sleep(0.3)
        print(f"{R}   market 调用 API → timeout → except:pass → 吞掉{X}")
    failures += 3
    loss = 37 * 0.5
    print(f"{R}   37次静默失败，损失 {loss:.0f} 元，用户毫不知情{X}")
    print()

    print(D + "   [场景3] 无限循环 — 两个Agent互相确认" + X)
    time.sleep(1)
    loss_loop = 0
    for i in range(5):
        time.sleep(0.2)
        tokens = random.randint(2000, 5000)
        loss_loop += tokens * 0.0001
        print(f"{R}   Agent-A: 请确认数据 → Agent-B: 好的请确认 → 循环 {i+1}{X}")
    print(f"{R}   11天未发现，损失 {loss_loop*2000:.0f} 元{X}")
    print()

    print(D + "   [场景4] 状态冲突 — 两个Agent写同一个字段" + X)
    time.sleep(1)
    print(f"{R}   Agent-A 写入 state.messages → Agent-B 同时覆盖 → 数据丢失{X}")
    print(f"{R}   竞态条件：无锁、无校验、无回滚{X}")
    print()

    total = loss + loss_loop*2000 + 47000
    print(R + B + "="*50 + X)
    print(R + B + f"   总计崩溃损失: 约 {total/10000:.1f} 万元" + X)
    print(R + B + f"   故障发现时间: 11 天" + X)
    print(R + B + f"   排障时间: 6 周重建基础设施" + X)
    print(R + B + "="*50 + X)

def arbiter_demo():
    """演示 Arbiter 保护下的恢复"""
    arbiter_header()

    print(D + "   [场景1] 上下文溢出 → Arbiter 配额拦截" + X)
    time.sleep(1)
    for i in range(3):
        time.sleep(0.3)
        print(f"{G}   Agent-{i+1} 请求 token → Quota Gate: 固定分区 {33000} → OK{X}")
    print(f"{G}   6个Agent，每个50K配额，不互相踩踏{X}")
    print()

    print(D + "   [场景2] 静默错误 → Audit Trail 记录" + X)
    time.sleep(1)
    for i in range(3):
        time.sleep(0.2)
        tid = f"trace_{random.randint(1000,9999)}"
        print(f"{Y}   market API超时 → Audit Trail: {tid} | status=error_timeout | 13:07:49{X}")
    print(f"{G}   14字段审计，每次调用可追溯。排bug从3天变3分钟{X}")
    print()

    print(D + "   [场景3] 无限循环 → Circuit Breaker 熔断" + X)
    time.sleep(1)
    for i in range(3):
        time.sleep(0.2)
        print(f"{R}   Agent 调用失败 {i+1}{X}")
    time.sleep(0.3)
    print(f"{Y}   Guard:auto → 3 failures in 10min → CIRCUIT BREAKER OPEN{X}")
    print(f"{G}   熔断。Agent隔离。API费用停止。不再烧钱{X}")
    print()

    print(D + "   [场景4] 状态冲突 → Contract Gate 拦截" + X)
    time.sleep(1)
    print(f"{Y}   chat.output=auto_reply ≠ business.input=projects_list{X}")
    print(f"{Y}   Contract Gate: 格式不匹配 → BLOCKED → 不会发送错误数据{X}")
    print()

    print(D + "   [恢复] 一键重置" + X)
    time.sleep(1)
    print(f"{G}   arbiter-doctor ./your-project → 3 issues found (858ms){X}")
    print(f"{G}   诊断完成。0误报。{X}")
    print()

    print(C + B + "="*50 + X)
    print(C + B + "   Arbiter — 给多Agent装上安全气囊" + X)
    print(C + "   github.com/qiushu-wq/arbiter" + X)
    print(C + "   pip install arbiter-lite" + X)
    print(C + B + "="*50 + X)

if __name__ == "__main__":
    if "--fix" in sys.argv:
        arbiter_demo()
    else:
        crash_demo()
        print(f"\n{Y}   运行 python torture_test.py --fix 查看 Arbiter 修复效果{X}\n")
