"use client";

import { useState } from "react";
import { AgentChat } from "./AgentChat";
import { TracePanel } from "./TracePanel";

export function AgentWorkspace({ initialPrompt }: { initialPrompt: string }) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [traceVersion, setTraceVersion] = useState(0);
  return (
    <div className="agent-page-grid">
      <section className="card agent-workspace">
        <AgentChat
          initialPrompt={initialPrompt}
          onSessionChange={setSessionId}
          onTraceUpdated={() => setTraceVersion((value) => value + 1)}
        />
      </section>
      <aside className="card trace-card"><TracePanel sessionId={sessionId} version={traceVersion} /></aside>
    </div>
  );
}
