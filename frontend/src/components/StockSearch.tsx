"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { errorText, getData } from "../lib/api";
import type { StockSearchResult } from "../lib/types";

export function StockSearch({
  onSelect,
  placeholder = "搜索股票代码 / 名称，例如：300750 宁德时代",
  autoFocus = false,
}: {
  onSelect?: (item: StockSearchResult) => void | Promise<void>;
  placeholder?: string;
  autoFocus?: boolean;
}) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [result, setResult] = useState<{ query: string; items: StockSearchResult[] } | null>(null);
  const [failure, setFailure] = useState<{ query: string; message: string } | null>(null);
  const term = query.trim();

  useEffect(() => {
    if (!term) return;
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      try {
        const response = await getData<StockSearchResult[]>(
          `/api/stocks/search?q=${encodeURIComponent(term)}&limit=8`, controller.signal
        );
        setResult({ query: term, items: response.data });
        setFailure(null);
      } catch (error) {
        if (!(error instanceof Error && error.name === "AbortError")) {
          setFailure({ query: term, message: errorText(error) });
        }
      }
    }, 280);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [term]);

  const items = result?.query === term ? result.items : null;
  const message = failure?.query === term ? failure.message : null;
  const choose = (item: StockSearchResult) => {
    setQuery("");
    setOpen(false);
    if (onSelect) void onSelect(item);
    else router.push(`/stock/${item.symbol}`);
  };

  return (
    <div className="search-wrap" onBlur={(event) => {
      if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
    }}>
      <span className="search-icon" aria-hidden="true">⌕</span>
      <input
        className="search-input" value={query} placeholder={placeholder} aria-label="搜索 A 股股票"
        autoFocus={autoFocus} autoComplete="off"
        onChange={(event) => { setQuery(event.target.value); setOpen(true); }}
        onFocus={() => setOpen(true)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && items?.length) choose(items[0]);
          if (event.key === "Escape") setOpen(false);
        }}
      />
      {open && term && (
        <div className="search-results" role="listbox" aria-label="股票搜索结果">
          {message ? <div className="search-message">{message}</div> :
            items === null ? <div className="search-message">正在搜索…</div> :
              items.length === 0 ? <div className="search-message">没有找到匹配股票</div> :
                items.map((item) => (
                  <button key={item.symbol} type="button" role="option" aria-selected="false"
                    className="search-result" onMouseDown={(event) => event.preventDefault()}
                    onClick={() => choose(item)}>
                    <span><strong>{item.name}</strong><small>{item.symbol}</small></span>
                    <em>{item.market}</em>
                  </button>
                ))}
        </div>
      )}
    </div>
  );
}
