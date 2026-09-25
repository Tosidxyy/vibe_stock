# StockPilot V0.1 TODO

> `[ ]` 未开始 · `[-]` 进行中 · `[x]` 已完成  
> 完成规则见 `AGENT.md`。

当前阶段：

```text
EastMoney Provider 已实现 → 下一阶段：Service + DB
```

## 1. 初始化

- [x] 建立 `frontend/ backend/ evals/ docs/`
- [x] 放入当前 Markdown 文档
- [x] 创建 `.gitignore`、`.env.example`、`README.md`
- [x] 使用 `uv` 初始化后端
- [x] FastAPI + `GET /health`
- [x] 初始化 Next.js + TypeScript + Tailwind
- [x] 初始化 Commit

验收：前后端可启动，`/health` 返回 200。

## 2. EastMoney Provider

- [x] `MarketDataProvider`
- [x] Quote / Kline / Index / Search 内部模型
- [x] `to_secid()`
- [x] 股票搜索
- [x] 批量实时行情
- [x] 三大指数
- [x] 日 K / 周 K
- [x] 主 / 备 Endpoint
- [x] Timeout / 统一异常
- [x] Provider 基础测试

验收：P0 数据能力均返回内部标准模型。

注：K 线解析与错误路径通过固定响应测试；2026-09-25 本机访问 K 线节点持续断开，在线成功验证待节点恢复后重试。

## 3. Service + DB

- [ ] `StockService`
- [ ] `MarketService`
- [ ] TTL Cache
- [ ] stale 降级
- [ ] SQLite + SQLAlchemy
- [ ] `watchlist`
- [ ] `chat_session`
- [ ] `chat_message`
- [ ] `agent_trace`
- [ ] `WatchlistService`
- [ ] Service / DB 测试

验收：自选股可增删查；Service 不暴露东方财富原始字段。

## 4. REST API

- [ ] Market indices / overview
- [ ] Stock search / quote / kline
- [ ] Watchlist GET / POST / DELETE
- [ ] P1：money-flow
- [ ] P1：news
- [ ] 核心 API 测试

验收：P0 API 足够支撑 Dashboard 和详情页。

## 5. Web 行情

- [ ] Layout / Sidebar / Topbar
- [ ] 三大指数
- [ ] 市场走势图
- [ ] 自选股增删与跳转
- [ ] 市场温度
- [ ] 股票搜索
- [ ] 个股基础行情
- [ ] 日 K / 周 K + 成交量
- [ ] P1：资金流
- [ ] P1：新闻
- [ ] Loading / Empty / Error

验收：整体布局与视觉方向参考 `docs/ui-demo.html`，并与 `design.md` 基本一致；Build / Type Check 通过。

## 6. Agent

- [ ] PydanticAI + 模型配置
- [ ] System Prompt
- [ ] `get_stock_quote`
- [ ] `get_stock_kline`
- [ ] `get_market_indices`
- [ ] `get_watchlist`
- [ ] P1：`get_stock_money_flow`
- [ ] P1：`get_stock_news`
- [ ] `POST /api/agent/chat`
- [ ] Agent Chat 前端
- [ ] Tool 基础测试

验收：通过 `prd.md` 核心 Agent Case。

## 7. Trace

- [ ] Tool / Input / Output Summary / Status / Latency
- [ ] 写入 `agent_trace`
- [ ] Trace 查询 API
- [ ] Dashboard 最近 Trace
- [ ] `/agent` 完整 Trace

验收：成功、失败 Tool 都可观察，不保存私有推理。

## 8. Evaluation

- [ ] 20～50 条 Case
- [ ] 单 Tool / 多 Tool / 自选股 / 股票比较
- [ ] Tool Selection Accuracy
- [ ] Argument Accuracy
- [ ] Task Success Rate
- [ ] CLI 运行 + 失败 Case
- [ ] README 写入真实结果

验收：可重复运行；无模型配置时明确跳过。

## 9. GitHub 收尾

- [ ] README / Quick Start / 环境变量
- [ ] Dashboard 截图
- [ ] Agent + Trace 截图
- [ ] 架构图
- [ ] 免责声明
- [ ] 清理敏感信息 / 临时文件
- [ ] 可选：GIF / Docker / GitHub Actions

## 10. V0.1 验收

- [ ] Dashboard / 搜索 / 详情 / K 线 / 自选股可用
- [ ] Agent 核心任务可用
- [ ] Trace 可用
- [ ] Eval 可真实运行
- [ ] 后端测试通过
- [ ] 前端 Build / Type Check 通过
- [ ] 文档与代码一致
- [ ] Git 历史清晰
- [ ] 无真实 API Key
