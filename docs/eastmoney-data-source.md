# 东方财富数据源实现参考

> 职责：记录旧项目中已经验证过的东方财富数据访问方式。公开 Web 接口可能变化，开发时必须重新测试。

## 1. 旧项目结论

旧项目已验证：

```text
Service
→ EastMoneyClient
→ 东方财富接口
→ 领域模型
```

成熟做法：
- 批量行情
- `secid` 转换
- 主 / 备节点
- 统一数据源异常
- Service 缓存与 stale 降级
- 技术指标基于 K 线本地计算
- Agent 不直接访问东方财富

StockPilot 改为：

```text
Service
→ MarketDataProvider
→ EastMoneyProvider
→ httpx.AsyncClient
```

## 2. 旧项目已验证 Endpoint

| 能力 | Endpoint |
|---|---|
| 批量行情 | `push2.eastmoney.com/api/qt/ulist.np/get` |
| 批量行情备用 | `push2delay.eastmoney.com/api/qt/ulist.np/get` |
| 分时 | `push2.eastmoney.com/api/qt/stock/trends2/get` |
| 分时备用 | `push2delay.eastmoney.com/api/qt/stock/trends2/get` |
| K 线 | `push2his.eastmoney.com/api/qt/stock/kline/get` |
| 股票搜索 | `searchapi.eastmoney.com/api/suggest/get` |

资金流、新闻、公告在新项目开发时单独验证，不预设未经验证的 Endpoint。

## 3. secid

```text
600519 → 1.600519
000001 → 0.000001
300750 → 0.300750
```

统一实现：

```python
to_secid(symbol: str) -> str
```

无效代码抛 `InvalidSymbolError`。

## 4. 批量行情

使用 `ulist.np/get` + `secids` 一次请求多只股票。

优先用于：
- Dashboard 自选股
- Agent 自选股总结
- 多股票行情比较

旧项目常见字段：

```text
f2 最新价
f3 涨跌幅
f5 成交量
f9 市盈率
f15 最高价
```

`fX` 必须在 Provider 内转换为内部模型。

## 5. 分时与 K 线

分时：`stock/trends2/get`
- 解析 `data.trends`
- 只保留最新交易日
- 保留主 / 备节点

K 线：`stock/kline/get`

旧项目已验证：

```text
klt=101  日 K
fqt=0    不复权
lmt      数量
```

新项目上层只传：

```text
period="daily" / "weekly"
```

具体参数映射在 Provider 内。

## 6. 股票搜索

接口：`searchapi.eastmoney.com/api/suggest/get`

旧项目使用：

```text
type=14
count=20
Classify == "AStock"
```

Provider / Service 负责过滤、去重和排序。

## 7. 请求与异常

旧项目：`requests.Session`，Connect Timeout 约 1.5s、Read Timeout 约 3s。

StockPilot：改用 `httpx.AsyncClient`，保留：
- 合理 Timeout
- 主 / 备 Endpoint
- 最近成功节点优先
- 网络、非 JSON、异常 rc 统一为 Provider 异常

建议异常：

```text
DataSourceError
ProviderTimeoutError
InvalidSymbolError
```

原始 httpx 异常不直接暴露给 API / Agent。

## 8. 缓存与 stale

旧项目已验证缓存降级思路。

StockPilot 建议：

```text
行情 / 指数  3～5 秒
K 线         30～60 秒
新闻         3～5 分钟
```

数据源失败但有旧缓存：

```text
stale=true
```

Agent 应能提示当前使用缓存数据。

## 9. 本地指标

旧项目基于 K 线本地计算：

```text
MA / EMA / RSI / MACD / 波动率
区间收益 / 区间最高 / 最低
```

StockPilot 继续保留此原则；V0.1 按需实现，不一次性堆指标。

## 10. 迁移结论

保留：

```text
secid / 批量行情 / 主备节点 / 统一异常 / 缓存降级 / 本地计算
```

升级：

```text
EastMoneyClient  → MarketDataProvider + EastMoneyProvider
requests.Session → httpx.AsyncClient
Desktop 调用     → FastAPI + Agent Web
```

开发 Provider 时优先参考旧项目已通过测试的请求参数，再用 StockPilot 测试确认当前接口仍可用。

## 11. StockPilot 当前实现与在线验证（2026-09-25）

- `to_secid()` 接收六位 A 股代码：`6` 开头映射沪市，`0` / `3` 开头映射深市，`4` / `8` 开头映射北交所；其他代码抛 `InvalidSymbolError`。
- `search_stocks()` 请求 `input`、`type=14`、`count`，仅保留 `Classify=AStock` 并去重。接口无匹配时返回 `Data=null`、`TotalCount=0`，Provider 转为空列表。
- `get_quotes()` 一次发送多个 `secid`。`f2` / `f3` / `f4` 等价格和涨跌字段除以 100；`f5` 保留原始成交量数值，`f6` 保留原始成交额数值；缺失或 `-` 转为 `None`。
- `get_indices()` 用 `1.000001`、`0.399001`、`0.399006` 一次获取上证、深证、创业板指数，并要求三项齐全。
- 行情和指数优先最近成功节点，主节点请求失败、返回异常或数据结构不合法时尝试 `push2delay`。超时、HTTP 错误、非 JSON 和异常 `rc` 转为统一 Provider 异常。
- `get_kline()` 用 `klt=101` / `102` 表示日 K / 周 K、`fqt=0` 表示不复权，并解析逗号分隔的 K 线。空 K 线作为数据源失败处理，避免把接口受限误报为无历史数据。

本机在线请求已确认搜索、无结果搜索、批量行情及备用节点指数响应结构。`push2his.eastmoney.com` 在本次验证中持续断开连接；日 K / 周 K 的解析和错误路径已用固定响应测试，但当前网络环境无法完成 K 线在线成功验证。后续接入 Service 前需重试该节点。
