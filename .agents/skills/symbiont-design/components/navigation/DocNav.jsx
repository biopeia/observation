import React from "react";
import { DomainGlyph } from "../core/DomainTag.jsx";
import { StatusGlyph } from "../core/StatusMark.jsx";

export function DocNav({ sections = [], activeId, onSelect, header }) {
  const label = { font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', textTransform: "uppercase", letterSpacing: "var(--tracking-label)" };
  return (
    <nav aria-label="Documentation" style={{ display: "flex", flexDirection: "column", gap: "var(--space-5)", font: "var(--type-meta)", fontSize: "0.875rem" }}>
      {header}
      {sections.map((s, si) => (
        <div key={si}>
          <div style={{ ...label, display: "flex", alignItems: "center", gap: 7, color: "var(--ink-3)", padding: "0 0 6px", borderBottom: "1px solid var(--rule-1)", marginBottom: 4 }}>
            {s.domain ? <DomainGlyph domain={s.domain} size={8} /> : null}{s.label}
          </div>
          <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
            {s.items.map((it) => {
              const active = it.id === activeId;
              return (
                <li key={it.id}>
                  <a href={`#${it.id}`} onClick={(e) => { if (onSelect) { e.preventDefault(); onSelect(it.id); } }}
                    aria-current={active ? "page" : undefined}
                    style={{
                      display: "flex", alignItems: "baseline", gap: 8, padding: "4px 0 4px 10px", marginLeft: -1,
                      borderLeft: active ? "1px solid var(--rule-ink)" : "1px solid transparent",
                      color: active ? "var(--ink-1)" : it.status === "superseded" ? "var(--ink-3)" : "var(--ink-2)",
                      fontWeight: active ? 600 : 400, textDecoration: "none", lineHeight: 1.35,
                    }}>
                    {it.number ? <span style={{ fontFamily: "var(--font-mono)", fontVariationSettings: '"wdth" var(--mono-wdth)', fontSize: "0.6875rem", color: "var(--ink-3)", fontWeight: 400, minWidth: 22 }}>{it.number}</span> : null}
                    <span style={{ flex: 1, textDecoration: it.status === "superseded" ? "line-through" : "none", textDecorationColor: "var(--rule-3)" }}>{it.label}</span>
                    {it.status ? <span style={{ alignSelf: "center" }}><StatusGlyph status={it.status} size={8} /></span> : null}
                  </a>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}
