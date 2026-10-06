/* @ds-bundle: {"format":4,"namespace":"SymbiontDesignSystem_45c50a","components":[{"name":"Callout","sourcePath":"components/blocks/Callout.jsx"},{"name":"CodeBlock","sourcePath":"components/blocks/CodeBlock.jsx"},{"name":"DataTable","sourcePath":"components/blocks/DataTable.jsx"},{"name":"DecisionList","sourcePath":"components/blocks/DecisionList.jsx"},{"name":"Figure","sourcePath":"components/blocks/Figure.jsx"},{"name":"DomainGlyph","sourcePath":"components/core/DomainTag.jsx"},{"name":"DomainTag","sourcePath":"components/core/DomainTag.jsx"},{"name":"EvidenceMeter","sourcePath":"components/core/EvidenceMeter.jsx"},{"name":"StatusGlyph","sourcePath":"components/core/StatusMark.jsx"},{"name":"StatusMark","sourcePath":"components/core/StatusMark.jsx"},{"name":"DocHeader","sourcePath":"components/document/DocHeader.jsx"},{"name":"Lineage","sourcePath":"components/document/Lineage.jsx"},{"name":"SectionHeading","sourcePath":"components/document/SectionHeading.jsx"},{"name":"SourceList","sourcePath":"components/document/SourceList.jsx"},{"name":"Breadcrumb","sourcePath":"components/navigation/Breadcrumb.jsx"},{"name":"Button","sourcePath":"components/navigation/Button.jsx"},{"name":"DocNav","sourcePath":"components/navigation/DocNav.jsx"},{"name":"SearchField","sourcePath":"components/navigation/SearchField.jsx"},{"name":"Toc","sourcePath":"components/navigation/Toc.jsx"}],"sourceHashes":{"components/blocks/Callout.jsx":"c211eeea429b","components/blocks/CodeBlock.jsx":"9449d7f05d90","components/blocks/DataTable.jsx":"89c34dcd6cd6","components/blocks/DecisionList.jsx":"e7455925d877","components/blocks/Figure.jsx":"5f5f29ec2fc8","components/core/DomainTag.jsx":"4e02cd068783","components/core/EvidenceMeter.jsx":"179c94698d7e","components/core/StatusMark.jsx":"697f962cf264","components/document/DocHeader.jsx":"386277f6f5f2","components/document/Lineage.jsx":"f09acfb4269f","components/document/SectionHeading.jsx":"95c31e978b8f","components/document/SourceList.jsx":"53e1c722c7bf","components/navigation/Breadcrumb.jsx":"ffa4874b95ff","components/navigation/Button.jsx":"9c0351a8b17e","components/navigation/DocNav.jsx":"128337e8ff3f","components/navigation/SearchField.jsx":"87a2a350352e","components/navigation/Toc.jsx":"bec6bfc1329b","ui_kits/docs/ScreenAdr.jsx":"7242041124fd","ui_kits/docs/ScreenChapter.jsx":"b75b6a0ec267","ui_kits/docs/ScreenEvidence.jsx":"b12e09b537f9","ui_kits/docs/ScreenGlossary.jsx":"519b3ec392dc","ui_kits/docs/ScreenIndex.jsx":"2b5da6b5e5ed","ui_kits/docs/Shell.jsx":"c84f57e6ab4b","ui_kits/docs/doc-page.js":"f52ae9c02fca"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.SymbiontDesignSystem_45c50a = window.SymbiontDesignSystem_45c50a || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/blocks/CodeBlock.jsx
try { (() => {
function CodeBlock({
  code = "",
  language,
  title,
  caption,
  tone = "paper",
  lineNumbers = false,
  highlight = []
}) {
  const night = tone === "night";
  const lines = String(code).replace(/\n$/, "").split("\n");
  const c = night ? {
    bg: "var(--night-0)",
    ink: "var(--night-ink-1)",
    meta: "var(--night-ink-3)",
    rule: "var(--night-rule)",
    hl: "var(--night-2)",
    com: "var(--night-ink-2)"
  } : {
    bg: "var(--paper-1)",
    ink: "var(--ink-1)",
    meta: "var(--ink-3)",
    rule: "var(--rule-2)",
    hl: "var(--paper-3)",
    com: "var(--ink-3)"
  };
  const mono = {
    fontFamily: "var(--font-mono)",
    fontVariationSettings: '"wdth" var(--mono-wdth)'
  };
  const renderLine = l => {
    const m = l.match(/^(.*?)(\s*(#|\/\/).*)$/);
    if (m && !/["'].*(#|\/\/).*["']/.test(l)) return /*#__PURE__*/React.createElement(React.Fragment, null, m[1], /*#__PURE__*/React.createElement("span", {
      style: {
        color: c.com,
        fontStyle: "normal"
      }
    }, m[2]));
    return l || " ";
  };
  return /*#__PURE__*/React.createElement("figure", {
    style: {
      margin: "0 0 var(--space-5)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      background: c.bg,
      borderTop: `1px solid ${night ? c.bg : c.rule}`,
      borderBottom: `1px solid ${night ? c.bg : c.rule}`
    }
  }, title || language ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between",
      gap: 16,
      padding: "8px var(--space-5)",
      borderBottom: `1px solid ${c.rule}`,
      ...mono,
      fontSize: "0.6875rem",
      color: c.meta
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: night ? c.ink : "var(--ink-2)"
    }
  }, title), /*#__PURE__*/React.createElement("span", {
    style: {
      textTransform: "uppercase",
      letterSpacing: "var(--tracking-label)"
    }
  }, language)) : null, /*#__PURE__*/React.createElement("pre", {
    style: {
      margin: 0,
      padding: "var(--space-4) 0",
      overflowX: "auto",
      ...mono,
      fontSize: "var(--fs-code)",
      lineHeight: "var(--lh-code)",
      color: c.ink
    }
  }, lines.map((l, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      display: "flex",
      padding: "0 var(--space-5)",
      background: highlight.includes(i + 1) ? c.hl : "transparent"
    }
  }, lineNumbers ? /*#__PURE__*/React.createElement("span", {
    style: {
      flex: "none",
      width: "2.6em",
      color: c.meta,
      userSelect: "none"
    }
  }, i + 1) : null, /*#__PURE__*/React.createElement("span", {
    style: {
      whiteSpace: "pre"
    }
  }, renderLine(l)))))), caption ? /*#__PURE__*/React.createElement("figcaption", {
    style: {
      font: "var(--type-meta)",
      color: "var(--ink-3)",
      marginTop: 8
    }
  }, caption) : null);
}
Object.assign(__ds_scope, { CodeBlock });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/blocks/CodeBlock.jsx", error: String((e && e.message) || e) }); }

// components/blocks/DataTable.jsx
try { (() => {
function DataTable({
  columns = [],
  rows = [],
  number,
  caption,
  dense = false
}) {
  const pad = dense ? "6px 14px 6px 0" : "9px 16px 9px 0";
  return /*#__PURE__*/React.createElement("figure", {
    style: {
      margin: "0 0 var(--space-6)",
      overflowX: "auto"
    }
  }, number || caption ? /*#__PURE__*/React.createElement("figcaption", {
    style: {
      display: "flex",
      gap: 14,
      alignItems: "baseline",
      marginBottom: 10
    }
  }, number ? /*#__PURE__*/React.createElement("span", {
    style: {
      font: "var(--type-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      textTransform: "uppercase",
      letterSpacing: "var(--tracking-label)"
    }
  }, "Table ", number) : null, /*#__PURE__*/React.createElement("span", {
    style: {
      font: "400 var(--fs-small)/1.5 var(--font-serif)",
      color: "var(--ink-2)"
    }
  }, caption)) : null, /*#__PURE__*/React.createElement("table", {
    style: {
      width: "100%",
      borderCollapse: "collapse",
      fontSize: dense ? "var(--fs-meta)" : "var(--fs-small)",
      lineHeight: 1.45,
      fontVariantNumeric: "tabular-nums"
    }
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, columns.map(c => /*#__PURE__*/React.createElement("th", {
    key: c.key,
    style: {
      textAlign: c.align || "left",
      padding: pad,
      borderTop: "1px solid var(--rule-ink)",
      borderBottom: "1px solid var(--rule-ink)",
      font: "var(--type-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      textTransform: "uppercase",
      letterSpacing: "var(--tracking-label)",
      color: "var(--ink-2)",
      whiteSpace: "nowrap",
      width: c.width
    }
  }, c.label)))), /*#__PURE__*/React.createElement("tbody", null, rows.map((r, i) => /*#__PURE__*/React.createElement("tr", {
    key: i
  }, columns.map(c => /*#__PURE__*/React.createElement("td", {
    key: c.key,
    style: {
      textAlign: c.align || "left",
      padding: pad,
      borderBottom: i === rows.length - 1 ? "1px solid var(--rule-ink)" : "1px solid var(--rule-1)",
      verticalAlign: "top",
      color: "var(--ink-1)",
      fontFamily: c.mono ? "var(--font-mono)" : "inherit",
      fontVariationSettings: c.mono ? '"wdth" var(--mono-wdth)' : "normal",
      fontSize: c.mono ? "0.8em" : "inherit"
    }
  }, r[c.key])))))));
}
Object.assign(__ds_scope, { DataTable });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/blocks/DataTable.jsx", error: String((e && e.message) || e) }); }

// components/blocks/Figure.jsx
try { (() => {
function Figure({
  number,
  caption,
  source,
  tone = "paper",
  height,
  children,
  wide = false
}) {
  const night = tone === "night";
  return /*#__PURE__*/React.createElement("figure", {
    style: {
      margin: "var(--space-6) 0",
      maxWidth: wide ? "var(--measure-wide)" : "none"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      minHeight: height,
      background: night ? "var(--night-0)" : "transparent",
      borderTop: night ? "none" : "1px solid var(--rule-ink)",
      borderBottom: night ? "none" : "1px solid var(--rule-2)",
      padding: night ? "var(--space-5)" : "var(--space-5) 0",
      color: night ? "var(--night-ink-1)" : "var(--ink-1)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      overflow: "hidden"
    }
  }, children), /*#__PURE__*/React.createElement("figcaption", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      gap: "4px 14px",
      marginTop: 10,
      alignItems: "baseline"
    }
  }, number ? /*#__PURE__*/React.createElement("span", {
    style: {
      font: "var(--type-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      textTransform: "uppercase",
      letterSpacing: "var(--tracking-label)",
      color: "var(--ink-1)"
    }
  }, "Fig. ", number) : null, /*#__PURE__*/React.createElement("span", {
    style: {
      flex: "1 1 300px",
      font: "400 var(--fs-small)/1.5 var(--font-serif)",
      color: "var(--ink-2)",
      textWrap: "pretty"
    }
  }, caption), source ? /*#__PURE__*/React.createElement("code", {
    style: {
      font: "var(--type-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      color: "var(--ink-3)"
    }
  }, source) : null));
}
Object.assign(__ds_scope, { Figure });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/blocks/Figure.jsx", error: String((e && e.message) || e) }); }

// components/core/DomainTag.jsx
try { (() => {
const DOMAINS = {
  symbiont: {
    label: "symbiont",
    shape: "circle"
  },
  embodiment: {
    label: "embodiment",
    shape: "square"
  },
  modality: {
    label: "modality",
    shape: "diamond"
  },
  environment: {
    label: "environment",
    shape: "ground"
  },
  lab: {
    label: "lab",
    shape: "ring"
  }
};
function DomainGlyph({
  domain = "symbiont",
  size = 9,
  color
}) {
  const d = DOMAINS[domain] || DOMAINS.symbiont;
  const c = color || `var(--dom-${domain})`;
  const s = size;
  const shapes = {
    circle: /*#__PURE__*/React.createElement("circle", {
      cx: s / 2,
      cy: s / 2,
      r: s / 2 - 0.5,
      fill: c
    }),
    square: /*#__PURE__*/React.createElement("rect", {
      x: "0.5",
      y: "0.5",
      width: s - 1,
      height: s - 1,
      fill: c
    }),
    diamond: /*#__PURE__*/React.createElement("rect", {
      x: s * 0.18,
      y: s * 0.18,
      width: s * 0.64,
      height: s * 0.64,
      fill: c,
      transform: `rotate(45 ${s / 2} ${s / 2})`
    }),
    ground: /*#__PURE__*/React.createElement("g", {
      fill: c
    }, /*#__PURE__*/React.createElement("rect", {
      x: "0",
      y: s * 0.56,
      width: s,
      height: s * 0.26
    }), /*#__PURE__*/React.createElement("rect", {
      x: s * 0.2,
      y: s * 0.18,
      width: s * 0.6,
      height: s * 0.22
    })),
    ring: /*#__PURE__*/React.createElement("circle", {
      cx: s / 2,
      cy: s / 2,
      r: s / 2 - 1.1,
      fill: "none",
      stroke: c,
      strokeWidth: "1.6"
    })
  };
  return /*#__PURE__*/React.createElement("svg", {
    width: s,
    height: s,
    viewBox: `0 0 ${s} ${s}`,
    "aria-hidden": "true",
    style: {
      flex: "none",
      display: "block"
    }
  }, shapes[d.shape]);
}
function DomainTag({
  domain = "symbiont",
  variant = "label",
  children,
  title
}) {
  const d = DOMAINS[domain] || DOMAINS.symbiont;
  const text = children || d.label;
  if (variant === "glyph") return /*#__PURE__*/React.createElement("span", {
    title: title || d.label,
    style: {
      display: "inline-flex"
    }
  }, /*#__PURE__*/React.createElement(DomainGlyph, {
    domain: domain
  }));
  const filled = variant === "filled";
  return /*#__PURE__*/React.createElement("span", {
    title: title,
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 6,
      height: 20,
      padding: filled ? "0 7px" : 0,
      background: filled ? `var(--dom-${domain}-tint)` : "transparent",
      boxShadow: filled ? `inset 0 0 0 1px var(--dom-${domain}-rule)` : "none",
      borderRadius: "var(--radius-1)",
      font: "var(--type-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      letterSpacing: "0.02em",
      color: `var(--dom-${domain}-ink)`,
      whiteSpace: "nowrap"
    }
  }, /*#__PURE__*/React.createElement(DomainGlyph, {
    domain: domain,
    size: 8
  }), text);
}
Object.assign(__ds_scope, { DomainGlyph, DomainTag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/DomainTag.jsx", error: String((e && e.message) || e) }); }

// components/core/EvidenceMeter.jsx
try { (() => {
const LEVELS = ["none", "single observation", "repeated observation", "controlled study", "preregistered & replicated"];
function EvidenceMeter({
  level = 2,
  label,
  scope,
  compact = false
}) {
  const lv = Math.max(0, Math.min(4, level));
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
      font: "var(--type-meta)",
      color: "var(--ink-2)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-label": `evidence strength ${lv} of 4`,
    style: {
      display: "inline-flex",
      alignItems: "flex-end",
      gap: 2,
      height: 12
    }
  }, [1, 2, 3, 4].map(i => /*#__PURE__*/React.createElement("span", {
    key: i,
    style: {
      width: 4,
      height: 3 + i * 2.25,
      background: i <= lv ? "var(--ink-1)" : "transparent",
      boxShadow: i <= lv ? "none" : "inset 0 0 0 1px var(--rule-3)"
    }
  }))), compact ? null : /*#__PURE__*/React.createElement("span", null, label || LEVELS[lv]), scope ? /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--ink-3)"
    }
  }, "\xB7 ", scope) : null);
}
Object.assign(__ds_scope, { EvidenceMeter });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/EvidenceMeter.jsx", error: String((e && e.message) || e) }); }

// components/core/StatusMark.jsx
try { (() => {
/* Status vocabulary is taken verbatim from the repository:
   evidence-status.md, lab/research/README.md, glossary (artifact lifecycle), ADR status lines. */
const STATUS = {
  // evidence status (symbiont/docs/reference/evidence-status.md)
  implemented: {
    glyph: "square",
    tone: "ink"
  },
  tested: {
    glyph: "squareHalf",
    tone: "ink",
    label: "covered by tests"
  },
  observed: {
    glyph: "half",
    tone: "ink"
  },
  supported: {
    glyph: "full",
    tone: "ink"
  },
  intended: {
    glyph: "dashed",
    tone: "ink2"
  },
  historical: {
    glyph: "strike",
    tone: "muted"
  },
  unresolved: {
    glyph: "ring",
    tone: "ink2"
  },
  // study lifecycle (lab/research/README.md)
  planned: {
    glyph: "dashed",
    tone: "ink2"
  },
  preregistered: {
    glyph: "ring",
    tone: "ink"
  },
  running: {
    glyph: "ringDot",
    tone: "ink"
  },
  discovery: {
    glyph: "half",
    tone: "ink2"
  },
  partial: {
    glyph: "half",
    tone: "ink"
  },
  negative: {
    glyph: "minus",
    tone: "ink"
  },
  inconclusive: {
    glyph: "ringBar",
    tone: "ink2"
  },
  superseded: {
    glyph: "strike",
    tone: "muted"
  },
  frozen: {
    glyph: "frozen",
    tone: "ink"
  },
  // artifact lifecycle (glossary)
  working: {
    glyph: "dashed",
    tone: "ink2"
  },
  validated: {
    glyph: "squareHalf",
    tone: "ink"
  },
  // ADR
  proposed: {
    glyph: "dashed",
    tone: "ink2"
  },
  accepted: {
    glyph: "square",
    tone: "ink"
  },
  "partially-superseded": {
    glyph: "halfStrike",
    tone: "ink2",
    label: "partially superseded"
  },
  // integrity
  failing: {
    glyph: "full",
    tone: "warn",
    label: "integrity failure"
  }
};
const TONES = {
  ink: "var(--ink-1)",
  ink2: "var(--ink-2)",
  muted: "var(--ink-3)",
  warn: "var(--signal-warn-ink)"
};
function StatusGlyph({
  status = "supported",
  size = 10
}) {
  const s = STATUS[status] || STATUS.unresolved;
  const c = TONES[s.tone];
  const r = size / 2 - 0.8,
    m = size / 2;
  const g = {
    full: /*#__PURE__*/React.createElement("circle", {
      cx: m,
      cy: m,
      r: r,
      fill: c
    }),
    half: /*#__PURE__*/React.createElement("g", null, /*#__PURE__*/React.createElement("circle", {
      cx: m,
      cy: m,
      r: r,
      fill: "none",
      stroke: c,
      strokeWidth: "1.2"
    }), /*#__PURE__*/React.createElement("path", {
      d: `M${m} ${m - r} A${r} ${r} 0 0 1 ${m} ${m + r} Z`,
      fill: c
    })),
    ring: /*#__PURE__*/React.createElement("circle", {
      cx: m,
      cy: m,
      r: r,
      fill: "none",
      stroke: c,
      strokeWidth: "1.2"
    }),
    dashed: /*#__PURE__*/React.createElement("circle", {
      cx: m,
      cy: m,
      r: r,
      fill: "none",
      stroke: c,
      strokeWidth: "1.2",
      strokeDasharray: "1.6 1.6"
    }),
    ringDot: /*#__PURE__*/React.createElement("g", null, /*#__PURE__*/React.createElement("circle", {
      cx: m,
      cy: m,
      r: r,
      fill: "none",
      stroke: c,
      strokeWidth: "1.2"
    }), /*#__PURE__*/React.createElement("circle", {
      cx: m,
      cy: m,
      r: r * 0.38,
      fill: c
    })),
    ringBar: /*#__PURE__*/React.createElement("g", null, /*#__PURE__*/React.createElement("circle", {
      cx: m,
      cy: m,
      r: r,
      fill: "none",
      stroke: c,
      strokeWidth: "1.2"
    }), /*#__PURE__*/React.createElement("rect", {
      x: m - r * 0.55,
      y: m - 0.6,
      width: r * 1.1,
      height: "1.2",
      fill: c
    })),
    minus: /*#__PURE__*/React.createElement("g", null, /*#__PURE__*/React.createElement("circle", {
      cx: m,
      cy: m,
      r: r,
      fill: c
    }), /*#__PURE__*/React.createElement("rect", {
      x: m - r * 0.55,
      y: m - 0.75,
      width: r * 1.1,
      height: "1.5",
      fill: "var(--paper-0)"
    })),
    strike: /*#__PURE__*/React.createElement("g", null, /*#__PURE__*/React.createElement("circle", {
      cx: m,
      cy: m,
      r: r,
      fill: "none",
      stroke: c,
      strokeWidth: "1.2"
    }), /*#__PURE__*/React.createElement("line", {
      x1: "0.6",
      y1: size - 0.6,
      x2: size - 0.6,
      y2: "0.6",
      stroke: c,
      strokeWidth: "1.2"
    })),
    halfStrike: /*#__PURE__*/React.createElement("g", null, /*#__PURE__*/React.createElement("path", {
      d: `M${m} ${m - r} A${r} ${r} 0 0 1 ${m} ${m + r} Z`,
      fill: c
    }), /*#__PURE__*/React.createElement("circle", {
      cx: m,
      cy: m,
      r: r,
      fill: "none",
      stroke: c,
      strokeWidth: "1.2"
    }), /*#__PURE__*/React.createElement("line", {
      x1: "0.6",
      y1: size - 0.6,
      x2: size - 0.6,
      y2: "0.6",
      stroke: c,
      strokeWidth: "1.2"
    })),
    square: /*#__PURE__*/React.createElement("rect", {
      x: "1",
      y: "1",
      width: size - 2,
      height: size - 2,
      fill: c
    }),
    squareHalf: /*#__PURE__*/React.createElement("g", null, /*#__PURE__*/React.createElement("rect", {
      x: "1.1",
      y: "1.1",
      width: size - 2.2,
      height: size - 2.2,
      fill: "none",
      stroke: c,
      strokeWidth: "1.2"
    }), /*#__PURE__*/React.createElement("rect", {
      x: "1",
      y: m,
      width: size - 2,
      height: size / 2 - 1,
      fill: c
    })),
    frozen: /*#__PURE__*/React.createElement("g", null, /*#__PURE__*/React.createElement("rect", {
      x: "1.1",
      y: "1.1",
      width: size - 2.2,
      height: size - 2.2,
      fill: "none",
      stroke: c,
      strokeWidth: "1.2"
    }), /*#__PURE__*/React.createElement("rect", {
      x: m - 1.6,
      y: m - 1.6,
      width: "3.2",
      height: "3.2",
      fill: c
    }))
  };
  return /*#__PURE__*/React.createElement("svg", {
    width: size,
    height: size,
    viewBox: `0 0 ${size} ${size}`,
    "aria-hidden": "true",
    style: {
      flex: "none",
      display: "block"
    }
  }, g[s.glyph]);
}
function StatusMark({
  status = "supported",
  label,
  detail,
  size = "md"
}) {
  const s = STATUS[status] || STATUS.unresolved;
  const text = label || s.label || status;
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 6,
      whiteSpace: "nowrap",
      font: "var(--type-label)",
      fontSize: size === "sm" ? "0.625rem" : "var(--fs-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      textTransform: "uppercase",
      letterSpacing: "var(--tracking-label)",
      color: TONES[s.tone],
      textDecoration: s.glyph === "strike" ? "line-through" : "none",
      textDecorationThickness: 1
    }
  }, /*#__PURE__*/React.createElement(StatusGlyph, {
    status: status,
    size: size === "sm" ? 9 : 10
  }), text, detail ? /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--ink-3)",
      textTransform: "none",
      letterSpacing: 0,
      textDecoration: "none"
    }
  }, detail) : null);
}
Object.assign(__ds_scope, { StatusGlyph, StatusMark });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/StatusMark.jsx", error: String((e && e.message) || e) }); }

// components/blocks/Callout.jsx
try { (() => {
/* Each kind = one information type. Differences are structural (rule weight, dash, ground), not decorative. */
const KINDS = {
  note: {
    label: "Note",
    top: "1px solid var(--rule-2)",
    bg: "transparent",
    labelColor: "var(--ink-3)"
  },
  principle: {
    label: "Principle",
    top: "1px solid var(--rule-ink)",
    bg: "transparent",
    labelColor: "var(--ink-1)",
    serif: true
  },
  invariant: {
    label: "Invariant",
    top: "2px solid var(--rule-ink)",
    bottom: "1px solid var(--rule-ink)",
    bg: "transparent",
    labelColor: "var(--ink-1)",
    strong: true
  },
  hypothesis: {
    label: "Hypothesis",
    top: "1px dashed var(--rule-3)",
    bottom: "1px dashed var(--rule-3)",
    bg: "transparent",
    labelColor: "var(--ink-2)",
    serif: true,
    italic: true
  },
  evidence: {
    label: "Evidence",
    top: "1px solid var(--rule-ink)",
    bg: "transparent",
    labelColor: "var(--ink-1)"
  },
  implementation: {
    label: "Implementation",
    top: "1px solid var(--rule-2)",
    bg: "var(--paper-1)",
    labelColor: "var(--ink-3)",
    pad: true
  },
  limitation: {
    label: "Limitation",
    top: "1px solid var(--signal-warn-rule)",
    bg: "transparent",
    labelColor: "var(--signal-warn-ink)"
  },
  warning: {
    label: "Warning",
    top: "2px solid var(--signal-warn)",
    bg: "var(--signal-warn-tint)",
    labelColor: "var(--signal-warn-ink)",
    pad: true
  },
  decision: {
    label: "Decision",
    top: "2px solid var(--rule-ink)",
    bg: "transparent",
    labelColor: "var(--ink-1)",
    strong: true
  },
  superseded: {
    label: "Superseded",
    top: "1px solid var(--rule-2)",
    bg: "repeating-linear-gradient(135deg, var(--paper-1) 0 6px, var(--paper-0) 6px 12px)",
    labelColor: "var(--ink-3)",
    pad: true,
    muted: true
  }
};
function Callout({
  kind = "note",
  title,
  id,
  status,
  strength,
  scope,
  source,
  supersededBy,
  children
}) {
  const k = KINDS[kind] || KINDS.note;
  const label = {
    font: "var(--type-label)",
    fontVariationSettings: '"wdth" var(--mono-wdth)',
    textTransform: "uppercase",
    letterSpacing: "var(--tracking-label)"
  };
  return /*#__PURE__*/React.createElement("aside", {
    "data-kind": kind,
    style: {
      display: "flex",
      flexWrap: "wrap",
      columnGap: "var(--space-5)",
      rowGap: "var(--space-2)",
      borderTop: k.top,
      borderBottom: k.bottom || "none",
      background: k.bg,
      padding: k.pad ? "var(--space-4) var(--space-5) var(--space-4)" : "var(--space-3) 0 var(--space-4)",
      margin: "0 0 var(--space-5)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: "0 0 128px",
      display: "flex",
      flexDirection: "column",
      gap: 4,
      paddingTop: 3
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...label,
      color: k.labelColor
    }
  }, k.label), id ? /*#__PURE__*/React.createElement("span", {
    style: {
      ...label,
      letterSpacing: "0.02em",
      textTransform: "none",
      color: "var(--ink-3)"
    }
  }, id) : null), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: "1 1 280px",
      minWidth: 0,
      color: k.muted ? "var(--ink-2)" : "var(--ink-1)"
    }
  }, title ? /*#__PURE__*/React.createElement("div", {
    style: {
      font: k.serif ? "500 1.125rem/1.4 var(--font-serif)" : "600 var(--fs-body)/1.4 var(--font-sans)",
      margin: "0 0 6px",
      textDecoration: k.muted ? "line-through" : "none",
      textDecorationColor: "var(--rule-3)"
    }
  }, title) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      font: k.serif ? "400 1.125rem/1.55 var(--font-serif)" : "var(--type-body)",
      fontStyle: k.italic ? "italic" : "normal",
      fontWeight: k.strong ? 500 : 400,
      textWrap: "pretty"
    }
  }, children), status || strength !== undefined || source || supersededBy ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      alignItems: "center",
      gap: "6px 16px",
      marginTop: 10
    }
  }, status ? /*#__PURE__*/React.createElement(__ds_scope.StatusMark, {
    status: status,
    size: "sm"
  }) : null, strength !== undefined ? /*#__PURE__*/React.createElement(__ds_scope.EvidenceMeter, {
    level: strength,
    scope: scope
  }) : null, source ? /*#__PURE__*/React.createElement("code", {
    style: {
      font: "var(--type-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      color: "var(--ink-3)"
    }
  }, source) : null, supersededBy ? /*#__PURE__*/React.createElement("span", {
    style: {
      font: "var(--type-meta)",
      color: "var(--ink-2)"
    }
  }, "Superseded by ", /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: "0.75rem",
      color: "var(--ink-1)"
    }
  }, supersededBy)) : null) : null));
}
Object.assign(__ds_scope, { Callout });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/blocks/Callout.jsx", error: String((e && e.message) || e) }); }

// components/blocks/DecisionList.jsx
try { (() => {
function DecisionList({
  items = [],
  start = 1
}) {
  return /*#__PURE__*/React.createElement("ol", {
    style: {
      listStyle: "none",
      margin: "0 0 var(--space-6)",
      padding: 0,
      borderTop: "2px solid var(--rule-ink)"
    }
  }, items.map((it, i) => /*#__PURE__*/React.createElement("li", {
    key: i,
    style: {
      display: "flex",
      flexWrap: "wrap",
      columnGap: "var(--space-5)",
      padding: "var(--space-4) 0",
      borderBottom: "1px solid var(--rule-1)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      flex: "0 0 128px",
      font: "var(--type-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      fontSize: "0.75rem",
      color: "var(--ink-3)",
      paddingTop: 4
    }
  }, "D", String(i + start).padStart(2, "0")), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: "1 1 280px",
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      alignItems: "baseline",
      gap: "4px 14px",
      marginBottom: 4
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: "600 var(--fs-body)/1.4 var(--font-sans)",
      color: it.status === "superseded" ? "var(--ink-3)" : "var(--ink-1)",
      textDecoration: it.status === "superseded" ? "line-through" : "none"
    }
  }, it.title), it.status ? /*#__PURE__*/React.createElement(__ds_scope.StatusMark, {
    status: it.status,
    size: "sm",
    detail: it.statusDetail
  }) : null), /*#__PURE__*/React.createElement("div", {
    style: {
      font: "var(--type-body)",
      color: "var(--ink-1)",
      textWrap: "pretty"
    }
  }, it.body)))));
}
Object.assign(__ds_scope, { DecisionList });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/blocks/DecisionList.jsx", error: String((e && e.message) || e) }); }

// components/document/DocHeader.jsx
try { (() => {
const TYPE_LABEL = {
  chapter: "Chapter",
  adr: "Architecture decision",
  specification: "Specification",
  study: "Study record",
  protocol: "Protocol",
  reference: "Reference",
  anatomy: "Anatomy",
  history: "Historical record",
  audit: "Audit"
};
function DocHeader({
  docType = "chapter",
  id,
  title,
  subtitle,
  abstract,
  domains = [],
  status,
  meta = [],
  supersededBy
}) {
  const label = {
    font: "var(--type-label)",
    fontVariationSettings: '"wdth" var(--mono-wdth)',
    textTransform: "uppercase",
    letterSpacing: "var(--tracking-label)"
  };
  const historical = docType === "history" || status === "superseded" || status === "historical";
  return /*#__PURE__*/React.createElement("header", {
    style: {
      margin: "0 0 var(--space-7)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      alignItems: "center",
      gap: "8px 18px",
      paddingBottom: 10,
      borderBottom: "1px solid var(--rule-ink)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...label,
      color: "var(--ink-1)"
    }
  }, TYPE_LABEL[docType] || docType), id ? /*#__PURE__*/React.createElement("span", {
    style: {
      ...label,
      textTransform: "none",
      letterSpacing: "0.02em",
      color: "var(--ink-2)"
    }
  }, id) : null, status ? /*#__PURE__*/React.createElement(__ds_scope.StatusMark, {
    status: status
  }) : null, /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      display: "inline-flex",
      flexWrap: "wrap",
      gap: 14
    }
  }, domains.map(d => /*#__PURE__*/React.createElement(__ds_scope.DomainTag, {
    key: d,
    domain: d
  })))), /*#__PURE__*/React.createElement("h1", {
    style: {
      font: "var(--type-title)",
      fontSize: "clamp(2rem, 4.2vw, var(--fs-title))",
      letterSpacing: "var(--tracking-title)",
      fontVariationSettings: '"opsz" 60',
      margin: "var(--space-6) 0 0",
      color: historical ? "var(--ink-2)" : "var(--ink-1)",
      textWrap: "balance",
      maxWidth: "22em"
    }
  }, title), subtitle ? /*#__PURE__*/React.createElement("p", {
    style: {
      font: "italic 400 var(--fs-lede)/1.4 var(--font-serif)",
      color: "var(--ink-2)",
      margin: "var(--space-3) 0 0",
      maxWidth: "36em"
    }
  }, subtitle) : null, supersededBy ? /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "var(--space-4) 0 0",
      padding: "8px 12px",
      background: "repeating-linear-gradient(135deg, var(--paper-1) 0 6px, var(--paper-0) 6px 12px)",
      font: "var(--type-meta)",
      color: "var(--ink-2)",
      display: "inline-block"
    }
  }, "Superseded by ", /*#__PURE__*/React.createElement("code", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: "0.75rem",
      color: "var(--ink-1)"
    }
  }, supersededBy), ". Retained as evidence for its original scope.") : null, abstract ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      columnGap: "var(--space-5)",
      rowGap: 6,
      marginTop: "var(--space-6)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...label,
      flex: "0 0 128px",
      color: "var(--ink-3)",
      paddingTop: 6
    }
  }, "Abstract"), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: "1 1 320px",
      maxWidth: "var(--measure)",
      font: "var(--type-lede)",
      fontSize: "1.1875rem",
      color: "var(--ink-1)",
      textWrap: "pretty"
    }
  }, abstract)) : null, meta.length ? /*#__PURE__*/React.createElement("dl", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))",
      gap: 0,
      margin: "var(--space-6) 0 0",
      borderTop: "1px solid var(--rule-2)"
    }
  }, meta.map((m, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      padding: "10px 16px 10px 0",
      borderBottom: "1px solid var(--rule-1)"
    }
  }, /*#__PURE__*/React.createElement("dt", {
    style: {
      ...label,
      fontSize: "0.625rem",
      color: "var(--ink-3)",
      marginBottom: 4
    }
  }, m.label), /*#__PURE__*/React.createElement("dd", {
    style: {
      margin: 0,
      font: m.mono ? "400 0.75rem/1.5 var(--font-mono)" : "var(--type-meta)",
      fontVariationSettings: m.mono ? '"wdth" var(--mono-wdth)' : "normal",
      color: "var(--ink-1)"
    }
  }, m.value)))) : null);
}
Object.assign(__ds_scope, { DocHeader });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/document/DocHeader.jsx", error: String((e && e.message) || e) }); }

// components/document/Lineage.jsx
try { (() => {
/* Document lineage: a vertical descent line linking versions/supersessions, newest first. */
function Lineage({
  items = [],
  title = "Lineage"
}) {
  const label = {
    font: "var(--type-label)",
    fontVariationSettings: '"wdth" var(--mono-wdth)',
    textTransform: "uppercase",
    letterSpacing: "var(--tracking-label)"
  };
  return /*#__PURE__*/React.createElement("section", {
    style: {
      margin: "0 0 var(--space-6)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      ...label,
      color: "var(--ink-3)",
      marginBottom: 10
    }
  }, title), /*#__PURE__*/React.createElement("ol", {
    style: {
      listStyle: "none",
      margin: 0,
      padding: 0
    }
  }, items.map((it, i) => {
    const last = i === items.length - 1;
    const past = it.status === "superseded" || it.status === "historical";
    return /*#__PURE__*/React.createElement("li", {
      key: i,
      style: {
        display: "grid",
        gridTemplateColumns: "14px minmax(0,1fr)",
        columnGap: 12
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        position: "relative",
        display: "flex",
        justifyContent: "center"
      }
    }, !last ? /*#__PURE__*/React.createElement("span", {
      style: {
        position: "absolute",
        top: 14,
        bottom: 0,
        width: 1,
        background: past ? "var(--rule-2)" : "var(--rule-3)",
        left: 6.5
      }
    }) : null, /*#__PURE__*/React.createElement("span", {
      style: {
        marginTop: 5,
        background: "var(--paper-0)",
        position: "relative"
      }
    }, /*#__PURE__*/React.createElement(__ds_scope.StatusGlyph, {
      status: it.status || "accepted",
      size: 11
    }))), /*#__PURE__*/React.createElement("div", {
      style: {
        paddingBottom: last ? 0 : 14
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        flexWrap: "wrap",
        gap: "2px 10px",
        alignItems: "baseline"
      }
    }, /*#__PURE__*/React.createElement("code", {
      style: {
        fontFamily: "var(--font-mono)",
        fontVariationSettings: '"wdth" var(--mono-wdth)',
        fontSize: "0.75rem",
        color: past ? "var(--ink-3)" : "var(--ink-1)"
      }
    }, it.id), it.date ? /*#__PURE__*/React.createElement("span", {
      style: {
        ...label,
        fontSize: "0.625rem",
        textTransform: "none",
        letterSpacing: 0,
        color: "var(--ink-3)"
      }
    }, it.date) : null), /*#__PURE__*/React.createElement("div", {
      style: {
        font: "var(--type-meta)",
        fontSize: "0.875rem",
        color: past ? "var(--ink-3)" : "var(--ink-1)"
      }
    }, it.title), it.relation ? /*#__PURE__*/React.createElement("div", {
      style: {
        font: "italic 400 0.8125rem/1.4 var(--font-serif)",
        color: "var(--ink-2)",
        marginTop: 2
      }
    }, it.relation) : null));
  })));
}
Object.assign(__ds_scope, { Lineage });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/document/Lineage.jsx", error: String((e && e.message) || e) }); }

// components/document/SectionHeading.jsx
try { (() => {
function SectionHeading({
  number,
  title,
  level = 2,
  id,
  kicker
}) {
  const Tag = level === 3 ? "h3" : "h2";
  const two = level !== 3;
  return /*#__PURE__*/React.createElement(Tag, {
    id: id,
    style: {
      display: "flex",
      flexWrap: "wrap",
      alignItems: "baseline",
      columnGap: "var(--space-5)",
      margin: two ? "var(--space-8) 0 var(--space-4)" : "var(--space-6) 0 var(--space-3)",
      paddingTop: two ? "var(--space-4)" : 0,
      borderTop: two ? "1px solid var(--rule-2)" : "none",
      font: two ? "var(--type-h2)" : "var(--type-h3)",
      color: "var(--ink-1)",
      scrollMarginTop: 24
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      flex: "0 0 128px",
      font: "var(--type-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      fontSize: two ? "0.75rem" : "0.6875rem",
      color: "var(--ink-3)",
      letterSpacing: "0.02em"
    }
  }, number ? `§ ${number}` : "", kicker ? /*#__PURE__*/React.createElement("span", {
    style: {
      display: "block",
      textTransform: "uppercase",
      letterSpacing: "var(--tracking-label)",
      marginTop: 4
    }
  }, kicker) : null), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: "1 1 280px",
      textWrap: "balance"
    }
  }, title));
}
Object.assign(__ds_scope, { SectionHeading });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/document/SectionHeading.jsx", error: String((e && e.message) || e) }); }

// components/document/SourceList.jsx
try { (() => {
const KIND = {
  design: "design",
  code: "src",
  test: "test",
  adr: "adr",
  study: "study",
  doc: "doc",
  config: "config"
};
function SourceList({
  title = "Principal sources",
  items = []
}) {
  const label = {
    font: "var(--type-label)",
    fontVariationSettings: '"wdth" var(--mono-wdth)',
    textTransform: "uppercase",
    letterSpacing: "var(--tracking-label)"
  };
  return /*#__PURE__*/React.createElement("section", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      columnGap: "var(--space-5)",
      rowGap: 8,
      borderTop: "1px solid var(--rule-2)",
      padding: "var(--space-4) 0",
      margin: "var(--space-6) 0"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...label,
      flex: "0 0 128px",
      color: "var(--ink-3)",
      paddingTop: 3
    }
  }, title), /*#__PURE__*/React.createElement("ul", {
    style: {
      flex: "1 1 320px",
      listStyle: "none",
      margin: 0,
      padding: 0,
      display: "grid",
      gap: 6
    }
  }, items.map((it, i) => /*#__PURE__*/React.createElement("li", {
    key: i,
    style: {
      display: "flex",
      gap: 12,
      alignItems: "baseline",
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...label,
      fontSize: "0.5625rem",
      width: 44,
      flex: "none",
      color: "var(--ink-3)"
    }
  }, KIND[it.kind] || it.kind || ""), /*#__PURE__*/React.createElement("span", {
    style: {
      minWidth: 0
    }
  }, it.href ? /*#__PURE__*/React.createElement("a", {
    href: it.href,
    style: {
      fontFamily: "var(--font-mono)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      fontSize: "0.75rem",
      wordBreak: "break-all"
    }
  }, it.path) : /*#__PURE__*/React.createElement("code", {
    style: {
      fontFamily: "var(--font-mono)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      fontSize: "0.75rem",
      color: "var(--ink-1)",
      wordBreak: "break-all"
    }
  }, it.path), it.note ? /*#__PURE__*/React.createElement("span", {
    style: {
      font: "var(--type-meta)",
      color: "var(--ink-3)",
      marginLeft: 8
    }
  }, it.note) : null)))));
}
Object.assign(__ds_scope, { SourceList });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/document/SourceList.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Breadcrumb.jsx
try { (() => {
function Breadcrumb({
  items = [],
  onSelect
}) {
  return /*#__PURE__*/React.createElement("nav", {
    "aria-label": "Breadcrumb",
    style: {
      display: "flex",
      flexWrap: "wrap",
      alignItems: "center",
      gap: 8,
      fontFamily: "var(--font-mono)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      fontSize: "0.6875rem",
      color: "var(--ink-3)"
    }
  }, items.map((it, i) => {
    const last = i === items.length - 1;
    return /*#__PURE__*/React.createElement(React.Fragment, {
      key: i
    }, last ? /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--ink-1)"
      }
    }, it.label) : /*#__PURE__*/React.createElement("a", {
      href: it.href || "#",
      onClick: e => {
        if (onSelect) {
          e.preventDefault();
          onSelect(it, i);
        }
      },
      style: {
        color: "var(--ink-3)",
        textDecoration: "none"
      }
    }, it.label), !last ? /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        color: "var(--rule-3)"
      }
    }, "/") : null);
  }));
}
Object.assign(__ds_scope, { Breadcrumb });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Breadcrumb.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Button.jsx
try { (() => {
function Button({
  variant = "secondary",
  size = "md",
  disabled = false,
  onClick,
  children,
  type = "button"
}) {
  const [hover, setHover] = React.useState(false);
  const h = size === "sm" ? 28 : 34;
  const v = disabled ? {
    primary: {
      bg: "var(--paper-1)",
      fg: "var(--ink-3)",
      ring: "var(--rule-2)"
    },
    secondary: {
      bg: "var(--paper-1)",
      fg: "var(--ink-3)",
      ring: "var(--rule-2)"
    },
    quiet: {
      bg: "transparent",
      fg: "var(--ink-3)",
      ring: "transparent"
    }
  }[variant] : {
    primary: {
      bg: hover ? "var(--ink-2)" : "var(--ink-1)",
      fg: "var(--paper-0)",
      ring: "transparent"
    },
    secondary: {
      bg: hover ? "var(--paper-1)" : "transparent",
      fg: "var(--ink-1)",
      ring: hover ? "var(--rule-ink)" : "var(--rule-3)"
    },
    quiet: {
      bg: "transparent",
      fg: hover ? "var(--ink-1)" : "var(--ink-2)",
      ring: "transparent"
    }
  }[variant];
  return /*#__PURE__*/React.createElement("button", {
    type: type,
    disabled: disabled,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
      height: h,
      padding: variant === "quiet" ? "0 4px" : `0 ${size === "sm" ? 12 : 16}px`,
      background: v.bg,
      color: v.fg,
      border: 0,
      boxShadow: `inset 0 0 0 1px ${v.ring}`,
      borderRadius: "var(--radius-1)",
      font: size === "sm" ? "var(--type-label)" : "var(--type-meta)",
      cursor: disabled ? "not-allowed" : "pointer",
      opacity: 1,
      textDecoration: variant === "quiet" ? "underline" : "none",
      textUnderlineOffset: "0.25em",
      textDecorationColor: hover ? "currentColor" : "var(--rule-3)",
      transition: "background var(--dur-1) var(--ease), box-shadow var(--dur-1) var(--ease)"
    }
  }, children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Button.jsx", error: String((e && e.message) || e) }); }

// components/navigation/DocNav.jsx
try { (() => {
function DocNav({
  sections = [],
  activeId,
  onSelect,
  header
}) {
  const label = {
    font: "var(--type-label)",
    fontVariationSettings: '"wdth" var(--mono-wdth)',
    textTransform: "uppercase",
    letterSpacing: "var(--tracking-label)"
  };
  return /*#__PURE__*/React.createElement("nav", {
    "aria-label": "Documentation",
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-5)",
      font: "var(--type-meta)",
      fontSize: "0.875rem"
    }
  }, header, sections.map((s, si) => /*#__PURE__*/React.createElement("div", {
    key: si
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      ...label,
      display: "flex",
      alignItems: "center",
      gap: 7,
      color: "var(--ink-3)",
      padding: "0 0 6px",
      borderBottom: "1px solid var(--rule-1)",
      marginBottom: 4
    }
  }, s.domain ? /*#__PURE__*/React.createElement(__ds_scope.DomainGlyph, {
    domain: s.domain,
    size: 8
  }) : null, s.label), /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: "none",
      margin: 0,
      padding: 0
    }
  }, s.items.map(it => {
    const active = it.id === activeId;
    return /*#__PURE__*/React.createElement("li", {
      key: it.id
    }, /*#__PURE__*/React.createElement("a", {
      href: `#${it.id}`,
      onClick: e => {
        if (onSelect) {
          e.preventDefault();
          onSelect(it.id);
        }
      },
      "aria-current": active ? "page" : undefined,
      style: {
        display: "flex",
        alignItems: "baseline",
        gap: 8,
        padding: "4px 0 4px 10px",
        marginLeft: -1,
        borderLeft: active ? "1px solid var(--rule-ink)" : "1px solid transparent",
        color: active ? "var(--ink-1)" : it.status === "superseded" ? "var(--ink-3)" : "var(--ink-2)",
        fontWeight: active ? 600 : 400,
        textDecoration: "none",
        lineHeight: 1.35
      }
    }, it.number ? /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: "var(--font-mono)",
        fontVariationSettings: '"wdth" var(--mono-wdth)',
        fontSize: "0.6875rem",
        color: "var(--ink-3)",
        fontWeight: 400,
        minWidth: 22
      }
    }, it.number) : null, /*#__PURE__*/React.createElement("span", {
      style: {
        flex: 1,
        textDecoration: it.status === "superseded" ? "line-through" : "none",
        textDecorationColor: "var(--rule-3)"
      }
    }, it.label), it.status ? /*#__PURE__*/React.createElement("span", {
      style: {
        alignSelf: "center"
      }
    }, /*#__PURE__*/React.createElement(__ds_scope.StatusGlyph, {
      status: it.status,
      size: 8
    })) : null));
  })))));
}
Object.assign(__ds_scope, { DocNav });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/DocNav.jsx", error: String((e && e.message) || e) }); }

// components/navigation/SearchField.jsx
try { (() => {
function SearchField({
  value,
  onChange,
  placeholder = "Search the corpus",
  shortcut = "/",
  width = "100%"
}) {
  const [focus, setFocus] = React.useState(false);
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      width,
      height: 34,
      padding: "0 10px",
      background: "var(--paper-0)",
      boxShadow: `inset 0 0 0 1px ${focus ? "var(--rule-ink)" : "var(--rule-2)"}`,
      borderRadius: "var(--radius-1)",
      transition: "box-shadow var(--dur-1) var(--ease)"
    }
  }, /*#__PURE__*/React.createElement("svg", {
    width: "13",
    height: "13",
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "var(--ink-3)",
    strokeWidth: "1.8",
    strokeLinecap: "round",
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("circle", {
    cx: "11",
    cy: "11",
    r: "7"
  }), /*#__PURE__*/React.createElement("path", {
    d: "m20 20-4-4"
  })), /*#__PURE__*/React.createElement("input", {
    value: value,
    onChange: e => onChange && onChange(e.target.value),
    placeholder: placeholder,
    onFocus: () => setFocus(true),
    onBlur: () => setFocus(false),
    style: {
      flex: 1,
      minWidth: 0,
      border: 0,
      outline: 0,
      background: "transparent",
      font: "var(--type-meta)",
      fontSize: "0.875rem",
      color: "var(--ink-1)"
    }
  }), shortcut ? /*#__PURE__*/React.createElement("kbd", {
    style: {
      fontFamily: "var(--font-mono)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      fontSize: "0.625rem",
      color: "var(--ink-3)",
      padding: "1px 5px",
      boxShadow: "inset 0 0 0 1px var(--rule-2)",
      borderRadius: "var(--radius-1)"
    }
  }, shortcut) : null);
}
Object.assign(__ds_scope, { SearchField });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/SearchField.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Toc.jsx
try { (() => {
function Toc({
  items = [],
  activeId,
  title = "On this page",
  onSelect
}) {
  return /*#__PURE__*/React.createElement("nav", {
    "aria-label": title,
    style: {
      font: "var(--type-meta)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: "var(--type-label)",
      fontVariationSettings: '"wdth" var(--mono-wdth)',
      textTransform: "uppercase",
      letterSpacing: "var(--tracking-label)",
      color: "var(--ink-3)",
      marginBottom: 8
    }
  }, title), /*#__PURE__*/React.createElement("ol", {
    style: {
      listStyle: "none",
      margin: 0,
      padding: 0,
      borderLeft: "1px solid var(--rule-1)"
    }
  }, items.map(it => {
    const active = it.id === activeId;
    return /*#__PURE__*/React.createElement("li", {
      key: it.id
    }, /*#__PURE__*/React.createElement("a", {
      href: `#${it.id}`,
      onClick: e => {
        if (onSelect) {
          e.preventDefault();
          onSelect(it.id);
        }
      },
      style: {
        display: "flex",
        gap: 8,
        padding: `3px 0 3px ${it.level === 3 ? 24 : 12}px`,
        marginLeft: -1,
        borderLeft: active ? "1px solid var(--rule-ink)" : "1px solid transparent",
        color: active ? "var(--ink-1)" : "var(--ink-3)",
        textDecoration: "none",
        lineHeight: 1.4
      }
    }, it.number ? /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: "var(--font-mono)",
        fontVariationSettings: '"wdth" var(--mono-wdth)',
        fontSize: "0.6875rem",
        minWidth: 20
      }
    }, it.number) : null, /*#__PURE__*/React.createElement("span", null, it.label)));
  })));
}
Object.assign(__ds_scope, { Toc });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Toc.jsx", error: String((e && e.message) || e) }); }

// ui_kits/docs/ScreenAdr.jsx
try { (() => {
function ScreenAdr() {
  const {
    DocHeader,
    SectionHeading,
    DecisionList,
    Callout,
    Lineage
  } = window.SymbiontDesignSystem_45c50a;
  return /*#__PURE__*/React.createElement("article", null, /*#__PURE__*/React.createElement(DocHeader, {
    docType: "adr",
    id: "ADR-0011 \xB7 ADR-EW-004",
    status: "partially-superseded",
    domains: ["modality", "embodiment"],
    title: "Visual apparatus and perceptual topology",
    meta: [{
      label: "Status",
      value: "Accepted. Decision 2 is reversible."
    }, {
      label: "Introduced in",
      value: "Milestone EW-C"
    }, {
      label: "Superseded in part by",
      value: "ADR-0066",
      mono: true
    }]
  }), /*#__PURE__*/React.createElement(Callout, {
    kind: "superseded",
    id: "2026-10-04",
    supersededBy: "ADR-0066"
  }, "After the substrate cut the array is sampled by a deterministic CPU ray caster owned by modality rather than by the physics engine's renderer. The receptor contract, topology, cadence and isolation rules here remain authoritative."), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "1",
    title: "Context",
    id: "context"
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("p", null, "The Experience & World specification requires Vision to arrive as a causal apparatus: physical world \u2192 apparatus \u2192 physical sample \u2192 opaque receptor channels \u2192 cognition. Observer geometry (", /*#__PURE__*/React.createElement("code", null, "world_scene"), ", ", /*#__PURE__*/React.createElement("code", null, "PhysicsWorldObserver.entities"), ") is not a valid substitute.")), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "2",
    title: "Decision",
    id: "decision"
  }), /*#__PURE__*/React.createElement(DecisionList, {
    items: [{
      title: "Topology",
      body: /*#__PURE__*/React.createElement(React.Fragment, null, "Physical receptor adjacency is apparatus-given structure. Grouping into sources is acquired structure. The apparatus owns a ", /*#__PURE__*/React.createElement("code", null, "PerceptualTopology"), ": neighbour lists over opaque receptor ids.")
    }, {
      title: "A new body kind, not a modified body",
      status: "intended",
      statusDetail: "reversible",
      body: /*#__PURE__*/React.createElement(React.Fragment, null, "Vision ships as ", /*#__PURE__*/React.createElement("code", null, "anthropomorphic-v6-vision"), ". The receptor contract of ", /*#__PURE__*/React.createElement("code", null, "anthropomorphic-v6"), " is left unchanged.")
    }, {
      title: "Apparatus",
      status: "superseded",
      statusDetail: "renderer identity · ADR-0066",
      body: "A single receptor array is mounted on the head link. Each receptor delivers a bounded luminance value in [0, 1]."
    }, {
      title: "Size and sensory budget",
      body: "The array is 12×12 (144 receptors). BodyDescriptor.sensory_capacity makes the budget per body: 256 for every existing body, 512 for the vision body."
    }, {
      title: "Opaque identities",
      body: "Visual receptors extend the existing rec.N namespace (rec.107–rec.250) through a fixed, versioned permutation of array positions."
    }]
  }), /*#__PURE__*/React.createElement(Callout, {
    kind: "evidence",
    title: "Closed by EW-D0 (2026-09-28/29)",
    strength: 2,
    scope: "seed 11, 6 \xD7 250 ticks",
    status: "observed"
  }, "Sensors 387 \u2192 413 \u2192 428 \u2192 434 \u2192 440 \u2192 440: plateau below the 512 capacity, 0 capacity rejections."), /*#__PURE__*/React.createElement(Callout, {
    kind: "limitation",
    title: "Open: bundle growth"
  }, "The portable bundle grows ~3.5 MB per 250 ticks (29 MB at 1500) without plateau \u2014 an age-dependent storage concern (Gate J), not a sensory-budget one."), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "3",
    title: "Consequences",
    id: "consequences"
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("ul", null, /*#__PURE__*/React.createElement("li", null, "Gate D (visual acquisition) is not claimed. EW-C delivers only the substrate."), /*#__PURE__*/React.createElement("li", null, "Raw receptor-field observer transport is not chosen here. It must be benchmarked before any Vision UI."))), /*#__PURE__*/React.createElement(Lineage, {
    items: [{
      id: "ADR-0066",
      title: "MuJoCo physics engine and engine-independent vision",
      status: "accepted",
      date: "2026-10-04",
      relation: "supersedes decision 3 (renderer identity) of"
    }, {
      id: "ADR-0011",
      title: "Visual apparatus and perceptual topology",
      status: "partially-superseded"
    }]
  }));
}
window.ScreenAdr = ScreenAdr;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/docs/ScreenAdr.jsx", error: String((e && e.message) || e) }); }

// ui_kits/docs/ScreenChapter.jsx
try { (() => {
function BoundaryDiagram() {
  const {
    DomainGlyph
  } = window.SymbiontDesignSystem_45c50a;
  const nodes = [["environment", "World", "external state and dynamics"], ["embodiment", "Body", "physical substrate"], ["embodiment", "Embodiment", "bounded relationship"], ["symbiont", "Symbiont", "persistent organism"]];
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      alignItems: "stretch",
      width: "100%",
      gap: 0
    }
  }, nodes.map(([d, n, s], i) => /*#__PURE__*/React.createElement(React.Fragment, {
    key: n
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: "1 1 120px",
      padding: "14px 14px 12px",
      borderTop: `2px solid var(--dom-${d})`,
      background: "var(--night-1)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8
    }
  }, /*#__PURE__*/React.createElement(DomainGlyph, {
    domain: d,
    size: 9
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      font: "500 15px/1.2 var(--font-sans)",
      color: "var(--night-ink-1)"
    }
  }, n)), /*#__PURE__*/React.createElement("div", {
    style: {
      font: "12px/1.4 var(--font-sans)",
      color: "var(--night-ink-2)",
      marginTop: 6
    }
  }, s)), i < nodes.length - 1 ? /*#__PURE__*/React.createElement("div", {
    style: {
      flex: "0 0 36px",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontFamily: "var(--font-mono)",
      fontSize: 12,
      color: "var(--night-ink-3)"
    }
  }, "\u2260") : null)));
}
function ScreenChapter() {
  const {
    DocHeader,
    SectionHeading,
    Figure,
    Callout,
    SourceList
  } = window.SymbiontDesignSystem_45c50a;
  return /*#__PURE__*/React.createElement("article", null, /*#__PURE__*/React.createElement(DocHeader, {
    docType: "chapter",
    id: "\xA7 03",
    status: "implemented",
    domains: ["environment", "embodiment", "symbiont"],
    title: "World, body and embodiment",
    subtitle: "Why three entities are required",
    abstract: "A body is not an organism and an embodiment is not a body. The distinction is easiest to see during change.",
    meta: [{
      label: "Source",
      value: "symbiont/docs/03-world-body-and-embodiment.md",
      mono: true
    }, {
      label: "Runtime",
      value: "Physics3D"
    }, {
      label: "Read next",
      value: "§ 04 Perception"
    }]
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("p", null, "If the same Symbiont is moved from one anthropomorphic body to a crawler, the organism persists, the old physical body does not, and the relationship between organism and physical surface is rebuilt. Calling all three \u201Cthe body\u201D makes it impossible to say what was learned, what was retained and what must be reacquired.")), /*#__PURE__*/React.createElement(Figure, {
    number: "3.1",
    tone: "night",
    caption: "The four entities of the boundary. Each is owned by a different domain; none may be inferred from another.",
    source: "symbiont/docs/index.md"
  }, /*#__PURE__*/React.createElement(BoundaryDiagram, null)), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "3.1",
    title: "Physical body",
    id: "body"
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("p", null, "In Physics3D the body is represented by PyBullet state plus an apparatus implementation. Body descriptors define the available receptor and effector sets. The runtime stores physical body identity explicitly; it does not infer identity from physical state or migrate older checkpoint formats."), /*#__PURE__*/React.createElement("p", null, "The body can be affected without cognition. Gravity, collision, joint limits, surface contact and environmental forces are physical dynamics. The laboratory can inspect them even when no corresponding internal representation exists.")), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "3.2",
    title: "Apparatus",
    id: "apparatus",
    level: 3
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("p", null, "The apparatus is the interface exposed by the body. On the incoming side it supplies receptor values. On the outgoing side it accepts validated actuator channels.")), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "3.3",
    title: "Embodiment contract",
    id: "contract"
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("p", null, "The core ", /*#__PURE__*/React.createElement("code", null, "EmbodimentContract"), " binds a perceptual surface, actuator surface, timing contract and mutually exclusive actuator groups. In Physics3D this contract is derived from the actual apparatus counts and effector constraints.")), /*#__PURE__*/React.createElement(Callout, {
    kind: "implementation",
    source: "src/symbiont/core/embodiment/contract.py"
  }, "The contract captures the actionable/sensible surface without claiming that the organism knows the anatomical meaning of those channels."), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "3.4",
    title: "Body schema",
    id: "schema"
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("p", null, /*#__PURE__*/React.createElement("code", null, "BodySchemaEngine"), " is organism-owned inferred structure. It is not a mirror of the PyBullet model. It is built from relationships available through experience and should therefore be read as an internal model of sensorimotor organisation rather than a copy of external anatomy.")), /*#__PURE__*/React.createElement(Callout, {
    kind: "limitation",
    title: "Observatory views are observer reconstructions"
  }, "A human-friendly skeletal view may draw a right arm because the observer knows the body's morphology. The organism's schema may contain only opaque channels, learned couplings and confidence about their relations."), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "3.5",
    title: "What should survive a body change?",
    id: "survive"
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("p", null, "The answer is not \u201Ceverything\u201D or \u201Cnothing\u201D. Persistence is mechanism-specific. Organism identity, genome and general cognitive history may survive; physical pose and body integrity do not.")), /*#__PURE__*/React.createElement(SourceList, {
    items: [{
      kind: "design",
      path: "docs/design/embodiment/embodiment-v2.md"
    }, {
      kind: "design",
      path: "docs/design/embodiment/embodiment-memory-v1.md"
    }, {
      kind: "code",
      path: "src/symbiont/core/embodiment/body_schema.py"
    }, {
      kind: "code",
      path: "src/symbiont_lab/physics3d/apparatus.py"
    }]
  }));
}
window.ScreenChapter = ScreenChapter;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/docs/ScreenChapter.jsx", error: String((e && e.message) || e) }); }

// ui_kits/docs/ScreenEvidence.jsx
try { (() => {
function ScreenEvidence() {
  const {
    DocHeader,
    SectionHeading,
    DataTable,
    StatusMark,
    Callout,
    CodeBlock
  } = window.SymbiontDesignSystem_45c50a;
  const rows = [["E1", "Yoked External Causation", "negative", "H1 not supported"], ["E2", "Tool / Body Distinction", "negative", "H1 not supported"], ["E3", "Temporal Causality", "negative", "H1 not supported"], ["E4", "Causal Revision", "negative", "H1 not supported"], ["E5", "Somatic Correlation Trap", "negative", "H1 not supported"], ["E6", "Hidden Common Cause", "negative", "H1 not supported"], ["E7", "Heredity Leakage", "supported", "no learned-state leakage observed in tested scope"], ["E8", "Label Invariance", "failing", "fails; open P0 integrity issue"]].map(([e, n, s, r]) => ({
    e,
    n,
    s: /*#__PURE__*/React.createElement(StatusMark, {
      status: s,
      size: "sm"
    }),
    r
  }));
  return /*#__PURE__*/React.createElement("article", null, /*#__PURE__*/React.createElement(DocHeader, {
    docType: "study",
    id: "E1\u2013E8",
    status: "frozen",
    domains: ["lab", "embodiment"],
    title: "Embodied agency: unified falsification battery",
    abstract: "Current embodiment evidence includes a unified falsification battery. These results define the next causal research problem; they are not defects to edit away.",
    meta: [{
      label: "Programme",
      value: "Embodied Agency E1–E6"
    }, {
      label: "Record",
      value: "lab/research/STATUS.md",
      mono: true
    }, {
      label: "Owner gate",
      value: "Scientific protocol"
    }]
  }), /*#__PURE__*/React.createElement(Callout, {
    kind: "warning",
    title: "E8 Label Invariance fails",
    status: "failing"
  }, "P0 experimental-integrity failure; remediation required."), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "1",
    title: "Results",
    id: "results"
  }), /*#__PURE__*/React.createElement(DataTable, {
    number: "1",
    caption: "Battery outcomes. Negative results are retained and are not rewritten when later work changes the mechanism.",
    columns: [{
      key: "e",
      label: "Exp.",
      mono: true,
      width: 60
    }, {
      key: "n",
      label: "Experiment"
    }, {
      key: "s",
      label: "Status",
      width: 150
    }, {
      key: "r",
      label: "Result"
    }],
    rows: rows
  }), /*#__PURE__*/React.createElement(Callout, {
    kind: "principle"
  }, "A capability being implemented does not establish scientific generalisation. A completed experiment remains bounded by its preregistered conditions."), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "2",
    title: "Evidence lifecycle",
    id: "lifecycle"
  }), /*#__PURE__*/React.createElement(CodeBlock, {
    language: "text",
    title: "lab/research/README.md",
    code: "PLANNED PREREGISTERED RUNNING DISCOVERY PARTIAL SUPPORTED NEGATIVE\nINCONCLUSIVE SUPERSEDED FROZEN"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      gap: "10px 20px",
      marginBottom: 24
    }
  }, ["planned", "preregistered", "running", "discovery", "partial", "supported", "negative", "inconclusive", "superseded", "frozen"].map(s => /*#__PURE__*/React.createElement(StatusMark, {
    key: s,
    status: s
  }))), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "3",
    title: "Reproduce",
    id: "reproduce"
  }), /*#__PURE__*/React.createElement(CodeBlock, {
    tone: "night",
    language: "bash",
    title: "validation layers",
    code: "pytest -o addopts= tests/integration tests/experimental_integrity\npytest -o addopts= tests/contract tests/experiments\npython scripts/agentctl.py verify   # governance check"
  }), /*#__PURE__*/React.createElement(Callout, {
    kind: "note"
  }, "Held-out, confirmation and replication runs require an explicit owner decision before launch."));
}
window.ScreenEvidence = ScreenEvidence;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/docs/ScreenEvidence.jsx", error: String((e && e.message) || e) }); }

// ui_kits/docs/ScreenGlossary.jsx
try { (() => {
function ScreenGlossary() {
  const {
    DocHeader,
    SectionHeading,
    StatusMark
  } = window.SymbiontDesignSystem_45c50a;
  const Term = ({
    t,
    children,
    mono
  }) => /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      columnGap: 24,
      rowGap: 4,
      padding: "14px 0",
      borderBottom: "1px solid var(--rule-1)"
    }
  }, /*#__PURE__*/React.createElement("dt", {
    style: {
      flex: "0 0 200px",
      font: "600 var(--fs-body)/1.4 var(--font-sans)"
    }
  }, t), /*#__PURE__*/React.createElement("dd", {
    style: {
      flex: "1 1 320px",
      margin: 0,
      font: "var(--type-body)",
      maxWidth: "62ch",
      textWrap: "pretty"
    }
  }, children));
  return /*#__PURE__*/React.createElement("article", null, /*#__PURE__*/React.createElement(DocHeader, {
    docType: "reference",
    id: "root.glossary",
    domains: ["symbiont", "lab"],
    title: "Glossary of epistemological and experimental terms"
  }), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "1",
    title: "Experimental hierarchy",
    id: "hier"
  }), /*#__PURE__*/React.createElement("dl", {
    style: {
      margin: 0
    }
  }, /*#__PURE__*/React.createElement(Term, {
    t: "Protocol"
  }, "A defined scientific procedure and measurement methodology (e.g. ", /*#__PURE__*/React.createElement("code", {
    className: "ic"
  }, "attention.causal"), "). Independent of software versions."), /*#__PURE__*/React.createElement(Term, {
    t: "Experiment"
  }, "A specific hypothesis-driven investigation bound to concrete parameters, hypotheses, and success criteria."), /*#__PURE__*/React.createElement(Term, {
    t: "Run"
  }, "A single deterministic execution of an experiment or protocol under a single world seed and parameter configuration."), /*#__PURE__*/React.createElement(Term, {
    t: "Study"
  }, "A collection of comparable runs across parameter sweeps and replication seeds.")), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "2",
    title: "Artifact status lifecycle",
    id: "life"
  }), /*#__PURE__*/React.createElement("dl", {
    style: {
      margin: 0
    }
  }, /*#__PURE__*/React.createElement(Term, {
    t: /*#__PURE__*/React.createElement(StatusMark, {
      status: "working"
    })
  }, "Mutable local run or prototype results residing in ", /*#__PURE__*/React.createElement("code", {
    className: "ic"
  }, ".symbiont/"), ". Not tracked in version control."), /*#__PURE__*/React.createElement(Term, {
    t: /*#__PURE__*/React.createElement(StatusMark, {
      status: "validated"
    })
  }, "Run or study that has passed all protocol invariants, integrity assertions, and replication criteria."), /*#__PURE__*/React.createElement(Term, {
    t: /*#__PURE__*/React.createElement(StatusMark, {
      status: "frozen"
    })
  }, "Formally accepted scientific record archived in ", /*#__PURE__*/React.createElement("code", {
    className: "ic"
  }, "research/"), ". Immutable baseline for publications and future comparisons."), /*#__PURE__*/React.createElement(Term, {
    t: /*#__PURE__*/React.createElement(StatusMark, {
      status: "superseded"
    })
  }, "Historical study preserved in ", /*#__PURE__*/React.createElement("code", {
    className: "ic"
  }, "research/"), " whose methodological premise was found flawed or refined by a subsequent audit.")), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "3",
    title: "Organism vocabulary",
    id: "org"
  }), /*#__PURE__*/React.createElement("dl", {
    style: {
      margin: 0
    }
  }, /*#__PURE__*/React.createElement(Term, {
    t: "Genome"
  }, "The closed, versioned, kernel-validated configuration for one individual's development."), /*#__PURE__*/React.createElement(Term, {
    t: "Phenotype"
  }, "The plastic cognitive graph (nodes/edges/weights) an individual develops during its life, distinct from its genome."), /*#__PURE__*/React.createElement(Term, {
    t: "EmbodimentEpisode"
  }, "One continuous period of one Symbiont in one Body. A new Body always starts a new episode; the previous one is closed and archived."), /*#__PURE__*/React.createElement(Term, {
    t: "Re-embodiment"
  }, "The canonical move of a Symbiont into a fresh Body: knowledge is carried, Body state is replaced, execution authority is withdrawn.")));
}
window.ScreenGlossary = ScreenGlossary;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/docs/ScreenGlossary.jsx", error: String((e && e.message) || e) }); }

// ui_kits/docs/ScreenIndex.jsx
try { (() => {
function ScreenIndex({
  onNavigate
}) {
  const {
    DocHeader,
    SectionHeading,
    CodeBlock,
    Callout,
    DataTable,
    DomainTag
  } = window.SymbiontDesignSystem_45c50a;
  const link = (id, t) => /*#__PURE__*/React.createElement("a", {
    href: `#${id}`,
    onClick: e => {
      e.preventDefault();
      onNavigate(id);
    }
  }, t);
  return /*#__PURE__*/React.createElement("article", null, /*#__PURE__*/React.createElement(DocHeader, {
    docType: "reference",
    id: "symbiont/docs/index.md",
    domains: ["symbiont"],
    title: "Symbiont \u2014 scientific description of the organism",
    abstract: "This corpus is the canonical entry point for studying Symbiont as a computational organism. It synthesizes design specifications, implementation notes and historical documents with the current implementation, and separates what exists from what was proposed."
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("p", null, "Symbiont should be read at three depths. A first reading explains the organism in ordinary scientific language. The anatomy documents then follow concrete processes end to end. The reference and atlas layers provide the exact ownership, implementation and causal relationships needed for verification.")), /*#__PURE__*/React.createElement(Callout, {
    kind: "principle",
    title: "The central architectural distinction"
  }, "A world contains external state and dynamics. A body is a physical substrate in that world. An embodiment is the historically bounded relationship between one Symbiont and one body contract. Symbiont is the persistent organism whose internal organization may survive the end of a particular body."), /*#__PURE__*/React.createElement(CodeBlock, {
    language: "text",
    code: "World != Body != Embodiment != Symbiont"
  }), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "1",
    title: "Reading path",
    id: "path"
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("p", null, "Start with ", link("c00", "Foundations and epistemology"), ", then read ", link("c01", "System and boundaries"), ". From there the natural path is lifecycle, embodiment, perception, physiology, cognition, agency, learning, generative cognition and social/lineage processes.")), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "2",
    title: "Five domains",
    id: "domains"
  }), /*#__PURE__*/React.createElement(DataTable, {
    columns: [{
      key: "d",
      label: "Domain",
      width: 170
    }, {
      key: "p",
      label: "Package",
      mono: true,
      width: 120
    }, {
      key: "r",
      label: "Responsibility"
    }],
    rows: [{
      d: /*#__PURE__*/React.createElement(DomainTag, {
        domain: "symbiont"
      }),
      p: "symbiont",
      r: "the organism / research subject"
    }, {
      d: /*#__PURE__*/React.createElement(DomainTag, {
        domain: "embodiment"
      }),
      p: "embodiment",
      r: "couplings between the organism and a concrete form of existence"
    }, {
      d: /*#__PURE__*/React.createElement(DomainTag, {
        domain: "modality"
      }),
      p: "modality",
      r: "signal channels; no cognitive meaning"
    }, {
      d: /*#__PURE__*/React.createElement(DomainTag, {
        domain: "environment"
      }),
      p: "environment",
      r: "external laws, dynamics and ground truth"
    }, {
      d: /*#__PURE__*/React.createElement(DomainTag, {
        domain: "lab"
      }),
      p: "lab",
      r: "composition, experiments, studies, observation, analysis"
    }]
  }), /*#__PURE__*/React.createElement(Callout, {
    kind: "invariant",
    id: "README \xA7Architecture"
  }, "symbiont, embodiment, modality and environment are peer, self-contained libraries: none imports another, none imports lab. Lab is the only composition root."), /*#__PURE__*/React.createElement(SectionHeading, {
    number: "3",
    title: "What is canonical here",
    id: "canonical"
  }), /*#__PURE__*/React.createElement("div", {
    className: "sym-prose"
  }, /*#__PURE__*/React.createElement("p", null, "This corpus is canonical for explanation of the current system. It does not make old specifications disappear. A specification answers \u201Cwhat was intended\u201D; this corpus answers \u201Chow the present system is organised and what evidence supports that description\u201D.")));
}
window.ScreenIndex = ScreenIndex;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/docs/ScreenIndex.jsx", error: String((e && e.message) || e) }); }

// ui_kits/docs/Shell.jsx
try { (() => {
const {
  DocNav,
  SearchField,
  Toc,
  Breadcrumb,
  DomainGlyph
} = window.SymbiontDesignSystem_45c50a;
const NAV = [{
  label: "Canonical corpus",
  domain: "symbiont",
  items: [{
    id: "index",
    label: "Scientific description"
  }, {
    id: "c00",
    number: "00",
    label: "Foundations and epistemology"
  }, {
    id: "c01",
    number: "01",
    label: "System and boundaries"
  }, {
    id: "c03",
    number: "03",
    label: "World, body and embodiment"
  }, {
    id: "c04",
    number: "04",
    label: "Perception and sensory development"
  }, {
    id: "c11",
    number: "11",
    label: "Persistence, provenance and re-embodiment"
  }]
}, {
  label: "Decisions",
  items: [{
    id: "adr11",
    number: "0011",
    label: "Visual apparatus and perceptual topology",
    status: "partially-superseded"
  }, {
    id: "adr13",
    number: "0013",
    label: "Longitudinal re-embodiment",
    status: "accepted"
  }]
}, {
  label: "Evidence",
  domain: "lab",
  items: [{
    id: "evidence",
    label: "Embodied agency E1–E8",
    status: "failing"
  }]
}, {
  label: "Reference",
  items: [{
    id: "glossary",
    label: "Glossary"
  }]
}];
function DocsShell({
  page,
  onNavigate,
  crumbs,
  toc,
  activeToc,
  children
}) {
  const [q, setQ] = React.useState("");
  return /*#__PURE__*/React.createElement("div", {
    className: "shell"
  }, /*#__PURE__*/React.createElement("aside", {
    className: "shell-nav"
  }, /*#__PURE__*/React.createElement("a", {
    href: "#index",
    onClick: e => {
      e.preventDefault();
      onNavigate("index");
    },
    style: {
      display: "block",
      marginBottom: 20
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logo/logo_horizontal.png",
    alt: "Symbiont",
    style: {
      height: 40,
      display: "block",
      marginLeft: -8
    }
  })), /*#__PURE__*/React.createElement(DocNav, {
    sections: NAV,
    activeId: page,
    onSelect: onNavigate,
    header: /*#__PURE__*/React.createElement(SearchField, {
      value: q,
      onChange: setQ
    })
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 32,
      paddingTop: 12,
      borderTop: "1px solid var(--rule-1)",
      display: "grid",
      gap: 6
    }
  }, ["symbiont", "embodiment", "modality", "environment", "lab"].map(d => /*#__PURE__*/React.createElement("span", {
    key: d,
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      fontFamily: "var(--font-mono)",
      fontVariationSettings: '"wdth" 87.5',
      fontSize: 10.5,
      color: "var(--ink-3)"
    }
  }, /*#__PURE__*/React.createElement(DomainGlyph, {
    domain: d,
    size: 8
  }), d, "/")))), /*#__PURE__*/React.createElement("main", {
    className: "shell-main"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: 32
    }
  }, /*#__PURE__*/React.createElement(Breadcrumb, {
    items: crumbs
  })), children, /*#__PURE__*/React.createElement("footer", {
    style: {
      marginTop: 96,
      paddingTop: 12,
      borderTop: "1px solid var(--rule-2)",
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "space-between",
      gap: 12,
      fontFamily: "var(--font-mono)",
      fontVariationSettings: '"wdth" 87.5',
      fontSize: 10.5,
      color: "var(--ink-3)"
    }
  }, /*#__PURE__*/React.createElement("span", null, "alessbarb/symbiont-lab \xB7 main"), /*#__PURE__*/React.createElement("span", null, "Historical results remain evidence for their original scope."))), /*#__PURE__*/React.createElement("aside", {
    className: "shell-toc"
  }, toc ? /*#__PURE__*/React.createElement(Toc, {
    items: toc,
    activeId: activeToc
  }) : null));
}
Object.assign(window, {
  DocsShell
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/docs/Shell.jsx", error: String((e && e.message) || e) }); }

// ui_kits/docs/doc-page.js
try { (() => {
// @ds-adherence-ignore -- omelette starter scaffold (raw elements/hex/px by design)
// Copied omelette starter. Re-running copy_starter_component with this kind overwrites this file with the latest version (page content is unaffected).
/* BEGIN USAGE */
/**
 * <doc-page> — paged-document shell for printable HTML.
 *
 * FIRST, decide how the document paginates — up front, before building:
 *
 * - FLOWING document (the default): write the whole document as one
 *   normal HTML flow inside <doc-page>; the browser's print engine
 *   splits it onto pages at export. Use for long-form documents with a
 *   single text flow: reports, memos, letters, essays.
 * - EXPLICIT pagination: a fixed set of pre-paginated pages, one
 *   <section class="page"> child per page. Use when the user asks for a
 *   specific page count, or the design implies one: a one-page resume, a
 *   two-sided flier, a poster, a certificate, a brochure — any richly
 *   laid-out document without a single text flow.
 * - If in doubt, ask the user as part of the build.
 *
 * PAGE SIZING — paper differs by country (letter vs A4), so the printed
 * sheet is not one fixed truth:
 * - FLOWING documents pin NO paper size: the print engine paginates
 *   onto the user's real paper, and the content reflows to it.
 * - EXPLICITLY PAGINATED documents print each page at a FIXED page box
 *   with overflow hidden — letter by default, size="a4" for a clearly
 *   metric user, the user's chosen paper when they export. Design each
 *   page to FILL that box, fitting letter and A4 alike without overlap.
 * - width/height pin an explicit fixed size, ONLY when the user gives
 *   one.
 * Never write your own @page rule or hard-code paper dimensions in the
 * content.
 *
 * Sizing modes (attributes):
 *   (none)                      — portrait: flowing docs use the user's
 *           paper; explicitly paginated pages use the named size box
 *           (letter unless size="a4")
 *   orientation="landscape"     — the same, landscape
 *   width / height              — explicit fixed size, ONLY when the user
 *           gives one (e.g. width="22in" height="30in" for a 22×30
 *           poster): the page IS the design's size, printed at true
 *           dimensions (or scaled onto the user's paper at print time).
 *           Any absolute CSS length: px/in/mm/cm/pt/pc.
 * The component announces the chosen mode to the host app at runtime (a
 * meta tag it injects), so the print path can inject the user's true
 * paper size.
 *
 * On screen the document renders on a desk background: a flowing
 * document as one tall scrolling sheet (Google Docs' pageless view);
 * explicitly paginated documents as one card per page.
 *
 * EXPLICIT pagination usage:
 *   <style>doc-page:not(:defined){visibility:hidden}</style>
 *   <doc-page>
 *     <section class="page" id="p1">…one page's design…</section>
 *     <section class="page" id="p2">…</section>
 *   </doc-page>
 *   <script src="doc-page.js"></script>
 * How the page box works, concretely: each .page prints as ONE full-bleed
 * sheet at a FIXED physical size — letter by default (set size="a4" for
 * a clearly metric user), the user's chosen paper when they export —
 * with overflow hidden. Nothing scrolls and nothing reflows onto a next
 * sheet: content that misses the box is CLIPPED. Design each page to
 * FILL that page box, and to fit it — letter and A4 alike — without
 * overlap. Each page is a size container; don't size anything in
 * viewport units (they track the window, not the page), and never set
 * width or height on the .page section itself (the component sizes the
 * page box; an authored height like 100% is meaningless at print and is
 * overridden). The component owns the page box, the screen card chrome,
 * and the page breaks (never add your own break-before/after). Don't mix
 * .page sections with flowing content or header/footer slots in the same
 * document.
 *
 * FLOWING usage:
 *   <style>doc-page:not(:defined){visibility:hidden}</style>
 *   <doc-page margin="0.75in">
 *     <h1>Title</h1>
 *     <p>…body…</p>
 *   </doc-page>
 *   <script src="doc-page.js"></script>
 * There is no manual page-splitting — the browser's print engine
 * paginates at export. Standard break-hygiene rules (`break-inside:
 * avoid` on figures, code blocks, images and table rows; `orphans/
 * widows: 3`) are applied so paragraphs and groups split cleanly. On
 * screen and at print, headings default to `text-wrap: balance` and
 * body text to `text-wrap: pretty`; the defaults have zero specificity,
 * so any text-wrap you declare wins.
 *
 * Other attributes:
 *   size    — letter | a4 | legal (default letter). Flowing documents:
 *           preview proportion only — it does NOT pin their printed
 *           paper (the print dialog's paper governs); leave it alone
 *           there. Explicitly paginated documents: it sets the page box
 *           the cards and the pinned @page share (the export dialog's
 *           choice overrides both at print) — set size="a4" for a
 *           clearly metric user. Scaled-fit: names the sheet the fit is
 *           computed against, same a4-for-metric-users advice.
 *   content-width / content-height — the design's own fixed dimensions
 *           (CSS lengths), for scaling a fixed-size design ONTO the
 *           named sheet: content lays out at exactly this size, and the
 *           component scales it to fit that sheet's printable area
 *           (centered horizontally, top-aligned; the export dialog
 *           re-fits to the user's actual paper choice where available).
 *           Both must be set; they do not change the page box. For pages
 *           WITHOUT running header/footer slots.
 *   margin  — printable inset on every page of a FLOWING document
 *           (default 0.75in); margin="0" makes pages full-bleed.
 *           Explicitly paginated pages are always full-bleed.
 *
 * Running header/footer (flowing documents only): give an element
 * `slot="header"` or `slot="footer"` and it repeats on every printed
 * page via `position: fixed`. To keep body text from sliding under it,
 * the component prints inside a single-cell table whose <thead>/<tfoot>
 * are spacers sized to the header/footer height — browsers repeat
 * thead/tfoot on every page, so each sheet's content starts below the
 * header and ends above the footer. On screen the header/footer render
 * once at the top/bottom of the sheet.
 *
 * At print the component injects `@page { margin: 0 }` (which leaves
 * Chrome no margin box to draw its date/URL/page-count header in) and
 * moves the visual margin onto the sheet's own padding. It also marks
 * the document as owning its print CSS (a
 * `meta[name="omelette-owns-print"]` it injects at runtime), so the
 * PDF export never injects page-geometry CSS of its own on top.
 *
 * Print best practices for the content you author:
 * - Multi-column text: use CSS columns (`column-count` +
 *   `column-gap`), never side-by-side flex/grid columns — only real
 *   CSS columns flow and break across pages. `column-span: all` lets
 *   a heading span the columns; `hyphens: auto` (needs `lang` on
 *   the html element) keeps narrow columns readable.
 * - Page breaks in flowing documents: `break-before: page` on an
 *   element that must start a new page (a chapter, an appendix). Add
 *   your own kept-together blocks (callouts, stat tiles, cards) to a
 *   `break-inside: avoid` rule, and keep each one shorter than a page.
 * - Extend `orphans: 3; widows: 3` to any custom text blocks you add
 *   (p and li are covered by default).
 * - Give long tables a <thead> — browsers repeat it on every printed
 *   page.
 * - No `position: fixed`/`sticky` and no viewport units in content:
 *   fixed elements stamp every printed page (running headers/footers go
 *   in the component's slots) and `100vh` mis-sizes at print.
 *
 * Author content as static HTML so the user can click-to-edit any text
 * directly. Do not set width/padding/background on the document body —
 * the component owns the sheet box.
 */
/* END USAGE */

(() => {
  const PAPER = {
    letter: ['8.5in', '11in'],
    a4: ['210mm', '297mm'],
    legal: ['8.5in', '14in']
  };
  const CSS_LENGTH = /^\d+(\.\d+)?(px|in|mm|cm|pt|pc)$/;
  // Unitless "0" is a valid CSS length and the natural way to write
  // margin="0"; normalise it to 0px so max()/calc() (which reject a bare
  // number) keep working.
  const safeLen = (v, fb) => {
    v = (v || '').trim();
    return v === '0' ? '0px' : CSS_LENGTH.test(v) ? v : fb;
  };
  // WebKit (Safari and every iOS browser shell) never repeats a table's
  // thead/tfoot on printed pages (WebKit bug 17205), so the spacer-borne
  // vertical margins of a FLOWING document reach only the first page
  // there. Engine check, not browser check: vendor is 'Apple Computer,
  // Inc.' exactly for WebKit and 'Google Inc.' for Blink.
  const WK_PRINT = /apple/i.test(navigator.vendor || '');
  // CSS length → px number (CSS absolute units are exact: 1in = 96px).
  // Returns NaN for anything safeLen would reject — callers gate on it.
  const PX_PER = {
    px: 1,
    in: 96,
    mm: 96 / 25.4,
    cm: 96 / 2.54,
    pt: 96 / 72,
    pc: 16
  };
  const toPx = v => {
    const m = /^(\d+(?:\.\d+)?)(px|in|mm|cm|pt|pc)$/.exec((v || '').trim());
    return m ? parseFloat(m[1]) * PX_PER[m[2]] : NaN;
  };
  const stylesheet = `
    :host {
      position: relative;
      display: block;
      /* When the viewport is narrower than the page, grow to wrap the
       * sheet (plus this padding) instead of staying viewport-width, so
       * the desk background and right margin reach the sheet's far edge
       * in the horizontal scroll. */
      min-width: max-content;
      min-height: 100vh;
      background: #f5f5f4;
      padding: 48px 24px;
      box-sizing: border-box;
      font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
      --doc-page-w: 8.5in;
      --doc-page-h: 11in;
      --doc-page-margin: 0.75in;
      --doc-hdr-h: 0px;
      --doc-ftr-h: 0px;
      --doc-hdr-pad: 0px;
      --doc-ftr-pad: 0px;
    }
    .sheet {
      width: var(--doc-page-w);
      margin: 0 auto;
      background: #fff;
      box-shadow: 0 2px 10px rgba(20, 20, 19, 0.12);
      border-radius: 7px;
      box-sizing: border-box;
      padding: var(--doc-page-margin);
    }
    .frame { width: 100%; border-collapse: collapse; }
    /* Scaled-fit mode (content-width/content-height): the inner .fit box
     * lays the content out at its authored fixed size and scales it onto
     * the printable area; .fit-box reserves the scaled footprint in flow
     * (transforms don't affect layout) and centers it. Without the mode,
     * both divs are unstyled block pass-throughs. */
    /* Explicit pagination: direct .page children are the pages. The sheet
     * becomes a transparent stack and each page carries the card look on
     * screen; at print each page is exactly one full-bleed sheet. The
     * ::slotted defaults are deliberately weak (document CSS wins), so
     * authored page styling can override any of this. */
    .sheet.paginated {
      background: transparent;
      box-shadow: none;
      border-radius: 0;
      padding: 0;
    }
    .paginated ::slotted(.page) {
      position: relative;
      display: block;
      width: 100%;
      aspect-ratio: var(--doc-page-ar);
      container-type: size;
      overflow: hidden;
      box-sizing: border-box;
      background: #fff;
      border-radius: 7px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
      print-color-adjust: exact;
      -webkit-print-color-adjust: exact;
      break-inside: avoid;
    }
    .paginated ::slotted(.page:not(:first-child)) { margin-top: 1rem; }
    @media print {
      .sheet.paginated { padding: 0; }
      /* The flowing-document vertical inset lives on the repeating
       * thead/tfoot spacers, not the sheet padding — they must go too,
       * or each full-sheet .page is pushed ~margin down and spills onto
       * a second sheet. Paginated pages are full-bleed by definition
       * (content owns its insets). */
      .sheet.paginated .hdr-space,
      .sheet.paginated .ftr-space { height: 0; }
      .paginated ::slotted(.page) {
        border-radius: 0 !important;
        box-shadow: none !important;
        margin: 0 !important;
        /* Physical page-box sizing, no viewport units: Safari resolves
         * 100vh against the window, not the page box, so a vh-sized card
         * paginates wrong there. --doc-page-w/h are the named size by
         * default and are overridden to the user's chosen paper by the
         * export path, so every card is exactly one sheet either way.
         * Width + height (same source values as @page size) rather than
         * width + aspect-ratio: the ratio is a 6-decimal rounding of the
         * same division, and a few millionths of overflow would spill a
         * blank sheet after every page. The screen-only aspect-ratio
         * (preview proportions) must not leak into print. cqh typography
         * tracks the same box.
         *
         * Every declaration is !important: per CSS Scoping, unimportant
         * shadow ::slotted rules LOSE to the document context, so a page
         * section's authored inline style would silently beat this print
         * geometry. A model-authored height:100% did exactly that — the
         * percentage resolves as auto in the all-auto print ancestry, the
         * base rule's size containment turns auto into ZERO, and
         * overflow:hidden then paints nothing: a blank PDF with perfect
         * page boxes. At print the component's geometry is the design's
         * whole contract, so it must win over any authored sizing. */
        aspect-ratio: auto !important;
        width: var(--doc-page-w) !important;
        height: var(--doc-page-h) !important;
        overflow: hidden !important;
      }
      .paginated ::slotted(.page:not(:first-child)) {
        break-before: page !important;
        margin-top: 0 !important;
      }
    }
    .fit-mode .fit-box {
      width: calc(var(--doc-fit-w) * var(--doc-fit-scale));
      height: calc(var(--doc-fit-h) * var(--doc-fit-scale));
      margin: 0 auto;
      break-inside: avoid;
    }
    /* Monolithic at print: Blink slices a transform-scaled child at
     * fragmentainer boundaries mapped in UNSCALED layout coordinates
     * (transforms are paint-time), so the .fit box (authored size, e.g.
     * 1400x990) gets cut at the page's free block space and spills onto
     * a second sheet even though its SCALED footprint fits the page by
     * construction. overflow:hidden makes .fit-box a scroll container —
     * monolithic under fragmentation (css-break-3) — so the scaled
     * content prints atomically on one sheet. No clipping for content
     * within the authored box: .fit-box is calc-sized to exactly the
     * scaled footprint. (Content that bleeds past content-width/height
     * is clipped at the footprint — fit mode's contract; it previously
     * painted beyond it at print.) Print-only, so the screen rendering
     * keeps visible overflow for editor affordances.
     * The export path injects the same rule into frozen copies
     * (print-eval.ts om-print-fit-contain). The .fit-mode scope is
     * load-bearing: .fit-box wraps slotted content in EVERY mode, and an
     * unscoped overflow:hidden would make whole flowing documents
     * monolithic (one truncated sheet). overflow:hidden, never clip —
     * clip is not a scroll container, so not monolithic. */
    @media print {
      .fit-mode .fit-box { overflow: hidden; }
    }
    .fit-mode .fit {
      width: var(--doc-fit-w);
      height: var(--doc-fit-h);
      transform: scale(var(--doc-fit-scale));
      transform-origin: top left;
    }
    .frame td, .frame th { padding: 0; text-align: left; font-weight: inherit; }
    .hdr-space { height: var(--doc-hdr-h); }
    .ftr-space { height: var(--doc-ftr-h); }
    ::slotted([slot="header"]),
    ::slotted([slot="footer"]) { display: block; box-sizing: border-box; }
    @media print {
      :host { background: none; padding: 0; min-width: 0; min-height: 0; }
      .sheet {
        width: auto; margin: 0; box-shadow: none; border-radius: 0;
        padding: 0 var(--doc-page-margin);
      }
      /* The thead/tfoot spacers repeat on every page, so they carry the
       * vertical page margin (which the sheet's own padding cannot, since
       * that padding is consumed once on the first/last page). The running
       * header/footer are fixed inside that band. */
      /* The 0.35in is breathing room between a running header/footer and
       * the body; without one the spacer is exactly the page margin, so a
       * margin="0" full-bleed document gets truly full-bleed pages. */
      .hdr-space { height: max(var(--doc-page-margin), calc(var(--doc-hdr-h) + var(--doc-hdr-pad))); }
      .ftr-space { height: max(var(--doc-page-margin), calc(var(--doc-ftr-h) + var(--doc-ftr-pad))); }
      /* WebKit flowing documents: @page carries the vertical margin (see
       * _syncPrintPageRule), so the spacers keep only whatever a running
       * header/footer needs BEYOND it — page 1 would otherwise double its
       * top inset. Paginated sheets already zero their spacers above. */
      .sheet.wk-print:not(.paginated) .hdr-space { height: max(0px, calc(max(var(--doc-page-margin), calc(var(--doc-hdr-h) + var(--doc-hdr-pad))) - var(--doc-page-margin))); }
      .sheet.wk-print:not(.paginated) .ftr-space { height: max(0px, calc(max(var(--doc-page-margin), calc(var(--doc-ftr-h) + var(--doc-ftr-pad))) - var(--doc-page-margin))); }
      ::slotted([slot="header"]) {
        position: fixed; top: 0; left: 0; right: 0; margin: 0;
        padding: calc(var(--doc-page-margin) * 0.45) var(--doc-page-margin) 0;
      }
      ::slotted([slot="footer"]) {
        position: fixed; bottom: 0; left: 0; right: 0; margin: 0;
        padding: 0 var(--doc-page-margin) calc(var(--doc-page-margin) * 0.45);
      }
    }
  `;
  class DocPage extends HTMLElement {
    static get observedAttributes() {
      return ['size', 'width', 'height', 'margin', 'orientation', 'content-width', 'content-height'];
    }
    constructor() {
      super();
      this._root = this.attachShadow({
        mode: 'open'
      });
      this._mo = typeof MutationObserver === 'function' ? new MutationObserver(() => this._scheduleMeasure()) : null;
    }

    /** The named paper's [w, h], swapped when orientation="landscape".
     *  Only the named size swaps — explicit width/height are exact values
     *  the author already oriented. */
    _paperSize() {
      const named = PAPER[(this.getAttribute('size') || '').toLowerCase()] || PAPER.letter;
      const landscape = (this.getAttribute('orientation') || '').trim().toLowerCase() === 'landscape';
      return landscape ? [named[1], named[0]] : named;
    }
    get pageWidth() {
      return safeLen(this.getAttribute('width'), this._paperSize()[0]);
    }
    get pageHeight() {
      return safeLen(this.getAttribute('height'), this._paperSize()[1]);
    }
    get pageMargin() {
      return safeLen(this.getAttribute('margin'), '0.75in');
    }

    /** Scaled-fit mode's content box [w, h] as CSS lengths, or null when
     *  the mode is off (either attribute missing/invalid/zero — a partial
     *  declaration falls back to normal flow rather than guessing). */
    _contentFit() {
      const w = safeLen(this.getAttribute('content-width'), null);
      const h = safeLen(this.getAttribute('content-height'), null);
      if (!w || !h) return null;
      const wPx = toPx(w),
        hPx = toPx(h);
      return wPx > 0 && hPx > 0 ? [w, h, wPx, hPx] : null;
    }
    connectedCallback() {
      if (!this._sheet) this._render();
      this._syncSize();
      this._syncPrintPageRule();
      this._ensureTextWrapDefaults();
      this._ensureOwnsPrintMeta();
      this._syncFixedSizeMeta();
      this._syncPrintSizingMeta();
      if (this._mo) this._mo.observe(this, {
        subtree: true,
        childList: true,
        characterData: true,
        attributes: true
      });
      this._onResize = () => this._scheduleMeasure();
      window.addEventListener('resize', this._onResize);
      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(() => this._scheduleMeasure());
      }
      this._scheduleMeasure();
    }
    disconnectedCallback() {
      window.removeEventListener('resize', this._onResize);
      if (this._mo) this._mo.disconnect();
      if (this._raf) {
        cancelAnimationFrame(this._raf);
        this._raf = null;
      }
      // Drop the head rules when the last doc-page leaves, so a deleted
      // document's @page geometry and text-wrap defaults can't apply to
      // whatever replaces it.
      const survivor = document.querySelector('doc-page');
      if (!survivor) {
        ['doc-page-print', 'doc-page-text-wrap', 'doc-page-owns-print', 'doc-page-fixed-size', 'doc-page-print-sizing'].forEach(id => {
          const tag = document.getElementById(id);
          if (tag) tag.remove();
        });
        // A live deck-stage deferred its own print-sizing meta to ours —
        // hand the page-global meta over so the deck isn't left unmarked.
        const deck = document.querySelector('deck-stage');
        if (deck && typeof deck._ensurePrintSizingMeta === 'function') {
          deck._ensurePrintSizingMeta();
        }
      } else {
        // A departed owner hands each page-global meta to whatever
        // doc-page remains (or it's removed).
        if (typeof survivor._syncFixedSizeMeta === 'function') {
          survivor._syncFixedSizeMeta();
        }
        if (typeof survivor._syncPrintSizingMeta === 'function') {
          survivor._syncPrintSizingMeta();
        }
      }
    }
    attributeChangedCallback() {
      if (!this._sheet) return;
      this._syncSize();
      this._syncPrintPageRule();
      this._syncFixedSizeMeta();
      this._syncPrintSizingMeta();
      this._scheduleMeasure();
    }
    _render() {
      this._root.innerHTML = `
        <style>${stylesheet}</style>
        <style id="vars"></style>
        <div class="sheet" data-screen-label="Document">
          <table class="frame" role="presentation">
            <thead><tr><th><div class="hdr-space"><slot name="header"></slot></div></th></tr></thead>
            <tbody><tr><td class="body"><div class="fit-box"><div class="fit"><slot></slot></div></div></td></tr></tbody>
            <tfoot><tr><td><div class="ftr-space"><slot name="footer"></slot></div></td></tr></tfoot>
          </table>
        </div>`;
      this._sheet = this._root.querySelector('.sheet');
      this._vars = this._root.getElementById('vars');
    }

    /** Runtime sizing lives in a shadow <style> :host rule, never on the
     *  light-DOM host element, so serialize-persist can't write it back. */
    _syncSize(hdrH, ftrH) {
      // Scaled-fit mode: content at its authored size, scaled onto the
      // printable area (page minus margins on both axes). The factor is a
      // plain number var so calc(length * number) stays valid; 4 decimals
      // keeps the shadow style stable across re-measures. Upscaling is
      // allowed — print transforms are vector, so text and CSS stay crisp
      // (raster images soften, which the catalog bullet warns about).
      const fit = this._contentFit();
      let fitVars = '';
      if (fit) {
        const marginPx = toPx(this.pageMargin) || 0;
        const availW = toPx(this.pageWidth) - 2 * marginPx;
        const availH = toPx(this.pageHeight) - 2 * marginPx;
        const scale = Math.min(availW / fit[2], availH / fit[3]);
        if (scale > 0 && Number.isFinite(scale)) {
          fitVars = '--doc-fit-w:' + fit[0] + ';' + '--doc-fit-h:' + fit[1] + ';' + '--doc-fit-scale:' + scale.toFixed(4) + ';';
        }
      }
      this._sheet.classList.toggle('fit-mode', !!fitVars);
      // Numeric w/h ratio for the paginated page cards' aspect-ratio —
      // aspect-ratio takes a number, not a length ratio, so compute it
      // here (CSS length division isn't portable). 6 decimals keeps the
      // shadow style stable across re-syncs.
      const arW = toPx(this.pageWidth);
      const arH = toPx(this.pageHeight);
      const ar = arW > 0 && arH > 0 ? (arW / arH).toFixed(6) : '0.772727';
      this._vars.textContent = ':host{' + fitVars + '--doc-page-ar:' + ar + ';' + '--doc-page-w:' + this.pageWidth + ';' + '--doc-page-h:' + this.pageHeight + ';' + '--doc-page-margin:' + this.pageMargin + ';' + '--doc-hdr-h:' + (hdrH || 0) + 'px;' + '--doc-ftr-h:' + (ftrH || 0) + 'px;' + '--doc-hdr-pad:' + (hdrH ? '0.35in' : '0px') + ';' + '--doc-ftr-pad:' + (ftrH ? '0.35in' : '0px') + '}';
    }

    /** @page is a no-op inside shadow DOM, so the rule lives in <head>.
     *  Re-appended on every sync so it stays last in source order — the
     *  @page cascade is source-order per descriptor, so this rule wins
     *  over any other @page rule in the document.
     *
     *  The @page SIZE is pinned where the page box IS part of the design:
     *  explicit-fixed-size mode (width + height authored), scaled-fit
     *  mode (the named sheet the fit targets), and explicit pagination
     *  (the named size the cards share — so card and sheet agree on
     *  every print path, and the export path's chosen paper overrides
     *  BOTH with one later rule). For FLOWING documents no paper size is
     *  emitted at all — the true size comes from the user's preference,
     *  injected by the export path or chosen in the print dialog — so a
     *  flowing document never fights the paper it lands on.
     *  margin: 0 is emitted in every mode: it leaves Chrome no margin box
     *  to draw its date/URL/page-count header in, and the visual margin
     *  lives on the sheet's own padding. */
    _syncPrintPageRule() {
      const id = 'doc-page-print';
      let tag = document.getElementById(id);
      if (!tag) {
        tag = document.createElement('style');
        tag.id = id;
      }
      document.head.appendChild(tag);
      // Three print-geometry regimes:
      // - true-size: the page IS the design — pin its exact size.
      // - scaled-fit (content-width/height): the fit factor is computed
      //   against the NAMED paper's printable area, so that paper must
      //   stay pinned or the scaled content overflows a smaller sheet
      //   (the export path re-fits and re-pins at print time on top).
      // - default modes: no paper size — but landscape still needs the
      //   paper-agnostic 'size: landscape' keyword, because the size
      //   descriptor is what carries orientation; without it a landscape
      //   document prints portrait whenever nothing injects a size.
      const landscape = (this.getAttribute('orientation') || '').trim().toLowerCase() === 'landscape';
      // Explicit pagination pins the page box to the SAME values that
      // size the cards (the named size by default, the export path's
      // chosen paper when its later rule overrides both) — card and
      // sheet agree on every print path, and a mismatched real paper
      // shrinks-to-fit in the dialog instead of clipping a Letter card
      // on A4. Declared before the paginated read below so both derive
      // from one check.
      const paginatedNow = this.querySelector(':scope > .page') !== null;
      const sizeDescriptor = this._trueSizePx() ? 'size: ' + this.pageWidth + ' ' + this.pageHeight + '; ' : this._contentFit() ? 'size: ' + this.pageWidth + ' ' + this.pageHeight + '; ' : paginatedNow ? 'size: ' + this.pageWidth + ' ' + this.pageHeight + '; ' : landscape ? 'size: landscape; ' : '';
      // WebKit never repeats the thead/tfoot spacers that carry a flowing
      // document's vertical page margins (see WK_PRINT above), so pages
      // after the first print edge-to-edge there. Carry the VERTICAL
      // margins on @page for WebKit instead, and the shadow print CSS
      // trims the first-page spacers by the same amount (.sheet.wk-print
      // rules). Horizontal inset stays on the sheet's own padding in
      // every engine. Blink keeps margin: 0 (a nonzero margin there
      // re-opens the box Chrome draws its header furniture in). One cost,
      // learned in testing: Safari's own date/URL headers are a USER
      // dialog setting ("Print headers and footers") that renders in the
      // margin area when room exists — margin: 0 only suppressed it by
      // leaving no room, and no CSS controls it. The export dialog's
      // Safari guide teaches turning the setting off for flowing
      // documents. Explicitly paginated and fixed-size documents keep
      // margin: 0 everywhere: their pages ARE the sheet.
      const wkFlowing = WK_PRINT && !paginatedNow && !this._trueSizePx() && !this._contentFit();
      const marginDescriptor = wkFlowing ? 'margin: ' + this.pageMargin + ' 0; ' : 'margin: 0; ';
      // Shadow-internal marker (never serialized), kept in lockstep with
      // the @page decision above: the print CSS trims the first-page
      // spacers ONLY while @page actually carries the margins — a
      // true-size or scaled-fit sheet keeps margin: 0 and must keep its
      // spacers too. Re-synced here so attribute changes and pagination
      // flips move both together.
      if (this._sheet) this._sheet.classList.toggle('wk-print', wkFlowing);
      tag.textContent = '@page { ' + sizeDescriptor + marginDescriptor + '} ' + '@media print { html, body { margin: 0 !important; padding: 0 !important; background: none !important; height: auto !important; overflow: visible !important; } ' + 'h1,h2,h3,h4,h5,h6 { break-after: avoid; } ' + 'figure,pre,blockquote,img,svg,tr { break-inside: avoid; } ' + 'p,li { orphans: 3; widows: 3; } ' + '* { -webkit-print-color-adjust: exact; print-color-adjust: exact; ' + 'backdrop-filter: none !important; -webkit-backdrop-filter: none !important; } ' + '*, *::before, *::after { animation-delay: -99s !important; animation-duration: .001s !important; ' + 'animation-iteration-count: 1 !important; animation-fill-mode: both !important; ' + 'animation-play-state: running !important; transition-duration: 0s !important; } }';
    }

    /** Typographic defaults for document text: balance headings, avoid
     *  widowed/orphaned words in body copy (browsers without text-wrap
     *  support drop the declarations). Zero-specificity via :where() so
     *  any text-wrap authored on those elements wins; document-level so the
     *  rules reach the slotted (light DOM) content — shadow styles can't.
     *  data-omelette-injected marks the tag for the host editor to strip
     *  at serialize, so it is never written back as authored source. */
    _ensureTextWrapDefaults() {
      if (document.getElementById('doc-page-text-wrap')) return;
      const tag = document.createElement('style');
      tag.id = 'doc-page-text-wrap';
      tag.setAttribute('data-omelette-injected', '');
      tag.textContent = ':where(h1,h2,h3,h4,h5,h6){text-wrap:balance}' + ':where(p,li,blockquote,figcaption){text-wrap:pretty}';
      document.head.appendChild(tag);
    }

    /** Declares that this document owns its print CSS. The instant-PDF
     *  export checks for the meta by NAME PRESENCE alone (content is
     *  ignored) and skips its automatic print-CSS injections, so the
     *  component's @page geometry is never overridden by a heuristic.
     *  data-omelette-injected keeps it out of serialized source. */
    _ensureOwnsPrintMeta() {
      if (document.getElementById('doc-page-owns-print')) return;
      const tag = document.createElement('meta');
      tag.id = 'doc-page-owns-print';
      tag.name = 'omelette-owns-print';
      tag.content = 'true';
      tag.setAttribute('data-omelette-injected', '');
      document.head.appendChild(tag);
    }

    /** This page's valid true-size page box (explicit width AND height)
     *  as [w, h] px ints, or null when the mode is off. */
    _trueSizePx() {
      if (!safeLen(this.getAttribute('width'), null) || !safeLen(this.getAttribute('height'), null)) return null;
      const w = Math.round(toPx(this.pageWidth));
      const h = Math.round(toPx(this.pageHeight));
      return w > 0 && h > 0 ? [w, h] : null;
    }

    /** True-size pages (explicit width AND height) also declare the page
     *  box as the preview size: the in-app preview reads
     *  meta[name="omelette-fixed-size"] (content "W,H" in px ints) and
     *  scales the sheet into view — without it an 18in poster previews at
     *  true size with scrollbars. Never overrides an author-set meta
     *  (only the component's own id is managed). The meta is page-global
     *  while doc-page instances are not, so every sync recomputes the
     *  page-wide owner — the first connected true-size doc-page — and a
     *  non-true-size sibling's sync can never delete the owner's meta.
     *  Removed when no true-size page remains (the owner's disconnect
     *  re-syncs via any survivor) or when an author-set meta exists. */
    _syncFixedSizeMeta() {
      const id = 'doc-page-fixed-size';
      const own = document.getElementById(id);
      const authored = document.querySelector('meta[name="omelette-fixed-size"]:not([data-omelette-injected])');
      // The page-wide owner, not this instance: an upgraded true-size page
      // anywhere in the document keeps the meta alive and sized.
      let box = null;
      for (const el of document.querySelectorAll('doc-page')) {
        box = typeof el._trueSizePx === 'function' ? el._trueSizePx() : null;
        if (box) break;
      }
      if (!box || authored) {
        if (own) own.remove();
        return;
      }
      const tag = own || document.createElement('meta');
      tag.id = id;
      tag.name = 'omelette-fixed-size';
      tag.content = box[0] + ',' + box[1];
      tag.setAttribute('data-omelette-injected', '');
      if (!own) document.head.appendChild(tag);
    }

    /** This page's print-sizing mode: 'fixed' when an explicit width AND
     *  height are authored (the page is the design's own size), else the
     *  default paper in the authored orientation. */
    _printSizingMode() {
      if (this._trueSizePx()) return 'fixed';
      const landscape = (this.getAttribute('orientation') || '').trim().toLowerCase() === 'landscape';
      return landscape ? 'default-landscape' : 'default-portrait';
    }

    /** Announces the print-sizing mode to the host app:
     *  meta[name="omelette-print-sizing"] with content 'default-portrait',
     *  'default-landscape', or 'fixed' (fixed pages also carry the
     *  omelette-fixed-size meta with the page box in px). The export path
     *  probes it to decide what true paper size to inject at print time —
     *  in the default modes the component emits no paper size of its own.
     *  Same page-global ownership rules as the fixed-size meta above:
     *  first connected doc-page owns it, an authored meta is never
     *  overridden, removed when no doc-page remains. */
    _syncPrintSizingMeta() {
      const id = 'doc-page-print-sizing';
      const own = document.getElementById(id);
      const authored = document.querySelector('meta[name="omelette-print-sizing"]:not([data-omelette-injected])');
      // A fixed page wins outright (mirroring the fixed-size loop above,
      // so the two metas can never contradict each other in a mixed
      // multi-page document); otherwise the first page's mode holds.
      let mode = null;
      for (const el of document.querySelectorAll('doc-page')) {
        if (typeof el._printSizingMode !== 'function') continue;
        const m = el._printSizingMode();
        if (m === 'fixed') {
          mode = m;
          break;
        }
        if (mode === null) mode = m;
      }
      if (!mode || authored) {
        if (own) own.remove();
        return;
      }
      // A deck-stage that connected first injected its own meta and
      // defers to any existing one — take it over, or the document ends
      // up with two conflicting injected metas (a doc-page page is the
      // document; the deck re-ensures its meta if every doc-page leaves).
      const deckMeta = document.getElementById('deck-stage-print-sizing');
      if (deckMeta) deckMeta.remove();
      const tag = own || document.createElement('meta');
      tag.id = id;
      tag.name = 'omelette-print-sizing';
      tag.content = mode;
      tag.setAttribute('data-omelette-injected', '');
      if (!own) document.head.appendChild(tag);
    }
    _scheduleMeasure() {
      if (this._raf) return;
      this._raf = requestAnimationFrame(() => {
        this._raf = null;
        this._measure();
      });
    }

    /** Slot heights feed the print spacers (--doc-hdr-h / --doc-ftr-h), so
     *  they re-measure on content mutation, resize, and font load. The
     *  same pass detects explicit pagination (direct .page children) and
     *  toggles the sheet between the flowing-document card and the
     *  page-per-card stack — content edits can add or remove pages at any
     *  time, so this tracks the same mutations the measurement does. */
    _measure() {
      const hdr = this.querySelector(':scope > [slot="header"]');
      const ftr = this.querySelector(':scope > [slot="footer"]');
      const wasPaginated = this._sheet.classList.contains('paginated');
      this._sheet.classList.toggle('paginated', this.querySelector(':scope > .page') !== null);
      // The WebKit @page margin is flowing-only, so a pagination flip
      // must re-emit the rule (content edits can add or remove .page
      // sections at any time).
      if (this._sheet.classList.contains('paginated') !== wasPaginated) {
        this._syncPrintPageRule();
      }
      this._syncSize(hdr ? hdr.offsetHeight : 0, ftr ? ftr.offsetHeight : 0);
    }
  }
  if (!customElements.get('doc-page')) {
    customElements.define('doc-page', DocPage);
  }
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/docs/doc-page.js", error: String((e && e.message) || e) }); }

__ds_ns.Callout = __ds_scope.Callout;

__ds_ns.CodeBlock = __ds_scope.CodeBlock;

__ds_ns.DataTable = __ds_scope.DataTable;

__ds_ns.DecisionList = __ds_scope.DecisionList;

__ds_ns.Figure = __ds_scope.Figure;

__ds_ns.DomainGlyph = __ds_scope.DomainGlyph;

__ds_ns.DomainTag = __ds_scope.DomainTag;

__ds_ns.EvidenceMeter = __ds_scope.EvidenceMeter;

__ds_ns.StatusGlyph = __ds_scope.StatusGlyph;

__ds_ns.StatusMark = __ds_scope.StatusMark;

__ds_ns.DocHeader = __ds_scope.DocHeader;

__ds_ns.Lineage = __ds_scope.Lineage;

__ds_ns.SectionHeading = __ds_scope.SectionHeading;

__ds_ns.SourceList = __ds_scope.SourceList;

__ds_ns.Breadcrumb = __ds_scope.Breadcrumb;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.DocNav = __ds_scope.DocNav;

__ds_ns.SearchField = __ds_scope.SearchField;

__ds_ns.Toc = __ds_scope.Toc;

})();
