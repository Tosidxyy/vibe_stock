# StockPilot AGENT.md

> Codex 规则。任务看 `TODO.md`；按需读取 `docs/`，不要一次加载全部文档。

## 开发闭环

```text
实现 → 简单测试 → 测试通过 → git commit
→ 同步相关 Markdown → 最后更新 TODO.md
```

测试失败不得提交；完成闭环后 TODO 才能标 `[x]`。

## 核心约束

- 数据链：`Route / Tool → Service → MarketDataProvider → EastMoneyProvider`。
- Tool 不直接发 HTTP；东方财富 `fX` 字段只留在 Provider。
- 网络请求用 `httpx.AsyncClient`；批量行情优先批量接口。
- 实时数据必须来自 Tool，失败时不得让模型编造。
- Trace 只记 Tool、输入、结果摘要、状态、耗时，不记私有推理。
- Eval 必须真实运行，不伪造分数。
- 不主动引入 LangChain、LangGraph、Redis、PostgreSQL、Vector DB 等。
- 不提交 `.env`、真实 API Key、临时文件。
- 前端开发优先参考 `docs/ui-demo.html`；除非 `design.md` 已明确更新，否则不要无理由重做整体布局与视觉方向。

## 测试与 Git

- 后端运行相关 `pytest`。
- 前端运行项目已有的 Build / Lint / Type Check。
- 每个完整模块单独 Commit；Commit 前后检查 `git status`。
- 推荐前缀：`feat:` `fix:` `refactor:` `test:` `docs:` `chore:`。

## 文档同步

仅按实际变化更新：

```text
产品范围 / 验收     → docs/prd.md
UI / 交互           → docs/design.md
架构 / API / DB / Tool → docs/architecture.md
东方财富实现约定    → docs/eastmoney-data-source.md
```

最后更新 `TODO.md`；文档改动也要 Commit。

## 每轮结束

```text
完成：
测试：
Commit：
文档：
下一步：
```
