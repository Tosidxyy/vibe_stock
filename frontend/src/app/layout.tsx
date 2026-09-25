import type { Metadata } from "next";
import { SiteChrome } from "../components/SiteChrome";
import "./globals.css";

export const metadata: Metadata = {
  title: "StockPilot · A 股智能看盘",
  description: "A 股行情、指数走势与自选股工作台",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN"><body><SiteChrome>{children}</SiteChrome></body></html>;
}
