import React from "react";

export function Breadcrumb({ items = [], onSelect }) {
  return (
    <nav aria-label="Breadcrumb" style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 8, fontFamily: "var(--font-mono)", fontVariationSettings: '"wdth" var(--mono-wdth)', fontSize: "0.6875rem", color: "var(--ink-3)" }}>
      {items.map((it, i) => {
        const last = i === items.length - 1;
        return (
          <React.Fragment key={i}>
            {last ? <span style={{ color: "var(--ink-1)" }}>{it.label}</span>
              : <a href={it.href || "#"} onClick={(e) => { if (onSelect) { e.preventDefault(); onSelect(it, i); } }} style={{ color: "var(--ink-3)", textDecoration: "none" }}>{it.label}</a>}
            {!last ? <span aria-hidden="true" style={{ color: "var(--rule-3)" }}>/</span> : null}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
