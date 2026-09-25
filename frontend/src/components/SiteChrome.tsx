"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { apiRequest } from "../lib/api";
import { StockSearch } from "./StockSearch";

export function SiteChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    void apiRequest<{ status: string }>("/health", { signal: controller.signal })
      .then((result) => setApiConnected(result.status === "ok"))
      .catch((error) => {
        if (!(error instanceof Error && error.name === "AbortError")) setApiConnected(false);
      });
    return () => controller.abort();
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" href="/" aria-label="StockPilot 首页">
          <span className="brand-mark">S</span>
          <span><strong>StockPilot</strong><small>A 股智能看盘</small></span>
        </Link>
        <nav aria-label="主导航">
          <p className="nav-title">Workspace</p>
          <Link className={`nav-link ${pathname === "/" ? "active" : ""}`} href="/" aria-current={pathname === "/" ? "page" : undefined}>
            <span className="nav-dot" />市场概览
          </Link>
          <Link className="nav-link" href="/#watchlist"><span className="nav-dot" />自选股</Link>
          <Link className={`nav-link ${pathname === "/agent" ? "active" : ""}`} href="/agent" aria-current={pathname === "/agent" ? "page" : undefined}><span className="nav-dot" />AI Agent</Link>
          <span className="nav-link muted"><span className="nav-dot" />执行追踪 <small>待接入</small></span>
        </nav>
        <div className="sidebar-footer">
          <div className="status-line"><span className={`status-pulse ${apiConnected === false ? "offline" : ""}`} />
            {apiConnected === null ? "检查 API 连接…" : apiConnected ? "API 已连接" : "API 未连接"}
          </div>
          <small>EastMoney Provider · V0.1</small>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <Link className="mobile-brand" href="/">StockPilot</Link>
          <StockSearch />
          <div className="top-actions"><span className="chip">A 股行情</span><span className="chip subtle">数据以接口为准</span></div>
        </header>
        {children}
      </div>
    </div>
  );
}
