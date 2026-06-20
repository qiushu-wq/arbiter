# Arbiter -- 给多Agent装上安全气囊

> 不是 Agent 框架。是你的 Agent 崩了之后，3秒熔断、告诉你哪一步崩的、一键恢复的东西。

## 为什么需要它

6个Agent同时跑，两个互相确认了11天没人发现。账单 4.7 万元。

多Agent崩不是因为模型不够强，是因为没人管：
- 三个Agent抢一个上下文窗口，一个溢出全崩
- `except: pass` 吞了错误，37次失败你不知道
- 两个Agent同时写同一个字段，数据静默丢失

**Arbiter 解决的不是"Agent 不够聪明"，是"Agent 互相踩踏"。**

## 快速上手

```bash
pip install arbiter-solo
arbiter-solo init          # 生成 agent.toml
arbiter-solo chat           # 开始和 Agent 对话
```

5 行代码接入现有项目：

```python
from arbiter_solo import *
config = Config()
budget = ContextBudget(200000, config.agent_names)
audit = AuditTrail()
loop = AgentLoop(config, budget, audit, Guard())
result = loop.execute("market", "搜索项目")
```

## 做了什么

```
Agent 崩溃 → Circuit Breaker 熔断 → Audit Trail 定位 → 一键恢复
```

- **Circuit Breaker**: 3次失败自动熔断，不再烧 API 费
- **Audit Trail**: 14字段，每次调用可追溯。排bug从3天变3分钟
- **Quota**: 每个Agent固定配额，不互相抢上下文
- **Contract Gate**: 上游输出和下游输入格式对不上 → 直接拦截

[运行崩溃测试]
```bash
python torture_test.py          # 看6个Agent怎么崩的
python torture_test.py --fix    # 看 Arbiter 怎么救的
```

## 产品分层

| 版本 | 价格 | 说明 |
|------|------|------|
| Solo | 免费/MIT | 个人开发者，pip install 即用 |
| Cloud | 1999元/月 | 自适应配额 + 自动熔断 + 自动恢复 |
| Enterprise | 定制 | 私有部署 + SSO + SLA |

## 谁在用

作者自己的 6 个 Agent 在 7x24 小时跑：搜项目、发提案、回消息、盯差评。2665 个项目管道，36 条线索，跑了 5 天没崩。

## 联系

- GitHub Issues: [提交 Issue](https://github.com/qiushu-wq/arbiter/issues)
- QQ: 2682289241
- 微信: liu147852012

---

作者一个人全职在搞。如果对你有用，留个 Star，或者在 Issue 里喷我代码写得烂。
