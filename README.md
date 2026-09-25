# StockPilot

StockPilot V0.1 是 A 股看盘与 AI 辅助分析应用。当前已完成 P0 行情数据链、REST API 和 Web 行情页面；Agent、Trace 与评测能力按 `TODO.md` 分阶段实现。

## 启动后端

需要 [uv](https://docs.astral.sh/uv/)。在 `backend/` 目录运行：

```powershell
uv sync
uv run uvicorn app.main:app --reload
```

访问 `http://127.0.0.1:8000/health`，应返回 `{"status":"ok"}`。可将根目录 `.env.example` 复制为 `backend/.env` 配置环境变量；不要提交真实密钥。

需要预先创建 SQLite 表时，在 `backend/` 目录运行：

```powershell
uv run python -c "from app.database.session import create_database_engine, init_db; init_db(create_database_engine())"
```

后端启动时会自动创建数据库表。可访问 `/docs` 查看 API 文档；当前提供指数及分时、基础市场概览、股票搜索、单只/批量行情、日/周 K 线和自选股增删查。行情响应包含 `stale` 标记；资金流、新闻、市场涨跌家数等 P1 能力尚未接入。

## 启动前端

需要 Node.js 和 npm。在 `frontend/` 目录运行：

```powershell
npm install
npm run dev
```

访问 `http://localhost:3000`。前端默认连接 `http://localhost:8000`，可参考 `frontend/.env.example` 设置 `NEXT_PUBLIC_API_BASE_URL`。首页提供三大指数、分时走势、搜索和自选股；个股详情提供基础行情与日/周 K 线。数据源不可用时会显示重试提示，若后端有最近成功缓存则标注旧数据。市场温度、资金流、新闻及 Agent 目前只显示待接入状态，不会展示模拟行情。

## 检查

```powershell
cd backend; uv run pytest
cd ../frontend; npm run lint; npx tsc --noEmit; npm run build
```
