import React from "react";
import { StatusMark } from "../core/StatusMark.jsx";
import { EvidenceMeter } from "../core/EvidenceMeter.jsx";

/* Each kind = one information type. Differences are structural (rule weight, dash, ground), not decorative. */
const KINDS = {
  note: { label: "Note", top: "1px solid var(--rule-2)", bg: "transparent", labelColor: "var(--ink-3)" },
  principle: { label: "Principle", top: "1px solid var(--rule-ink)", bg: "transparent", labelColor: "var(--ink-1)", serif: true },
  invariant: { label: "Invariant", top: "2px solid var(--rule-ink)", bottom: "1px solid var(--rule-ink)", bg: "transparent", labelColor: "var(--ink-1)", strong: true },
  hypothesis: { label: "Hypothesis", top: "1px dashed var(--rule-3)", bottom: "1px dashed var(--rule-3)", bg: "transparent", labelColor: "var(--ink-2)", serif: true, italic: true },
  evidence: { label: "Evidence", top: "1px solid var(--rule-ink)", bg: "transparent", labelColor: "var(--ink-1)" },
  implementation: { label: "Implementation", top: "1px solid var(--rule-2)", bg: "var(--paper-1)", labelColor: "var(--ink-3)", pad: true },
  limitation: { label: "Limitation", top: "1px solid var(--signal-warn-rule)", bg: "transparent", labelColor: "var(--signal-warn-ink)" },
  warning: { label: "Warning", top: "2px solid var(--signal-warn)", bg: "var(--signal-warn-tint)", labelColor: "var(--signal-warn-ink)", pad: true },
  decision: { label: "Decision", top: "2px solid var(--rule-ink)", bg: "transparent", labelColor: "var(--ink-1)", strong: true },
  superseded: { label: "Superseded", top: "1px solid var(--rule-2)", bg: "repeating-linear-gradient(135deg, var(--paper-1) 0 6px, var(--paper-0) 6px 12px)", labelColor: "var(--ink-3)", pad: true, muted: true },
};

export function Callout({ kind = "note", title, id, status, strength, scope, source, supersededBy, children }) {
  const k = KINDS[kind] || KINDS.note;
  const label = { font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', textTransform: "uppercase", letterSpacing: "var(--tracking-label)" };
  return (
    <aside data-kind={kind} style={{
      display: "flex", flexWrap: "wrap", columnGap: "var(--space-5)", rowGap: "var(--space-2)",
      borderTop: k.top, borderBottom: k.bottom || "none", background: k.bg,
      padding: k.pad ? "var(--space-4) var(--space-5) var(--space-4)" : "var(--space-3) 0 var(--space-4)", margin: "0 0 var(--space-5)",
    }}>
      <div style={{ flex: "0 0 128px", display: "flex", flexDirection: "column", gap: 4, paddingTop: 3 }}>
        <span style={{ ...label, color: k.labelColor }}>{k.label}</span>
        {id ? <span style={{ ...label, letterSpacing: "0.02em", textTransform: "none", color: "var(--ink-3)" }}>{id}</span> : null}
      </div>
      <div style={{ flex: "1 1 280px", minWidth: 0, color: k.muted ? "var(--ink-2)" : "var(--ink-1)" }}>
        {title ? <div style={{ font: k.serif ? "500 1.125rem/1.4 var(--font-serif)" : "600 var(--fs-body)/1.4 var(--font-sans)", margin: "0 0 6px", textDecoration: k.muted ? "line-through" : "none", textDecorationColor: "var(--rule-3)" }}>{title}</div> : null}
        <div style={{
          font: k.serif ? "400 1.125rem/1.55 var(--font-serif)" : "var(--type-body)", fontStyle: k.italic ? "italic" : "normal",
          fontWeight: k.strong ? 500 : 400, textWrap: "pretty",
        }}>{children}</div>
        {(status || strength !== undefined || source || supersededBy) ? (
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "6px 16px", marginTop: 10 }}>
            {status ? <StatusMark status={status} size="sm" /> : null}
            {strength !== undefined ? <EvidenceMeter level={strength} scope={scope} /> : null}
            {source ? <code style={{ font: "var(--type-label)", fontVariationSettings: '"wdth" var(--mono-wdth)', color: "var(--ink-3)" }}>{source}</code> : null}
            {supersededBy ? <span style={{ font: "var(--type-meta)", color: "var(--ink-2)" }}>Superseded by <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem", color: "var(--ink-1)" }}>{supersededBy}</span></span> : null}
          </div>
        ) : null}
      </div>
    </aside>
  );
}
