# StockPilot V0.1 技术架构文档

> 职责：定义“怎么实现”。东方财富细节见 `eastmoney-data-source.md`。

## 1. 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Next.js + React + TypeScript + Tailwind CSS |
| 图表 | Apache ECharts |
| 后端 | FastAPI + Pydantic |
| HTTP | httpx.AsyncClient |
| 数据 | SQLAlchemy + SQLite |
| 缓存 | cachetools.TTLCache |
| Agent | PydanticAI |
| LLM | DeepSeek / OpenAI-compatible API |
| Eval | pydantic-evals |
| 测试 | pytest |
| Python 管理 | uv |

V0.1 不主动引入 LangChain、LangGraph、Redis、PostgreSQL、Vector DB、Celery、Kafka、Kubernetes。

## 2. 总体架构

```text
Next.js
   │ REST
FastAPI Route
   ├──────────── Agent
   │               │ Tool
   └───────┬───────┘
           ▼
       Service Layer
        │         │
    TTL Cache   MarketDataProvider
                  │
            EastMoneyProvider
                  │
              东方财富

Supporting: SQLite / Trace / Evaluation
```

统一依赖方向：

```text
Frontend → Route → Service → Provider
Agent Tool → Service → Provider / Database
```

## 3. 仓库结构

以下是 V0.1 的目标结构；初始化阶段已建立 `frontend/`、`backend/app/core/`、`backend/tests/`、`evals/` 和 `docs/`。其余业务目录随对应 TODO 阶段创建。

```text
stockpilot/
├── frontend/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agent/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── providers/
│   │   ├── services/
│   │   └── main.py
│   └── tests/
├── evals/
├── docs/
│   ├── prd.md
│   ├── design.md
│   ├── architecture.md
│   ├── eastmoney-data-source.md
│   └── ui-demo.html
├── TODO.md
├── AGENT.md
├── README.md
└── .env.example
```

## 4. 后端分层

### API
只负责 HTTP 参数、依赖注入、调用 Service / Agent、状态码。

### Service
负责业务组合、缓存、批量查询、自选股聚合和降级。

核心：

```text
StockService
MarketService
WatchlistService
```

### Provider
`MarketDataProvider` 定义统一接口，`EastMoneyProvider` 实现：
- `secid` / Endpoint 等东方财富细节
- HTTP 请求
- 主备节点
- 原始字段解析
- Provider 异常
- 转换为内部 Pydantic Model

东方财富 `fX` 字段不得进入 Service、Agent 或前端。

## 5. 内部模型

核心模型：

```text
StockQuote
KlineItem
MarketIndex
IntradayPoint
MoneyFlow
StockNews
SymbolSearchResult
```

数据流：

```text
EastMoney Raw → Provider → Pydantic Model → Service → API / Tool
```

## 6. 异步与缓存

统一使用 `httpx.AsyncClient`；需要并发时使用 `asyncio.gather()`。

优先使用东方财富批量行情接口，避免自选股逐只请求。

建议 TTL：

```text
行情 / 指数  3～5 秒
K 线         30～60 秒
资金流       30～60 秒
新闻         3～5 分钟
```

Provider 短暂失败且存在旧缓存时，可返回：

```text
stale=true
```

## 7. 数据库

SQLite + SQLAlchemy。

V0.1 表：

```text
watchlist
chat_session
chat_message
agent_trace
```

Trace 至少保存：

```text
session_id / step_index / tool_name / tool_input
tool_output_summary / status / latency_ms / created_at
```

## 8. API

初始化阶段已实现 `GET /health`，返回 `{"status":"ok"}`。下列业务 API 仍属后续阶段。

```text
GET    /api/market/indices
GET    /api/market/overview

GET    /api/stocks/search?q=
GET    /api/stocks/{code}/quote
GET    /api/stocks/{code}/kline
GET    /api/stocks/{code}/money-flow
GET    /api/stocks/{code}/news

GET    /api/watchlist
POST   /api/watchlist
DELETE /api/watchlist/{code}

POST   /api/agent/chat
GET    /api/agent/traces/{session_id}
```

P1 API 可在对应能力实现后启用。

## 9. Agent

```text
User
→ PydanticAI
→ Tool
→ Service
→ Provider / DB
→ Tool Result
→ Final Answer
```

Tool 只做：
- 参数 Schema
- Service 调用
- 结构化返回

配置：

```text
MODEL_NAME
MODEL_API_KEY
MODEL_BASE_URL
```

Agent 不硬编码模型 Key。

## 10. Trace

Tool 执行时：

```text
计时 → 执行 → 记录 Input → Output Summary → Status → Latency → 持久化
```

不保存模型私有推理。

## 11. Evaluation

```text
evals/
├── datasets/
│   ├── tool_selection.yaml
│   ├── arguments.yaml
│   └── workflow.yaml
└── run_eval.py
```

指标：

```text
Tool Selection Accuracy
Argument Accuracy
Task Success Rate
```

未配置模型则明确跳过，不伪造结果。

## 12. 测试

重点：
- Provider：代码转换、字段解析、备用节点、异常
- Service：缓存、批量聚合、stale 降级
- API：正常 / 参数错误 / Provider 不可用
- Tool：参数、Service 调用、返回 Schema
- 前端：Build / Type Check + 核心页面人工检查

执行流程见根目录 `AGENT.md`。

## 13. 环境变量

根目录 `.env.example` 提供示例；后端从 `backend/.env` 读取本地配置。初始化阶段配置模块已定义以下字段，尚未连接模型或数据库：

```text
APP_NAME=StockPilot
ENVIRONMENT=development
MODEL_NAME=
MODEL_API_KEY=
MODEL_BASE_URL=
DATABASE_URL=sqlite:///./stockpilot.db
MARKET_DATA_PROVIDER=eastmoney
```

## 14. 架构决策

1. Provider 抽象，不让业务层直接爬接口。
2. Async HTTP，不使用阻塞式 requests。
3. 批量行情优先。
4. 指标优先基于 K 线本地计算。
5. TTLCache 优先于 Redis。
6. 单 Agent + Tool Calling 优先于复杂 Workflow。
7. Trace + Eval 优先于继续堆功能。
