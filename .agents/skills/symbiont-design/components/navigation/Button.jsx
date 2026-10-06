import React from "react";

export function Button({ variant = "secondary", size = "md", disabled = false, onClick, children, type = "button" }) {
  const [hover, setHover] = React.useState(false);
  const h = size === "sm" ? 28 : 34;
  const v = disabled ? {
    primary: { bg: "var(--paper-1)", fg: "var(--ink-3)", ring: "var(--rule-2)" },
    secondary: { bg: "var(--paper-1)", fg: "var(--ink-3)", ring: "var(--rule-2)" },
    quiet: { bg: "transparent", fg: "var(--ink-3)", ring: "transparent" },
  }[variant] : {
    primary: { bg: hover ? "var(--ink-2)" : "var(--ink-1)", fg: "var(--paper-0)", ring: "transparent" },
    secondary: { bg: hover ? "var(--paper-1)" : "transparent", fg: "var(--ink-1)", ring: hover ? "var(--rule-ink)" : "var(--rule-3)" },
    quiet: { bg: "transparent", fg: hover ? "var(--ink-1)" : "var(--ink-2)", ring: "transparent" },
  }[variant];
  return (
    <button type={type} disabled={disabled} onClick={onClick} onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{
        display: "inline-flex", alignItems: "center", gap: 8, height: h, padding: variant === "quiet" ? "0 4px" : `0 ${size === "sm" ? 12 : 16}px`,
        background: v.bg, color: v.fg, border: 0, boxShadow: `inset 0 0 0 1px ${v.ring}`, borderRadius: "var(--radius-1)",
        font: size === "sm" ? "var(--type-label)" : "var(--type-meta)", cursor: disabled ? "not-allowed" : "pointer",
        opacity: 1, textDecoration: variant === "quiet" ? "underline" : "none", textUnderlineOffset: "0.25em",
        textDecorationColor: hover ? "currentColor" : "var(--rule-3)", transition: "background var(--dur-1) var(--ease), box-shadow var(--dur-1) var(--ease)",
      }}>{children}</button>
  );
}
