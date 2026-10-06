import React from "react";

export function DataTable({ columns = [], rows = [], number, caption, dense = false }) {
  const pad = dense ? "6px 14px 6px 0" : "9px 16px 9px 0";
  return (
    <figure style={{ margin: "0 0 var(--space-6)", overflowX: "auto" }}>
      {(number || caption) ? (
        <figcaption style={{ display: "flex", gap: 14, alignItems: "baseline", marginBottom: 10 }}>
          {number ? <span style={{ font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', textTransform: "uppercase", letterSpacing: "var(--tracking-label)" }}>Table {number}</span> : null}
          <span style={{ font: "400 var(--fs-small)/1.5 var(--font-serif)", color: "var(--ink-2)" }}>{caption}</span>
        </figcaption>
      ) : null}
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: dense ? "var(--fs-meta)" : "var(--fs-small)", lineHeight: 1.45, fontVariantNumeric: "tabular-nums" }}>
        <thead>
          <tr>{columns.map((c) => (
            <th key={c.key} style={{ textAlign: c.align || "left", padding: pad, borderTop: "1px solid var(--rule-ink)", borderBottom: "1px solid var(--rule-ink)", font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', textTransform: "uppercase", letterSpacing: "var(--tracking-label)", color: "var(--ink-2)", whiteSpace: "nowrap", width: c.width }}>{c.label}</th>
          ))}</tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>{columns.map((c) => (
              <td key={c.key} style={{ textAlign: c.align || "left", padding: pad, borderBottom: i === rows.length - 1 ? "1px solid var(--rule-ink)" : "1px solid var(--rule-1)", verticalAlign: "top", color: "var(--ink-1)", fontFamily: c.mono ? "var(--font-mono)" : "inherit", fontVariationSettings: c.mono ? '"wdth" var(--mono-wdth)' : "normal", fontSize: c.mono ? "0.8em" : "inherit" }}>{r[c.key]}</td>
            ))}</tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}
