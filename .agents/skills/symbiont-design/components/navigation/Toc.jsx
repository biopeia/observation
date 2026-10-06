import React from "react";

export function Toc({ items = [], activeId, title = "On this page", onSelect }) {
  return (
    <nav aria-label={title} style={{ font: "var(--type-meta)" }}>
      <div style={{ font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', textTransform: "uppercase", letterSpacing: "var(--tracking-label)", color: "var(--ink-3)", marginBottom: 8 }}>{title}</div>
      <ol style={{ listStyle: "none", margin: 0, padding: 0, borderLeft: "1px solid var(--rule-1)" }}>
        {items.map((it) => {
          const active = it.id === activeId;
          return (
            <li key={it.id}>
              <a href={`#${it.id}`} onClick={(e) => { if (onSelect) { e.preventDefault(); onSelect(it.id); } }}
                style={{ display: "flex", gap: 8, padding: `3px 0 3px ${it.level === 3 ? 24 : 12}px`, marginLeft: -1, borderLeft: active ? "1px solid var(--rule-ink)" : "1px solid transparent", color: active ? "var(--ink-1)" : "var(--ink-3)", textDecoration: "none", lineHeight: 1.4 }}>
                {it.number ? <span style={{ fontFamily: "var(--font-mono)", fontVariationSettings: '"wdth" var(--mono-wdth)', fontSize: "0.6875rem", minWidth: 20 }}>{it.number}</span> : null}
                <span>{it.label}</span>
              </a>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
