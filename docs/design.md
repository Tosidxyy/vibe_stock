# StockPilot V0.1 界面设计文档

> 职责：定义“页面如何呈现”。产品范围见 `prd.md`。  
> 前端实现时优先参考 `ui-demo.html`，该文件作为 V0.1 的视觉与布局基线；允许根据真实数据和组件实现做合理调整，但不要无理由完全重做整体风格。

## 1. 设计定位

方向：

> **金融 Dashboard + AI Copilot + Developer Portfolio**

关键词：深色、简洁、技术感、信息密度适中、Agent 突出。

避免：完整复刻券商终端、过多指标、过度动画、独立套壳 Chat UI。

## 2. 视觉规范

```text
背景        #0A0D12
一级卡片    #10141B
二级卡片    #151A22
边框        #222A35
主文字      #EDF2F7
次文字      #8D98A8
强调色      #6EA8FE
辅助色      #8B5CF6
上涨        #F05252
下跌        #22C55E
```

A 股习惯：**红涨、绿跌**。

字体：`Inter / system-ui / PingFang SC / Microsoft YaHei`。Tool / Trace 可用等宽字体。

## 3. 全局布局

```text
┌───────────┬────────────────────────────────────┐
│ Sidebar   │ Topbar：搜索 / 市场状态            │
│           ├──────────────────────┬─────────────┤
│ 市场概览  │ 行情主区域           │ Agent Chat  │
│ 自选股    │ 指数 / 图表 / 自选股 ├─────────────┤
│ AI Agent  │                      │ Agent Trace │
└───────────┴──────────────────────┴─────────────┘
```

建议：
- Sidebar：约 220px
- Agent 列：380～430px
- 主内容：自适应
- Desktop First，重点 ≥1280px

Sidebar：
- 市场概览
- 自选股
- AI Agent
- Agent Eval（P1）

## 4. Dashboard `/`

### 顶部
- `市场概览`
- 股票代码 / 名称搜索
- 交易状态、数据延迟

### 三大指数
上证、深证、创业板；展示点位、涨跌幅、涨跌额、成交额。

### 市场走势
默认上证分时；展示当前、高低、成交额和 ECharts Line。

### 自选股
字段：

```text
股票 | 现价 | 涨跌幅 | 成交额 | 换手率
```

点击进入 `/stock/[code]`。

### 市场温度
上涨家数、下跌家数、涨停家数、两市成交额。

当前 P0 API 尚无全市场统计，页面保留真实数据占位；该模块待 P1 数据能力接入后完成。

### Agent
首页保持可见，提供输入框和快捷问题：

```text
今天市场怎么样？
分析我的自选股
分析东方财富
比较宁德时代和比亚迪
```

旁边显示最近一次 Trace。

Web 行情阶段只保留 Agent 与 Trace 的可见预留区域；输入与快捷问题在 Agent 阶段接入真实功能。

## 5. 个股详情 `/stock/[code]`

顺序：

```text
股票头部 → 基础行情 → K线/成交量 → 资金流 → 新闻 → AI快捷分析
```

股票头部示例：

```text
宁德时代 300750 · 深交所
251.30   +1.72%
```

支持加入 / 移出自选。

K 线：
- `日 K | 周 K`
- ECharts Candlestick + Volume
- V0.1 不强制 MACD / KDJ / RSI

AI 快捷入口：

```text
分析今日表现
分析最近 5 日
总结相关新闻
```

资金流与新闻当前仅显示 P1 数据待接入；AI 快捷入口在 Agent 阶段启用。

## 6. Agent 工作台 `/agent`

```text
┌───────────────────────────┬─────────────────────┐
│ Chat                      │ Execution Trace     │
│                           │ Tool Input / Output │
└───────────────────────────┴─────────────────────┘
```

Agent 回答优先使用简洁结构化信息。

Trace：

```text
✓ get_watchlist       42ms
✓ get_stock_quote    287ms
✓ generate_response  981ms
```

展开查看 Input、Output Summary、Status、Latency。

## 7. Agent Eval（P1）

只展示：

```text
Tool Selection Accuracy
Argument Accuracy
Task Success Rate
```

附少量失败 Case，定位为工程调试页。

## 8. 通用状态

- Loading：Skeleton
- Error：简洁错误 + 必要时重试
- Empty：给出下一步操作
- 数据源旧缓存：显示 `stale` 提示

窄屏时 Sidebar 收起，Agent 下移，表格允许横向滚动。

## 9. 设计原则

1. 数据可读性优先。
2. Agent 融入看盘流程，不做独立聊天套壳。
3. Trace 清晰可见但不抢主内容。
4. 无明确用途的模块不加入首页。
5. 以 `docs/ui-demo.html` 为 V0.1 视觉基线；明显偏离布局、信息层级或整体风格时，应先同步更新本文。
