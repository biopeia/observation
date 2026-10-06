import React from "react";
import { StatusMark } from "../core/StatusMark.jsx";

export function DecisionList({ items = [], start = 1 }) {
  return (
    <ol style={{ listStyle: "none", margin: "0 0 var(--space-6)", padding: 0, borderTop: "2px solid var(--rule-ink)" }}>
      {items.map((it, i) => (
        <li key={i} style={{ display: "flex", flexWrap: "wrap", columnGap: "var(--space-5)", padding: "var(--space-4) 0", borderBottom: "1px solid var(--rule-1)" }}>
          <span style={{ flex: "0 0 128px", font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', fontSize: "0.75rem", color: "var(--ink-3)", paddingTop: 4 }}>D{String(i + start).padStart(2, "0")}</span>
          <div style={{ flex: "1 1 280px", minWidth: 0 }}>
            <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: "4px 14px", marginBottom: 4 }}>
              <span style={{ font: "600 var(--fs-body)/1.4 var(--font-sans)", color: it.status === "superseded" ? "var(--ink-3)" : "var(--ink-1)", textDecoration: it.status === "superseded" ? "line-through" : "none" }}>{it.title}</span>
              {it.status ? <StatusMark status={it.status} size="sm" detail={it.statusDetail} /> : null}
            </div>
            <div style={{ font: "var(--type-body)", color: "var(--ink-1)", textWrap: "pretty" }}>{it.body}</div>
          </div>
        </li>
      ))}
    </ol>
  );
}
