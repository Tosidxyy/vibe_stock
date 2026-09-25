"use client";

import type { TraceEntry } from "../lib/types";
import { useResource } from "../lib/use-resource";

export function TracePanel({
  sessionId = null, recent = false, version = 0, compact = false,
}: {
  sessionId?: string | null;
  recent?: boolean;
  version?: number;
  compact?: boolean;
}) {
  const path = recent
    ? `/api/agent/traces/recent?limit=${compact ? 4 : 10}&v=${version}`
    : sessionId ? `/api/agent/traces/${encodeURIComponent(sessionId)}?v=${version}` : null;
  const traces = useResource<TraceEntry[]>(path);

  return (
    <>
      <div className="section-head"><div><h2>Agent Execution Trace</h2><span>{recent ? "最近 Tool 调用" : "当前会话 Tool 调用"}</span></div>{traces.data && <span className="soft-label">{traces.data.length} 条</span>}</div>
      {!path ? <div className="section-state">开始对话后可查看每次 Tool 调用。</div> :
        traces.loading ? <div className="section-state">正在加载执行记录…</div> :
          traces.error && !traces.data ? <div className="section-state error-state">{traces.error}<button onClick={traces.refresh}>重试</button></div> :
            !traces.data?.length ? <div className="section-state">暂无 Tool 调用记录。</div> :
              <ol className="trace-list">{traces.data.map((step) => (
                <li className={`trace-step ${step.status}`} key={`${step.session_id}-${step.step_index}`}>
                  <div className="trace-step-head">
                    <span className="trace-status" aria-label={step.status === "success" ? "成功" : "失败"}>{step.status === "success" ? "✓" : "!"}</span>
                    <strong>{step.tool_name}</strong>
                    <span className="trace-latency">{step.latency_ms} ms</span>
                  </div>
                  <p>{step.tool_output_summary}</p>
                  {!compact && <details className="trace-details"><summary>输入与结果摘要</summary><div><span>Input</span><code>{JSON.stringify(step.tool_input)}</code><span>Output Summary</span><code>{step.tool_output_summary}</code></div></details>}
                </li>
              ))}</ol>}
      {traces.error && traces.data && <p className="inline-error">Trace 更新失败：{traces.error}</p>}
    </>
  );
}
