# Arbiter Solo · 个人级 Agent 架构

> 基于 Claude Agent SDK / OpenAI Agents SDK / Google ADK + 2026 个人 Agent 部署模式
> 推演出的适配 Arbiter 体系的个人级架构
> 
> 2026-06-16 · v1.0 · Architecture Review 闭环

---

## 一、架构定位

```
Arbiter Solo（个人级）
    ↓ 用到
Arbiter Lite（budget_policy + audit + status + trace）
    ↓ Agent 多了升级到
Arbiter Cloud（heal + guard + adapt）
    ↓ 企业部署升级到
Arbiter Enterprise（SSO + RBAC + SLA）
```

Solo 不是新产品。它是 Arbiter Lite + Agent Loop + 记忆 + 技能系统，面向单用户。

---

## 二、五层结构

```
┌─────────────────────────────────────────────────────────┐
│                     Layer 1: 界面                        │
│  arbiter solo chat · run · daemon · status · search     │
└────────────────────────┬────────────────────────────────┘
┌────────────────────────▼────────────────────────────────┐
│                  Layer 2: Agent 循环                      │
│  每一步过三道门：安全门 → 配额门 → 审计门                  │
│  + post-loop hook 生成 compact 汇总行                     │
│  + 失败反馈闭环（上一轮 error 注入下一轮 context）          │
└────────────────────────┬────────────────────────────────┘
┌────────────────────────▼────────────────────────────────┐
│                Layer 3: 模型路由                          │
│  agent.toml 声明 Agent 级模型路由（不依赖 LiteLLM）        │
│  API Key 只用环境变量/.env，不存 toml                      │
└────────────────────────┬────────────────────────────────┘
┌────────────────────────▼────────────────────────────────┐
│                Layer 4: 记忆系统                          │
│  Tier 1: Profile (~5KB, 总是加载)                        │
│  Tier 2: Project Context (按需加载)                       │
│  Tier 3: 审计轨迹结构化查询（agent_name + task 字段过滤）   │
│  存储: JSONL（审计） + metadata.json（摘要索引）            │
│  搜索: 写入时标准化 + 热数据窗口（30天）+ --all 全量搜索     │
└────────────────────────┬────────────────────────────────┘
┌────────────────────────▼────────────────────────────────┐
│                Layer 5: 工具 & 沙箱                       │
│  MCP Servers + Sandbox + Skills（兼容 SKILL.md 格式）     │
│  Guard: confirm（安全门，session 级授权）                  │
│  工具映射: Read/Write/Bash → mcp:filesystem/mcp:shell     │
└─────────────────────────────────────────────────────────┘
```

---

## 三、Agent 组合模型

### 两个原语

| 原语 | 用途 | 执行逻辑 |
|------|------|---------|
| **Sequential** | 有先后顺序的任务 | A 完成 → B 开始 → C 开始 |
| **Parallel** | 互不依赖的任务 | 间隔 500ms 排队发出（快速串行，避免 API 429） |

Router 和 Loop 留给 Cloud 版。dependent parallel 就是 Sequential，不重复发明。

### Executor 统一异常分类

Executor（执行 Agent 调用的那一层）统一分类异常 → recoverable 三态：

| recoverable | 场景 | 调度器行为 |
|-------------|------|-----------|
| false | 未捕获异常 | Parallel 继续，跳过错的那个 |
| true | 超时 | 可重试 |
| deferred | 被 guard 跳过 | guard 恢复后重试 |

---

## 四、Guard 体系

| | Guard: confirm | Guard: auto |
|------|---------------|------------|
| **用途** | 安全门 — 危险操作前确认 | 熔断器 — 连续失败自动隔离 |
| **Solo 版** | ✅ 有 | ❌ 无（Cloud 专属） |
| **交互** | session 级授权，daemon 过期自动 deny | Solo 人工重置 `arbiter solo reset --agent=X` |
| **通知** | 阻塞任务自动跳过 + 审计记录 | status 面板显示熔断状态 |

---

## 五、数据模型

### 存储

- **审计轨迹**: JSONL 追加写（Solo 和 Cloud 统一格式）
- **摘要索引**: metadata.json（每 50 条新记录更新一次，daemon 退出时强制 flush）
- **配置**: agent.toml（不存凭据）

### Solo ↔ Cloud 数据流

- 升级: `arbiter cloud import --from-solo`
- 降级: `arbiter solo sync --from-cloud`（只拉 Solo 认得的字段，Cloud 特有字段保留在 `_cloud_extra`）
- 版本契约: `_cloud_contract_version` 字段防不匹配

### 管理操作审计

admin 操作也写入审计轨迹，用 `admin_` 前缀区分。面板计算指标时排除 admin 操作。管理操作带 severity 标签——用户主动触发=info，触发时系统存在异常指标=warning。

---

## 六、搜索

- **写入时**: 内容字段（task/context/output）标准化——全角转半角、去零宽空格。原始字段保留在 `_raw` 中
- **搜索时**: 用户输入 trim + 去重空格 + Unicode 标准化
- **默认**: 热数据窗口（30 天内），SQLite LIKE 查询
- **全量**: `arbiter solo search --all`，实时进度条（显示速率，不给分母预估）
- **归档**: 超过 30 天的记录 `arbiter solo clean` 归档，raw 保留、normalized 删除

---

## 七、CLI 命令

| 命令 | 用途 |
|------|------|
| `arbiter solo chat` | 交互式对话（优先读环境变量，fallback .env） |
| `arbiter solo run` | 单次执行 |
| `arbiter solo daemon` | 常驻后台（用 .env） |
| `arbiter solo status` | 状态面板（`--watch` 原地刷新，`--no-ansi` 降级纯文本） |
| `arbiter solo search <关键词>` | 搜索审计轨迹 |
| `arbiter solo diagnose --agent=X` | Agent 级诊断 |
| `arbiter solo reset --agent=X` | 手动重置熔断 |
| `arbiter solo auth renew` | 刷新 guard session 授权 |
| `arbiter solo clean` | 清理归档超过 30 天的记录 |

---

## 八、v1 交付清单

首版 Solo = 7 样：

1. Agent Loop（while 循环 + 三道门 + post-loop compact 汇总 + 失败反馈闭环）
2. Sequential + Parallel 两个组合原语
3. 三层记忆（Tier 1+2 面板 + Tier 3 审计轨迹查询）
4. Guard: confirm（session 级授权，daemon 降级 deny）
5. agent.toml Agent 级模型路由
6. 三个 CLI 命令（chat / run / status）
7. SKILL.md 兼容（Read/Write/Bash 三个工具硬编码映射 + tool-map.toml 用户扩展）

以下标记为 v2 预研：
- deferred_task_queue 自动重试
- Guard: auto 熔断器（Solo 版最小实现）
- diagnose 上次成功修复命令记忆
- status 面板条件提示（配额低正常/异常判断）
- 管理操作 severity 系统健康度快照

---

## 九、设计原则

1. **Solo 是 Runtime，不是 OS。** 提供原语、执行请求、返回状态。不替 Agent 做决策
2. **痛点是升级的触发器，不是功能数量。** Solo 让你看到痛（配额溢出、熔断），Cloud 帮你消除痛
3. **数据格式一致 > 存储引擎一致。** Solo JSONL ↔ Cloud SQL 通过导入/导出命令双向流动
4. **诚实 > 完美。** 做不到的标注"不支持"，搜不到的提示"试试 --all"，数据不足的显示"数据积累中"
5. **简单 > 优雅。** .env 唯一凭据方案，不区分 export。Parallel 就是快速串行，不加依赖队列
6. **不预定义 Cloud 的类型枚举。** Solo 动态聚合 Cloud 数据，版本不匹配时显式报告而非沉默归并

---

## 十、竞品差异化

| 维度 | Claude Agent SDK | OpenAI Agents SDK | Google ADK | Arbiter Solo |
|------|-----------------|-------------------|------------|-------------|
| Agent 循环 | ✅ | ✅ | ✅ | ✅ + 每一步过配额门 + 审计门 |
| Harness/Sandbox | 一体 | ✅ 分离 | 一体 | ✅ 分离 + Guard 门 |
| 记忆 | 三层文件 | SQLiteSession | Memory Bank | ✅ 三层文件 + 审计轨迹查询 |
| Agent 组合 | ❌ | ❌ | ✅ 四种原语 | ✅ 两种原语（Sequential/Parallel） |
| 配额管理 | ❌ | ❌ | ❌ | ✅ Arbiter 原生 |
| 审计轨迹 | ❌ | ❌ | ❌ | ✅ 12 字段结构化 |
| Agent 升级路径 | ❌ | ❌ | ❌ | ✅ Solo → Cloud → Enterprise |
| 单机部署 | CLI | 需要沙箱服务 | 需要 Cloud Run | ✅ pip install 即用 |

---

> Arbiter Solo = Agent Loop（取 Claude）+ Harness/Sandbox 分离（取 OpenAI）+ Agent 组合原语（取 ADK）+ 三层记忆（取 Claude）+ Guard/配额/审计（自己的 Arbiter）+ 声明式 Skills（取社区）= 一个 pip install 就能用的个人 Agent 运行时。
