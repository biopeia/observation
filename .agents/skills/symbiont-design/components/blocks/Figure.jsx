import React from "react";

export function Figure({ number, caption, source, tone = "paper", height, children, wide = false }) {
  const night = tone === "night";
  return (
    <figure style={{ margin: "var(--space-6) 0", maxWidth: wide ? "var(--measure-wide)" : "none" }}>
      <div style={{
        minHeight: height, background: night ? "var(--night-0)" : "transparent",
        borderTop: night ? "none" : "1px solid var(--rule-ink)", borderBottom: night ? "none" : "1px solid var(--rule-2)",
        padding: night ? "var(--space-5)" : "var(--space-5) 0", color: night ? "var(--night-ink-1)" : "var(--ink-1)",
        display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden",
      }}>{children}</div>
      <figcaption style={{ display: "flex", flexWrap: "wrap", gap: "4px 14px", marginTop: 10, alignItems: "baseline" }}>
        {number ? <span style={{ font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', textTransform: "uppercase", letterSpacing: "var(--tracking-label)", color: "var(--ink-1)" }}>Fig. {number}</span> : null}
        <span style={{ flex: "1 1 300px", font: "400 var(--fs-small)/1.5 var(--font-serif)", color: "var(--ink-2)", textWrap: "pretty" }}>{caption}</span>
        {source ? <code style={{ font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', color: "var(--ink-3)" }}>{source}</code> : null}
      </figcaption>
    </figure>
  );
}
