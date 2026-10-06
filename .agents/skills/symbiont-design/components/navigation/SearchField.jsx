import React from "react";

export function SearchField({ value, onChange, placeholder = "Search the corpus", shortcut = "/", width = "100%" }) {
  const [focus, setFocus] = React.useState(false);
  return (
    <label style={{ display: "flex", alignItems: "center", gap: 8, width, height: 34, padding: "0 10px", background: "var(--paper-0)", boxShadow: `inset 0 0 0 1px ${focus ? "var(--rule-ink)" : "var(--rule-2)"}`, borderRadius: "var(--radius-1)", transition: "box-shadow var(--dur-1) var(--ease)" }}>
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--ink-3)" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></svg>
      <input value={value} onChange={(e) => onChange && onChange(e.target.value)} placeholder={placeholder}
        onFocus={() => setFocus(true)} onBlur={() => setFocus(false)}
        style={{ flex: 1, minWidth: 0, border: 0, outline: 0, background: "transparent", font: "var(--type-meta)", fontSize: "0.875rem", color: "var(--ink-1)" }} />
      {shortcut ? <kbd style={{ fontFamily: "var(--font-mono)", fontVariationSettings: '"wdth" var(--mono-wdth)', fontSize: "0.625rem", color: "var(--ink-3)", padding: "1px 5px", boxShadow: "inset 0 0 0 1px var(--rule-2)", borderRadius: "var(--radius-1)" }}>{shortcut}</kbd> : null}
    </label>
  );
}
