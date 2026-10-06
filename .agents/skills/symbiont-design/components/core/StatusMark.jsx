import React from "react";

/* Status vocabulary is taken verbatim from the repository:
   evidence-status.md, lab/research/README.md, glossary (artifact lifecycle), ADR status lines. */
const STATUS = {
  // evidence status (symbiont/docs/reference/evidence-status.md)
  implemented: { glyph: "square", tone: "ink" },
  tested: { glyph: "squareHalf", tone: "ink", label: "covered by tests" },
  observed: { glyph: "half", tone: "ink" },
  supported: { glyph: "full", tone: "ink" },
  intended: { glyph: "dashed", tone: "ink2" },
  historical: { glyph: "strike", tone: "muted" },
  unresolved: { glyph: "ring", tone: "ink2" },
  // study lifecycle (lab/research/README.md)
  planned: { glyph: "dashed", tone: "ink2" },
  preregistered: { glyph: "ring", tone: "ink" },
  running: { glyph: "ringDot", tone: "ink" },
  discovery: { glyph: "half", tone: "ink2" },
  partial: { glyph: "half", tone: "ink" },
  negative: { glyph: "minus", tone: "ink" },
  inconclusive: { glyph: "ringBar", tone: "ink2" },
  superseded: { glyph: "strike", tone: "muted" },
  frozen: { glyph: "frozen", tone: "ink" },
  // artifact lifecycle (glossary)
  working: { glyph: "dashed", tone: "ink2" },
  validated: { glyph: "squareHalf", tone: "ink" },
  // ADR
  proposed: { glyph: "dashed", tone: "ink2" },
  accepted: { glyph: "square", tone: "ink" },
  "partially-superseded": { glyph: "halfStrike", tone: "ink2", label: "partially superseded" },
  // integrity
  failing: { glyph: "full", tone: "warn", label: "integrity failure" },
};

const TONES = { ink: "var(--ink-1)", ink2: "var(--ink-2)", muted: "var(--ink-3)", warn: "var(--signal-warn-ink)" };

export function StatusGlyph({ status = "supported", size = 10 }) {
  const s = STATUS[status] || STATUS.unresolved;
  const c = TONES[s.tone];
  const r = size / 2 - 0.8, m = size / 2;
  const g = {
    full: <circle cx={m} cy={m} r={r} fill={c} />,
    half: <g><circle cx={m} cy={m} r={r} fill="none" stroke={c} strokeWidth="1.2" /><path d={`M${m} ${m - r} A${r} ${r} 0 0 1 ${m} ${m + r} Z`} fill={c} /></g>,
    ring: <circle cx={m} cy={m} r={r} fill="none" stroke={c} strokeWidth="1.2" />,
    dashed: <circle cx={m} cy={m} r={r} fill="none" stroke={c} strokeWidth="1.2" strokeDasharray="1.6 1.6" />,
    ringDot: <g><circle cx={m} cy={m} r={r} fill="none" stroke={c} strokeWidth="1.2" /><circle cx={m} cy={m} r={r * 0.38} fill={c} /></g>,
    ringBar: <g><circle cx={m} cy={m} r={r} fill="none" stroke={c} strokeWidth="1.2" /><rect x={m - r * 0.55} y={m - 0.6} width={r * 1.1} height="1.2" fill={c} /></g>,
    minus: <g><circle cx={m} cy={m} r={r} fill={c} /><rect x={m - r * 0.55} y={m - 0.75} width={r * 1.1} height="1.5" fill="var(--paper-0)" /></g>,
    strike: <g><circle cx={m} cy={m} r={r} fill="none" stroke={c} strokeWidth="1.2" /><line x1="0.6" y1={size - 0.6} x2={size - 0.6} y2="0.6" stroke={c} strokeWidth="1.2" /></g>,
    halfStrike: <g><path d={`M${m} ${m - r} A${r} ${r} 0 0 1 ${m} ${m + r} Z`} fill={c} /><circle cx={m} cy={m} r={r} fill="none" stroke={c} strokeWidth="1.2" /><line x1="0.6" y1={size - 0.6} x2={size - 0.6} y2="0.6" stroke={c} strokeWidth="1.2" /></g>,
    square: <rect x="1" y="1" width={size - 2} height={size - 2} fill={c} />,
    squareHalf: <g><rect x="1.1" y="1.1" width={size - 2.2} height={size - 2.2} fill="none" stroke={c} strokeWidth="1.2" /><rect x="1" y={m} width={size - 2} height={size / 2 - 1} fill={c} /></g>,
    frozen: <g><rect x="1.1" y="1.1" width={size - 2.2} height={size - 2.2} fill="none" stroke={c} strokeWidth="1.2" /><rect x={m - 1.6} y={m - 1.6} width="3.2" height="3.2" fill={c} /></g>,
  };
  return <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true" style={{ flex: "none", display: "block" }}>{g[s.glyph]}</svg>;
}

export function StatusMark({ status = "supported", label, detail, size = "md" }) {
  const s = STATUS[status] || STATUS.unresolved;
  const text = label || s.label || status;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6, whiteSpace: "nowrap",
      font: "var(--type-label)", fontSize: size === "sm" ? "0.625rem" : "var(--fs-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)', textTransform: "uppercase", letterSpacing: "var(--tracking-label)",
      color: TONES[s.tone], textDecoration: s.glyph === "strike" ? "line-through" : "none", textDecorationThickness: 1,
    }}>
      <StatusGlyph status={status} size={size === "sm" ? 9 : 10} />
      {text}
      {detail ? <span style={{ color: "var(--ink-3)", textTransform: "none", letterSpacing: 0, textDecoration: "none" }}>{detail}</span> : null}
    </span>
  );
}
