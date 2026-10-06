import React from "react";

const LEVELS = ["none", "single observation", "repeated observation", "controlled study", "preregistered & replicated"];

export function EvidenceMeter({ level = 2, label, scope, compact = false }) {
  const lv = Math.max(0, Math.min(4, level));
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 8, font: "var(--type-meta)", color: "var(--ink-2)" }}>
      <span aria-label={`evidence strength ${lv} of 4`} style={{ display: "inline-flex", alignItems: "flex-end", gap: 2, height: 12 }}>
        {[1, 2, 3, 4].map((i) => (
          <span key={i} style={{ width: 4, height: 3 + i * 2.25, background: i <= lv ? "var(--ink-1)" : "transparent", boxShadow: i <= lv ? "none" : "inset 0 0 0 1px var(--rule-3)" }} />
        ))}
      </span>
      {compact ? null : <span>{label || LEVELS[lv]}</span>}
      {scope ? <span style={{ color: "var(--ink-3)" }}>· {scope}</span> : null}
    </span>
  );
}
