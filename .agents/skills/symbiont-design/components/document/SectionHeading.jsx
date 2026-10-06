import React from "react";

export function SectionHeading({ number, title, level = 2, id, kicker }) {
  const Tag = level === 3 ? "h3" : "h2";
  const two = level !== 3;
  return (
    <Tag id={id} style={{
      display: "flex", flexWrap: "wrap", alignItems: "baseline", columnGap: "var(--space-5)",
      margin: two ? "var(--space-8) 0 var(--space-4)" : "var(--space-6) 0 var(--space-3)",
      paddingTop: two ? "var(--space-4)" : 0, borderTop: two ? "1px solid var(--rule-2)" : "none",
      font: two ? "var(--type-h2)" : "var(--type-h3)", color: "var(--ink-1)", scrollMarginTop: 24,
    }}>
      <span style={{ flex: "0 0 128px", font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', fontSize: two ? "0.75rem" : "0.6875rem", color: "var(--ink-3)", letterSpacing: "0.02em" }}>
        {number ? `§ ${number}` : ""}{kicker ? <span style={{ display: "block", textTransform: "uppercase", letterSpacing: "var(--tracking-label)", marginTop: 4 }}>{kicker}</span> : null}
      </span>
      <span style={{ flex: "1 1 280px", textWrap: "balance" }}>{title}</span>
    </Tag>
  );
}
