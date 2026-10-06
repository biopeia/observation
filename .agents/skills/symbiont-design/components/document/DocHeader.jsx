import React from "react";
import { DomainTag } from "../core/DomainTag.jsx";
import { StatusMark } from "../core/StatusMark.jsx";

const TYPE_LABEL = { chapter: "Chapter", adr: "Architecture decision", specification: "Specification", study: "Study record", protocol: "Protocol", reference: "Reference", anatomy: "Anatomy", history: "Historical record", audit: "Audit" };

export function DocHeader({ docType = "chapter", id, title, subtitle, abstract, domains = [], status, meta = [], supersededBy }) {
  const label = { font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', textTransform: "uppercase", letterSpacing: "var(--tracking-label)" };
  const historical = docType === "history" || status === "superseded" || status === "historical";
  return (
    <header style={{ margin: "0 0 var(--space-7)" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "8px 18px", paddingBottom: 10, borderBottom: "1px solid var(--rule-ink)" }}>
        <span style={{ ...label, color: "var(--ink-1)" }}>{TYPE_LABEL[docType] || docType}</span>
        {id ? <span style={{ ...label, textTransform: "none", letterSpacing: "0.02em", color: "var(--ink-2)" }}>{id}</span> : null}
        {status ? <StatusMark status={status} /> : null}
        <span style={{ flex: 1 }} />
        <span style={{ display: "inline-flex", flexWrap: "wrap", gap: 14 }}>{domains.map((d) => <DomainTag key={d} domain={d} />)}</span>
      </div>
      <h1 style={{ font: "var(--type-title)", fontSize: "clamp(2rem, 4.2vw, var(--fs-title))", letterSpacing: "var(--tracking-title)", fontVariationSettings: '"opsz" 60', margin: "var(--space-6) 0 0", color: historical ? "var(--ink-2)" : "var(--ink-1)", textWrap: "balance", maxWidth: "22em" }}>{title}</h1>
      {subtitle ? <p style={{ font: "italic 400 var(--fs-lede)/1.4 var(--font-serif)", color: "var(--ink-2)", margin: "var(--space-3) 0 0", maxWidth: "36em" }}>{subtitle}</p> : null}
      {supersededBy ? (
        <p style={{ margin: "var(--space-4) 0 0", padding: "8px 12px", background: "repeating-linear-gradient(135deg, var(--paper-1) 0 6px, var(--paper-0) 6px 12px)", font: "var(--type-meta)", color: "var(--ink-2)", display: "inline-block" }}>
          Superseded by <code style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem", color: "var(--ink-1)" }}>{supersededBy}</code>. Retained as evidence for its original scope.
        </p>
      ) : null}
      {abstract ? (
        <div style={{ display: "flex", flexWrap: "wrap", columnGap: "var(--space-5)", rowGap: 6, marginTop: "var(--space-6)" }}>
          <span style={{ ...label, flex: "0 0 128px", color: "var(--ink-3)", paddingTop: 6 }}>Abstract</span>
          <div style={{ flex: "1 1 320px", maxWidth: "var(--measure)", font: "var(--type-lede)", fontSize: "1.1875rem", color: "var(--ink-1)", textWrap: "pretty" }}>{abstract}</div>
        </div>
      ) : null}
      {meta.length ? (
        <dl style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: 0, margin: "var(--space-6) 0 0", borderTop: "1px solid var(--rule-2)" }}>
          {meta.map((m, i) => (
            <div key={i} style={{ padding: "10px 16px 10px 0", borderBottom: "1px solid var(--rule-1)" }}>
              <dt style={{ ...label, fontSize: "0.625rem", color: "var(--ink-3)", marginBottom: 4 }}>{m.label}</dt>
              <dd style={{ margin: 0, font: m.mono ? "400 0.75rem/1.5 var(--font-mono)" : "var(--type-meta)", fontVariationSettings: m.mono ? '"wdth" var(--mono-wdth)' : "normal", color: "var(--ink-1)" }}>{m.value}</dd>
            </div>
          ))}
        </dl>
      ) : null}
    </header>
  );
}
