import React from "react";

const DOMAINS = {
  symbiont: { label: "symbiont", shape: "circle" },
  embodiment: { label: "embodiment", shape: "square" },
  modality: { label: "modality", shape: "diamond" },
  environment: { label: "environment", shape: "ground" },
  lab: { label: "lab", shape: "ring" },
};

export function DomainGlyph({ domain = "symbiont", size = 9, color }) {
  const d = DOMAINS[domain] || DOMAINS.symbiont;
  const c = color || `var(--dom-${domain})`;
  const s = size;
  const shapes = {
    circle: <circle cx={s / 2} cy={s / 2} r={s / 2 - 0.5} fill={c} />,
    square: <rect x="0.5" y="0.5" width={s - 1} height={s - 1} fill={c} />,
    diamond: <rect x={s * 0.18} y={s * 0.18} width={s * 0.64} height={s * 0.64} fill={c} transform={`rotate(45 ${s / 2} ${s / 2})`} />,
    ground: <g fill={c}><rect x="0" y={s * 0.56} width={s} height={s * 0.26} /><rect x={s * 0.2} y={s * 0.18} width={s * 0.6} height={s * 0.22} /></g>,
    ring: <circle cx={s / 2} cy={s / 2} r={s / 2 - 1.1} fill="none" stroke={c} strokeWidth="1.6" />,
  };
  return <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`} aria-hidden="true" style={{ flex: "none", display: "block" }}>{shapes[d.shape]}</svg>;
}

export function DomainTag({ domain = "symbiont", variant = "label", children, title }) {
  const d = DOMAINS[domain] || DOMAINS.symbiont;
  const text = children || d.label;
  if (variant === "glyph") return <span title={title || d.label} style={{ display: "inline-flex" }}><DomainGlyph domain={domain} /></span>;
  const filled = variant === "filled";
  return (
    <span title={title} style={{
      display: "inline-flex", alignItems: "center", gap: 6, height: 20, padding: filled ? "0 7px" : 0,
      background: filled ? `var(--dom-${domain}-tint)` : "transparent",
      boxShadow: filled ? `inset 0 0 0 1px var(--dom-${domain}-rule)` : "none", borderRadius: "var(--radius-1)",
      font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', letterSpacing: "0.02em",
      color: `var(--dom-${domain}-ink)`, whiteSpace: "nowrap",
    }}>
      <DomainGlyph domain={domain} size={8} />
      {text}
    </span>
  );
}
