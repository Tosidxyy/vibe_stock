"use client";

import { useEffect, useState } from "react";
import { ApiError, apiRequest, errorText } from "../lib/api";

type Message = { role: "user" | "assistant"; content: string };
type ChatResult = { session_id: string; answer: string };
type StoredSession = { session_id: string; messages: Message[] };

const sessionKey = "stockpilot-agent-session";
const suggestions = ["今天市场怎么样？", "今天我的自选股怎么样？", "东方财富最近五天走势？"];

export function AgentChat({
  compact = false, initialPrompt = "", onSessionChange, onTraceUpdated,
}: {
  compact?: boolean;
  initialPrompt?: string;
  onSessionChange?: (sessionId: string | null) => void;
  onTraceUpdated?: () => void;
}) {
  const [configured, setConfigured] = useState<boolean | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState(initialPrompt);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const stored = window.localStorage.getItem(sessionKey);
    void apiRequest<{ configured: boolean }>("/api/agent/status")
      .then((result) => { if (active) setConfigured(result.configured); })
      .catch(() => { if (active) setConfigured(null); })
      .finally(() => { if (active && !stored) setLoading(false); });
    if (stored) {
      void apiRequest<StoredSession>(`/api/agent/sessions/${encodeURIComponent(stored)}`)
        .then((result) => {
          if (!active) return;
          setSessionId(result.session_id);
          setMessages(result.messages);
          onSessionChange?.(result.session_id);
        })
        .catch(() => {
          if (active) window.localStorage.removeItem(sessionKey);
        })
        .finally(() => { if (active) setLoading(false); });
    }
    return () => { active = false; };
  }, [onSessionChange]);

  const send = async (value = draft) => {
    const message = value.trim();
    if (!message || busy || configured !== true) return;
    setBusy(true);
    setError(null);
    try {
      const response = await apiRequest<ChatResult>("/api/agent/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId }),
      });
      setMessages((current) => [...current, { role: "user", content: message }, { role: "assistant", content: response.answer }]);
      setSessionId(response.session_id);
      onSessionChange?.(response.session_id);
      onTraceUpdated?.();
      window.localStorage.setItem(sessionKey, response.session_id);
      setDraft("");
    } catch (cause) {
      if (cause instanceof ApiError && cause.sessionId) {
        setSessionId(cause.sessionId);
        onSessionChange?.(cause.sessionId);
        window.localStorage.setItem(sessionKey, cause.sessionId);
        onTraceUpdated?.();
      }
      setError(errorText(cause));
    } finally {
      setBusy(false);
    }
  };

  const newChat = () => {
    setMessages([]);
    setSessionId(null);
    onSessionChange?.(null);
    setError(null);
    window.localStorage.removeItem(sessionKey);
  };

  return (
    <div className={`agent-chat ${compact ? "compact" : ""}`}>
      <div className="agent-chat-head">
        <div className="agent-head"><span className="agent-icon">✦</span><div><h2>Stock Agent</h2><small>行情 Tool 驱动的对话</small></div></div>
        {messages.length > 0 && <button className="text-button" type="button" onClick={newChat} disabled={busy}>新对话</button>}
      </div>
      <div className="agent-messages" aria-live="polite">
        {loading ? <div className="agent-empty">正在恢复对话…</div> :
          messages.length === 0 ? <div className="agent-empty"><span className="agent-orb">✦</span><h3>从真实行情开始分析</h3><p>可以查询指数、个股行情、K 线或自选股。回答会区分行情事实与分析。</p></div> :
            messages.map((item, index) => <div className={`agent-message ${item.role}`} key={index}><span>{item.role === "user" ? "你" : "Stock Agent"}</span><p>{item.content}</p></div>)}
        {busy && <div className="agent-message assistant pending"><span>Stock Agent</span><p>正在读取行情并分析…</p></div>}
      </div>
      {configured === false && <p className="agent-config-note">模型尚未配置。请在后端设置模型名称与 API Key 后启动对话。</p>}
      {configured === null && <p className="agent-config-note">无法确认模型状态，请检查后端连接。</p>}
      {error && <p className="inline-error" role="alert">{error}</p>}
      {messages.length === 0 && configured && <div className="agent-suggestions">{suggestions.map((item) => <button key={item} type="button" onClick={() => void send(item)} disabled={busy}>{item}</button>)}</div>}
      <form className="agent-composer" onSubmit={(event) => { event.preventDefault(); void send(); }}>
        <input aria-label="向 Stock Agent 提问" placeholder="询问行情、K 线或自选股…" value={draft} onChange={(event) => setDraft(event.target.value)} disabled={busy || configured !== true} maxLength={2000} />
        <button type="submit" disabled={busy || configured !== true || !draft.trim()} aria-label="发送消息">发送</button>
      </form>
      <p className="agent-disclaimer">行情信息仅供参考，不构成投资建议。</p>
    </div>
  );
}
