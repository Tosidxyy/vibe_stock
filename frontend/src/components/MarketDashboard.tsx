"use client";

import { useState } from "react";
import { amount, moveClass, number, signed } from "../lib/format";
import type { IntradayPoint, MarketIndex } from "../lib/types";
import { useResource } from "../lib/use-resource";
import { MarketLineChart } from "./Charts";
import { WatchlistPanel } from "./WatchlistPanel";

const indexNames: Record<string, string> = {
  "000001": "上证指数", "399001": "深证成指", "399006": "创业板指",
};

export function MarketDashboard() {
  const [selected, setSelected] = useState("000001");
  const indices = useResource<MarketIndex[]>("/api/market/indices", 30000);
  const trend = useResource<IntradayPoint[]>(`/api/market/indices/${selected}/intraday`, 30000);
  const active = indices.data?.find((item) => item.symbol === selected);

  return (
    <main className="content">
      <div className="hero"><div><p className="eyebrow">STOCKPILOT / OVERVIEW</p><h1>市场概览</h1><p>指数走势、自选股和研究入口集中在一个工作台。</p></div><span className="chip">实时接口 · P0</span></div>

      {indices.loading ? <div className="indices"><div className="card skeleton index-card" /><div className="card skeleton index-card" /><div className="card skeleton index-card" /></div> :
        indices.error && !indices.data ? <div className="card section-state error-state">{indices.error}<button onClick={indices.refresh}>重试</button></div> :
          !indices.data?.length ? <div className="card section-state">暂无指数数据。</div> :
            <section className="indices" aria-label="三大指数">{indices.data.map((index) => (
              <button key={index.symbol} type="button" className={`card index-card ${selected === index.symbol ? "selected" : ""}`} onClick={() => setSelected(index.symbol)} aria-pressed={selected === index.symbol}>
                <span className="kicker">{index.name}</span>
                <span className="index-main"><strong>{number(index.value)}</strong><em className={moveClass(index.change_percent)}>{signed(index.change_percent)}</em></span>
                <span className="index-sub"><span className={moveClass(index.change_amount)}>{signed(index.change_amount, "")}</span><span>成交额 {amount(index.turnover)}</span></span>
              </button>
            ))}</section>}
      {indices.stale && <p className="stale-note">指数使用最近成功数据，行情源暂时不可用。</p>}

      <div className="dashboard-grid">
        <div className="left-col">
          <section className="card market-card" aria-labelledby="trend-title">
            <div className="section-head"><div><h2 id="trend-title">{indexNames[selected]} · 分时走势</h2><span>{trend.data?.length ? trend.data[trend.data.length - 1].time.slice(0, 10) : "最新交易日"}</span></div><span className="soft-label">09:30 — 15:00</span></div>
            <div className="market-meta">
              <div className="metric"><span>最新</span><strong>{number(active?.value)}</strong></div>
              <div className="metric"><span>涨跌幅</span><strong className={moveClass(active?.change_percent)}>{signed(active?.change_percent)}</strong></div>
              <div className="metric"><span>最高</span><strong>{number(active?.high)}</strong></div>
              <div className="metric"><span>最低</span><strong>{number(active?.low)}</strong></div>
              <div className="metric"><span>成交额</span><strong>{amount(active?.turnover)}</strong></div>
            </div>
            <div className="chart-wrap">
              {trend.loading ? <div className="chart skeleton" /> :
                trend.error && !trend.data ? <div className="section-state error-state">{trend.error}<button onClick={trend.refresh}>重试</button></div> :
                  !trend.data?.length ? <div className="section-state">最新交易日暂无分时数据。</div> :
                    <MarketLineChart points={trend.data} name={indexNames[selected]} />}
            </div>
            {trend.stale && <p className="stale-note">分时图使用最近成功数据。</p>}
          </section>

          <WatchlistPanel />

          <section className="card temperature-card" aria-labelledby="temperature-title">
            <div className="section-head"><div><h2 id="temperature-title">市场温度</h2><span>全市场 · P1 数据待接入</span></div></div>
            <div className="overview-grid">
              {["上涨", "下跌", "涨停", "两市成交额"].map((label) => <div className="mini" key={label}><span>{label}</span><strong>—</strong></div>)}
            </div>
            <p className="card-note">当前数据接口不提供全市场涨跌家数；接入后在此显示真实统计。</p>
          </section>
        </div>

        <aside className="right-col" aria-label="智能分析预留区域">
          <section className="card agent-card">
            <div className="agent-head"><span className="agent-icon">✦</span><div><h2>Stock Agent</h2><small>基于真实行情的 Tool Calling</small></div><span className="chip">即将接入</span></div>
            <div className="agent-placeholder"><span className="agent-orb">✦</span><h3>行情分析，下一阶段开启</h3><p>Agent 对话将在接入模型与行情 Tool 后提供。当前请使用上方搜索和左侧看盘功能。</p></div>
            <div className="prompt-preview"><span>分析我的自选股</span><span>比较两只股票</span><span>今天市场怎么样？</span></div>
          </section>
          <section className="card trace-card"><div className="section-head"><div><h2>Agent Execution Trace</h2><span>工具执行记录</span></div></div><div className="section-state">运行 Agent 后会在这里显示真实 Tool 调用。</div></section>
        </aside>
      </div>
      <p className="footnote">StockPilot V0.1 · 行情信息仅供参考，不构成投资建议</p>
    </main>
  );
}
