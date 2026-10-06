---
version: alpha
name: Symbiont
description: Documentation identity for Symbiont — a scientific and technical knowledge system for an embodied artificial-life research project. Research publication + technical specification + living system.
colors:
  primary: "#18202b"
  on-primary: "#fbfaf6"
  background: "#fbfaf6"
  surface: "#fbfaf6"
  surface-aside: "#f5f3ec"
  surface-code: "#eeebe2"
  surface-highlight: "#e5e1d5"
  on-surface: "#18202b"
  on-surface-secondary: "#3a424d"
  on-surface-meta: "#5c636c"
  on-surface-faint: "#878c92"
  rule-hair: "#e4e0d4"
  rule: "#d2ccbc"
  rule-strong: "#aba491"
  rule-ink: "#18202b"
  night: "#0e1317"
  night-1: "#151c21"
  night-2: "#1d262c"
  night-rule: "#2c373e"
  on-night: "#e7ece9"
  on-night-secondary: "#a7b5b0"
  domain-symbiont: "oklch(0.52 0.11 152)"
  domain-embodiment: "oklch(0.56 0.10 62)"
  domain-modality: "oklch(0.52 0.12 252)"
  domain-environment: "oklch(0.53 0.06 200)"
  domain-lab: "oklch(0.50 0.10 300)"
  signal-warn: "oklch(0.54 0.17 32)"
  signal-warn-ink: "oklch(0.45 0.15 32)"
  signal-warn-tint: "oklch(0.955 0.025 40)"
  link: "oklch(0.41 0.11 252)"
  brand-leaf: "#36a56d"
  brand-cell: "#1f6fd1"
typography:
  title:
    fontFamily: Source Serif 4
    fontSize: 2.5rem
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: -0.012em
  h2:
    fontFamily: Source Serif 4
    fontSize: 1.75rem
    fontWeight: 400
    lineHeight: 1.25
  h3:
    fontFamily: Schibsted Grotesk
    fontSize: 1.25rem
    fontWeight: 600
    lineHeight: 1.25
  lede:
    fontFamily: Source Serif 4
    fontSize: 1.25rem
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: Schibsted Grotesk
    fontSize: 1.0625rem
    fontWeight: 400
    lineHeight: 1.62
  small:
    fontFamily: Schibsted Grotesk
    fontSize: 0.9375rem
    fontWeight: 400
    lineHeight: 1.5
  meta:
    fontFamily: Schibsted Grotesk
    fontSize: 0.8125rem
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: Martian Mono
    fontSize: 0.6875rem
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: 0.09em
  code:
    fontFamily: Martian Mono
    fontSize: 0.8125rem
    fontWeight: 400
    lineHeight: 1.7
rounded:
  none: 0px
  sm: 2px
  md: 3px
spacing:
  "1": 4px
  "2": 8px
  "3": 12px
  "4": 16px
  "5": 24px
  "6": 32px
  "7": 48px
  "8": 64px
  "9": 96px
  gutter: 128px
  measure: 68ch
  nav: 272px
  toc: 220px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    height: 34px
    padding: 0 16px
    typography: "{typography.meta}"
  button-primary-hover:
    backgroundColor: "{colors.on-surface-secondary}"
  button-secondary:
    backgroundColor: transparent
    textColor: "{colors.on-surface}"
    borderColor: "{colors.rule-strong}"
    rounded: "{rounded.sm}"
    height: 34px
    padding: 0 16px
    typography: "{typography.meta}"
  button-secondary-hover:
    backgroundColor: "{colors.surface-aside}"
    borderColor: "{colors.rule-ink}"
  button-disabled:
    backgroundColor: "{colors.surface-aside}"
    textColor: "{colors.on-surface-meta}"
    borderColor: "{colors.rule}"
    opacity: 1
  search-field:
    backgroundColor: "{colors.surface}"
    borderColor: "{colors.rule}"
    rounded: "{rounded.sm}"
    height: 34px
  code-inline:
    backgroundColor: "{colors.surface-code}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.sm}"
  code-block:
    backgroundColor: "{colors.surface-aside}"
    textColor: "{colors.on-surface}"
    typography: "{typography.code}"
  code-block-night:
    backgroundColor: "{colors.night}"
    textColor: "{colors.on-night}"
  callout-invariant:
    borderTop: 2px solid {colors.rule-ink}
    borderBottom: 1px solid {colors.rule-ink}
  callout-hypothesis:
    borderTop: 1px dashed {colors.rule-strong}
  callout-implementation:
    backgroundColor: "{colors.surface-aside}"
  callout-warning:
    backgroundColor: "{colors.signal-warn-tint}"
    borderTop: 2px solid {colors.signal-warn}
    textColor: "{colors.signal-warn-ink}"
  callout-superseded:
    background: repeating-linear-gradient(135deg, {colors.surface-aside} 0 6px, {colors.surface} 6px 12px)
---

# Symbiont — DESIGN.md

## Overview

Symbiont is an experimental artificial-life and cognitive-architecture project: a persistent, embodied, self-developing digital organism and the laboratory apparatus used to study it. Its documentation is a body of scientific knowledge — chapters, specifications, ADRs, experiments, evidence, glossaries — that may grow to hundreds of documents.

The interface should read like a **research publication crossed with a technical specification**, calm enough for very long reading and dense when the material demands it. It is never a dashboard and never decorative sci-fi. Every visual element carries meaning: colour marks domain ownership or integrity failure, rule style marks information type, glyph shape marks epistemic status.

Source repository: <https://github.com/alessbarb/symbiont-lab>

## Colors

- **Paper grounds.** Pages sit on warm near-white `#fbfaf6`, never pure white. `surface-aside` (`#f5f3ec`) holds code and implementation notes; `surface-code` (`#eeebe2`) holds inline code.
- **Ink.** Text comes from the wordmark's blue-black `#18202b`. Secondary `#3a424d`, meta `#5c636c` (≥5.9:1 on paper). `on-surface-faint` is decorative only, never text.
- **Night.** `#0e1317` and its steps are reserved for instrument content: runtime figures, telemetry, terminal output, diagrams of live systems. Never for page chrome.
- **Domain hues.** Five desaturated oklch hues mark which package owns a document or entity. Each has `-ink` (text), `-tint` (ground) and `-rule` (line) variants in `tokens/colors.css`.
  - symbiont — green, the organism
  - embodiment — ochre, the body coupling
  - modality — blue, signal channels
  - environment — slate-teal, world and ground truth
  - lab — violet, composition and observation
- **Signal.** Vermilion `signal-warn` is the only alarm colour, reserved for integrity failures, warnings and limitations. Negative scientific results are **not** red; they are ink.
- **Brand pair.** `brand-leaf` and `brand-cell` are the logo's extremes, for the mark and covers only — never UI chrome.

## Typography

Three faces, each with one job:

- **Source Serif 4** — structure: document titles (40px/1.1, opsz 60, −0.012em), section heads (28px), abstracts and ledes (20px), figure and table captions, principles.
- **Schibsted Grotesk** — reading: body 17px/1.62 at a 68ch measure, subsection heads (20px semibold), metadata (13px).
- **Martian Mono** at `wdth 87.5` — data: code (13px/1.7), identifiers, file paths, gutter labels (11px uppercase, 0.09em tracking), telemetry.

Sentence case for every title and heading. Identifiers keep their code casing (`EmbodimentContract`, `rec.107`). Status words appear as uppercase mono labels (`PREREGISTERED`, `FROZEN`). Use `text-wrap: pretty` for prose and `balance` for titles.

## Layout

- **Editorial gutter.** A 128px left label column holds § numbers and block-type labels (ABSTRACT, INVARIANT, HYPOTHESIS). Content sits 24px to the right in a 68ch reading column. Prose is indented 152px so it aligns with block content.
- **Docs shell.** 272px sticky navigation · fluid reading column · 220px sticky "On this page". The TOC drops below 1180px and the navigation below 820px.
- **Rhythm.** 4px base. Sections break with 64px plus a rule above; subsections with 32px. Blocks are separated by 24px.
- **Fluid.** Use `minmax(0,1fr)` tracks and flex-wrap gutters so the label column stacks above content on narrow screens.

## Elevation & Depth

Documents are flat. No shadows, no blur, no transparency, no gradients. Depth comes from **rules**:

- hairline `#e4e0d4` — row separators
- rule `#d2ccbc` — section breaks, code-block edges
- ink rule `#18202b` — table heads, figure tops, header baselines
- 2px ink — invariants and decisions

`--shadow-pop` exists only for transient popovers. The single pattern in the system is the 135° hatch, which means *superseded*.

## Shapes

Corners are square by default. 2px radius only for inline code, inputs, buttons and chips; 3px max. No pills, no rounded cards.

Two glyph families carry meaning and survive greyscale and print:

- **Domain glyphs:** symbiont ● circle · embodiment ■ square · modality ◆ diamond · environment ▬ ground · lab ○ ring.
- **Status glyphs:** filled circle = supported · half = observed/partial/discovery · ring = preregistered/unresolved · dashed ring = intended/planned/proposed · filled with bar = negative · ring with bar = inconclusive · struck = superseded/historical · filled square = implemented/accepted · half square = tested/validated · square with core = frozen · vermilion filled = integrity failure.

## Components

All in `components/`, React, styled only through the CSS custom properties.

- **Core:** `DomainTag` / `DomainGlyph` (ownership), `StatusMark` / `StatusGlyph` (repository status vocabulary), `EvidenceMeter` (four bars, 0 none → 4 preregistered & replicated, always with scope).
- **Blocks:** `Callout` with ten kinds — each encoded by structure, not colour:
  - note: thin rule
  - principle: ink rule, serif
  - invariant: 2px ink top + 1px ink bottom, medium weight
  - hypothesis: dashed rules, serif italic
  - evidence: ink rule + EvidenceMeter + status
  - implementation: aside ground + source path
  - limitation: vermilion rule
  - warning: vermilion 2px + tint
  - decision: 2px ink
  - superseded: hatch + "Superseded by"

  Also `CodeBlock` (paper or night), `Figure` (numbered, serif caption, source path), `DataTable` (book style: ink rules top and bottom, hairline rows, no fills), `DecisionList` (D01, D02… with per-decision status).
- **Document:** `DocHeader` (type · id · status line, domains, serif title, gutter abstract, metadata grid), `SectionHeading` (§ number in the gutter), `SourceList` ("Principal sources"), `Lineage` (vertical descent line of supersessions, newest first).
- **Navigation:** `DocNav` (sections, numbered items, trailing status glyphs, ink hairline for the active item), `Toc`, `Breadcrumb` (mono repository path), `SearchField`, `Button` (primary ink fill, secondary hairline, quiet underline).

Interaction is quiet: 120–220ms `cubic-bezier(.2,.6,.2,1)` on colour only. Links go from blue-ink to ink and the underline turns solid. Focus is a 2px modality-blue outline at 2px offset. No press-shrink, no bounce, no pulse. `prefers-reduced-motion` is honoured.

## Do's and Don'ts

**Do**

- Make the scope of every claim visible: runtime, seeds, preregistered conditions.
- Give negative results the same typographic weight as positive ones.
- Keep superseded and historical material fully legible (≥4.5:1). Signal its state with strike, hatch and a "Superseded by" link.
- Tag every document with its domain(s) and status.
- Use night surfaces only for instrument content.
- Write impersonal, third-person scientific prose in sentence case, with no emoji.

**Don't**

- Use colour ornamentally: no domain hue outside ownership, no vermilion outside integrity issues.
- Use cards, shadows, glassmorphism, gradients, glows or rounded SaaS panels.
- Turn documents into dashboards with KPI tiles.
- Write "proves", "guarantees", "always" or "never" unless the claim is established by contract.
- Recolour, redraw or place the logo PNGs on dark grounds; they have opaque white backgrounds.
- Add icons where a typed label does the job. If one is unavoidable, use Lucide at 1.5px stroke, 16px, ink-3.

## Constraints

The `Don't` rules above are inviolable. The YAML front matter is the sole source of color, typography, radius, spacing, and component tokens; do not add or substitute tokens ad hoc. Follow only the listed typographic scale and use spacing in multiples of its 4px base. An unresolved design detail is a specification gap: do not guess—record the gap and obtain a design decision before implementation.

The specification does not define disabled-state appearance for interactive controls. Before implementing an interactive component that needs a disabled state, obtain and record a design decision rather than inventing a visual treatment. Preserve accessible hover and focus behavior, including the specified modality-blue focus outline and reduced-motion preference.
