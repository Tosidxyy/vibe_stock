import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "StockPilot",
  description: "A 股智能看盘与分析工作台",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>
        <div className="app-shell">
          <aside className="sidebar">
            <div className="brand">
              <span className="brand-mark">S</span>
              <span><strong>StockPilot</strong><small>A 股智能看盘</small></span>
            </div>
            <nav aria-label="主导航">
              <p className="nav-title">工作台</p>
              <Link className="nav-link active" href="/" aria-current="page"><span className="nav-dot" />市场概览</Link>
              <span className="nav-link muted"><span className="nav-dot" />自选股</span>
              <span className="nav-link muted"><span className="nav-dot" />AI Agent</span>
            </nav>
            <div className="sidebar-footer">StockPilot <span>V0.1</span></div>
          </aside>
          <div className="main-shell">
            <header className="topbar">
              <span className="topbar-label">市场工作台</span>
              <span className="topbar-badge">初始化阶段</span>
            </header>
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}
