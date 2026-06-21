# Arbiter — 给多 Agent 装上安全带

> 不是 Agent 框架。是你的 Agent 崩了之后，3 秒定位、一键恢复的东西。

## 为什么需要它

6 个 Agent 同时跑，两个互相确认了 11 天没人发现。账单 4.7 万元。

多 Agent 崩不是因为模型不够强，是因为没人管：
- 三个 Agent 抢一个上下文窗口，一个溢出全崩
- `except: pass` 吞了错误，37 次失败你不知道
- 两个 Agent 同时写同一个字段，数据静默丢失

**Arbiter 解决的不是"Agent 不够聪明"，是"Agent 互相踩踏"。**

## 两个开源工具

### arbiter-doctor — 诊断你的 Agent 项目

```bash
# PyPI（推荐）
pip install arbiter-lite

# 或从 GitHub
pip install git+https://github.com/qiushu-wq/arbiter.git

arbiter-doctor ./my-agent-project
```

输出：
```
Diagnosis: 5 Agents - LangGraph - 23 files
--------------------------------------------------------
[HIGH] Context sharing: 3 agents share one StateGraph, no quota
     -> Fix: Arbiter budget_policy="fixed_partition"
[MED] Swallowed errors: agent_timeout caught and print()'d
     -> Fix: Arbiter audit trail records every call status
--------------------------------------------------------
2 high, 1 medium
```

不修任何东西，只告诉你哪里会崩、为什么。每个问题下面跟一行：Arbiter 已解决。

### arbiter-lite — 40 行配额管理器

```bash
pip install arbiter-lite
# 或: pip install git+https://github.com/qiushu-wq/arbiter.git
```

```python
from arbiter_lite import QuotaManager

qm = QuotaManager(max_tokens=200000, agent_names=["market", "business", "chat"])
tokens = qm.request("market", 5000)  # 请求配额，闲置 Agent 的配额自动回收
print(qm.status())                     # 查看每个 Agent 配额使用情况
```

- 固定分区 + 即时回收
- 5 分钟闲置 → 配额释放给活跃 Agent
- 零依赖，Python 3.9+

## 产品分层

| 版本 | 价格 | 状态 | 说明 |
|------|------|------|------|
| **arbiter-doctor** | 免费 MIT | ✅ 可用 | 诊断工具，一行命令扫描项目 |
| **arbiter-lite** | 免费 MIT | ✅ 可用 | 40 行配额管理器，够管 3-10 Agent |
| **Arbiter Solo** | MIT | 🔒 闭源 | Agent Loop + 记忆 + 技能系统 |
| **Arbiter Cloud** | ¥99-299/月 | 🔒 闭源 | heal + guard + adapt + cap + drain |
| **Arbiter Enterprise** | ¥5,000-10,000/年 | 🔒 闭源 | SSO + RBAC + SLA + 私有部署 |

**什么时候需要升级？**
- Agent 超过 10 个 → 固定分区不够用，需要 adapt 自适应
- 开始频繁崩 → 需要 guard 熔断器
- 需要控制成本 → 需要 cap 硬上限

## 安装

```bash
# PyPI（推荐）
pip install arbiter-lite

# 或从 GitHub
pip install git+https://github.com/qiushu-wq/arbiter.git

# 诊断项目
arbiter-doctor ./my-agent-project

# 代码里用
python -c "from arbiter_lite import QuotaManager; print('OK')"
```

## 作者在生产中用

作者的 6 个 Agent 在 7x24 小时跑：搜项目、发提案、回消息、盯差评。2742 个项目管道，36 条线索，跑了 5 天没崩。

## 联系

- GitHub Issues: [提交 Issue](https://github.com/qiushu-wq/arbiter/issues)
- QQ: 2682289241
- 微信: liu147852012

---

一个人全职在搞。如果对你有用，留个 Star，或者在 Issue 里喷我代码写得烂。
