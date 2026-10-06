import React from "react";
import { StatusGlyph } from "../core/StatusMark.jsx";

/* Document lineage: a vertical descent line linking versions/supersessions, newest first. */
export function Lineage({ items = [], title = "Lineage" }) {
  const label = { font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', textTransform: "uppercase", letterSpacing: "var(--tracking-label)" };
  return (
    <section style={{ margin: "0 0 var(--space-6)" }}>
      <div style={{ ...label, color: "var(--ink-3)", marginBottom: 10 }}>{title}</div>
      <ol style={{ listStyle: "none", margin: 0, padding: 0 }}>
        {items.map((it, i) => {
          const last = i === items.length - 1;
          const past = it.status === "superseded" || it.status === "historical";
          return (
            <li key={i} style={{ display: "grid", gridTemplateColumns: "14px minmax(0,1fr)", columnGap: 12 }}>
              <span style={{ position: "relative", display: "flex", justifyContent: "center" }}>
                {!last ? <span style={{ position: "absolute", top: 14, bottom: 0, width: 1, background: past ? "var(--rule-2)" : "var(--rule-3)", left: 6.5 }} /> : null}
                <span style={{ marginTop: 5, background: "var(--paper-0)", position: "relative" }}><StatusGlyph status={it.status || "accepted"} size={11} /></span>
              </span>
              <div style={{ paddingBottom: last ? 0 : 14 }}>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "2px 10px", alignItems: "baseline" }}>
                  <code style={{ fontFamily: "var(--font-mono)", fontVariationSettings: '"wdth" var(--mono-wdth)', fontSize: "0.75rem", color: past ? "var(--ink-3)" : "var(--ink-1)" }}>{it.id}</code>
                  {it.date ? <span style={{ ...label, fontSize: "0.625rem", textTransform: "none", letterSpacing: 0, color: "var(--ink-3)" }}>{it.date}</span> : null}
                </div>
                <div style={{ font: "var(--type-meta)", fontSize: "0.875rem", color: past ? "var(--ink-3)" : "var(--ink-1)" }}>{it.title}</div>
                {it.relation ? <div style={{ font: "italic 400 0.8125rem/1.4 var(--font-serif)", color: "var(--ink-2)", marginTop: 2 }}>{it.relation}</div> : null}
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
