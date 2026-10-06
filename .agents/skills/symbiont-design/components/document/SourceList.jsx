import React from "react";

const KIND = { design: "design", code: "src", test: "test", adr: "adr", study: "study", doc: "doc", config: "config" };

export function SourceList({ title = "Principal sources", items = [] }) {
  const label = { font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', textTransform: "uppercase", letterSpacing: "var(--tracking-label)" };
  return (
    <section style={{ display: "flex", flexWrap: "wrap", columnGap: "var(--space-5)", rowGap: 8, borderTop: "1px solid var(--rule-2)", padding: "var(--space-4) 0", margin: "var(--space-6) 0" }}>
      <span style={{ ...label, flex: "0 0 128px", color: "var(--ink-3)", paddingTop: 3 }}>{title}</span>
      <ul style={{ flex: "1 1 320px", listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 6 }}>
        {items.map((it, i) => (
          <li key={i} style={{ display: "flex", gap: 12, alignItems: "baseline", minWidth: 0 }}>
            <span style={{ ...label, fontSize: "0.5625rem", width: 44, flex: "none", color: "var(--ink-3)" }}>{KIND[it.kind] || it.kind || ""}</span>
            <span style={{ minWidth: 0 }}>
              {it.href ? <a href={it.href} style={{ fontFamily: "var(--font-mono)", fontVariationSettings: '"wdth" var(--mono-wdth)', fontSize: "0.75rem", wordBreak: "break-all" }}>{it.path}</a>
                : <code style={{ fontFamily: "var(--font-mono)", fontVariationSettings: '"wdth" var(--mono-wdth)', fontSize: "0.75rem", color: "var(--ink-1)", wordBreak: "break-all" }}>{it.path}</code>}
              {it.note ? <span style={{ font: "var(--type-meta)", color: "var(--ink-3)", marginLeft: 8 }}>{it.note}</span> : null}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
