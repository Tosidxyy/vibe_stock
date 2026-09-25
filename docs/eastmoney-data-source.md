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

## 2. 已验证 Endpoint

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
