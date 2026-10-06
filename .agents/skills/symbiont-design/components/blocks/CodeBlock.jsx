import React from "react";

export function CodeBlock({ code = "", language, title, caption, tone = "paper", lineNumbers = false, highlight = [] }) {
  const night = tone === "night";
  const lines = String(code).replace(/\n$/, "").split("\n");
  const c = night
    ? { bg: "var(--night-0)", ink: "var(--night-ink-1)", meta: "var(--night-ink-3)", rule: "var(--night-rule)", hl: "var(--night-2)", com: "var(--night-ink-2)" }
    : { bg: "var(--paper-1)", ink: "var(--ink-1)", meta: "var(--ink-3)", rule: "var(--rule-2)", hl: "var(--paper-3)", com: "var(--ink-3)" };
  const mono = { fontFamily: "var(--font-mono)", fontVariationSettings: '"wdth" var(--mono-wdth)' };
  const renderLine = (l) => {
    const m = l.match(/^(.*?)(\s*(#|\/\/).*)$/);
    if (m && !/["'].*(#|\/\/).*["']/.test(l)) return <>{m[1]}<span style={{ color: c.com, fontStyle: "normal" }}>{m[2]}</span></>;
    return l || " ";
  };
  return (
    <figure style={{ margin: "0 0 var(--space-5)" }}>
      <div style={{ background: c.bg, borderTop: `1px solid ${night ? c.bg : c.rule}`, borderBottom: `1px solid ${night ? c.bg : c.rule}` }}>
        {(title || language) ? (
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, padding: "8px var(--space-5)", borderBottom: `1px solid ${c.rule}`, ...mono, fontSize: "0.6875rem", color: c.meta }}>
            <span style={{ color: night ? c.ink : "var(--ink-2)" }}>{title}</span>
            <span style={{ textTransform: "uppercase", letterSpacing: "var(--tracking-label)" }}>{language}</span>
          </div>
        ) : null}
        <pre style={{ margin: 0, padding: "var(--space-4) 0", overflowX: "auto", ...mono, fontSize: "var(--fs-code)", lineHeight: "var(--lh-code)", color: c.ink }}>
          {lines.map((l, i) => (
            <div key={i} style={{ display: "flex", padding: "0 var(--space-5)", background: highlight.includes(i + 1) ? c.hl : "transparent" }}>
              {lineNumbers ? <span style={{ flex: "none", width: "2.6em", color: c.meta, userSelect: "none" }}>{i + 1}</span> : null}
              <span style={{ whiteSpace: "pre" }}>{renderLine(l)}</span>
            </div>
          ))}
        </pre>
      </div>
      {caption ? <figcaption style={{ font: "var(--type-meta)", color: "var(--ink-3)", marginTop: 8 }}>{caption}</figcaption> : null}
    </figure>
  );
}
