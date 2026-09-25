export default function Home() {
  return (
    <main className="content">
      <div className="page-heading">
        <span className="eyebrow">STOCKPILOT / OVERVIEW</span>
        <h1>市场概览</h1>
        <p>看盘工作台已就绪。行情与智能分析将在后续阶段接入。</p>
      </div>
      <section className="welcome-card" aria-labelledby="welcome-title">
        <div className="welcome-icon">S</div>
        <span className="eyebrow">WORKSPACE READY</span>
        <h2 id="welcome-title">从这里开始看市场</h2>
        <p>当前版本已建立基础界面与服务入口。接下来的阶段将逐步提供指数、自选股和分析能力。</p>
        <div className="feature-list" aria-label="后续模块">
          <span>市场数据</span><span>自选股</span><span>AI 分析</span>
        </div>
      </section>
      <p className="footnote">StockPilot V0.1 · 数据功能开发中</p>
    </main>
  );
}
