import Link from "next/link";
import { AgentChat } from "../../components/AgentChat";

export default async function AgentPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  return (
    <main className="content agent-page">
      <nav className="breadcrumb" aria-label="当前位置"><Link href="/">市场概览</Link><span>/</span><span>AI Agent</span></nav>
      <div className="hero"><div><p className="eyebrow">STOCKPILOT / AGENT</p><h1>AI 行情分析</h1><p>通过行情 Tool 查询事实，再让 Agent 帮你整理与理解。</p></div></div>
      <div className="agent-page-grid">
        <section className="card agent-workspace"><AgentChat initialPrompt={q?.slice(0, 2000) ?? ""} /></section>
        <aside className="card trace-card"><div className="section-head"><div><h2>Agent Execution Trace</h2><span>工具执行记录</span></div></div><div className="section-state">Trace 查询与展示将在下一阶段接入。</div></aside>
      </div>
    </main>
  );
}
