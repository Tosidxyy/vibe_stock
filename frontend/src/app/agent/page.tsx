import Link from "next/link";
import { AgentWorkspace } from "../../components/AgentWorkspace";

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
      <AgentWorkspace initialPrompt={q?.slice(0, 2000) ?? ""} />
    </main>
  );
}
