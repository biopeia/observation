# Symbiont Design System

A documentation identity for **Symbiont** — an experimental artificial-life and cognitive-architecture research project: a persistent, embodied, self-developing digital organism and the laboratory apparatus used to study it.

The system is built for a body of scientific and technical knowledge — specifications, ADRs, experiments, evidence, glossaries, implementation notes — not for a dashboard. Think research publication + technical specification + living system.

## Sources

- GitHub: **https://github.com/alessbarb/symbiont-lab** (branch `main`). Explore it to ground any new design in real content:
  - `README.md` — project state, five-domain architecture, scientific method
  - `symbiont/docs/` — canonical scientific corpus (chapters 00–14, anatomy, reference, atlas)
  - `docs/adr/` — ~70 architecture decision records
  - `docs/glossary.md`, `symbiont/docs/reference/evidence-status.md`, `lab/research/README.md` — the status vocabulary this system encodes
  - `lab/src/lab/workbench/web/` — the existing Lab Workbench (dark, glassmorphic). **Not** used as visual reference for docs; the brief explicitly moves away from it.
  - `assets/logo/` — the four logo PNGs copied into `assets/logo/`.

## Product context

The repository is five peer domains in one workspace, and the visual system makes that boundary visible:

| Domain | Responsibility | Glyph |
| --- | --- | --- |
| `symbiont` | the organism / research subject | ● circle, green |
| `embodiment` | couplings between organism and a concrete body | ■ square, ochre |
| `modality` | signal channels; no cognitive meaning | ◆ diamond, blue |
| `environment` | external laws, dynamics, ground truth | ▬ ground, slate-teal |
| `lab` | composition, experiments, observation | ○ ring, violet |

Core invariant: `World != Body != Embodiment != Symbiont`. Evaluator knowledge never flows back into the subject.

Surfaces: (1) the documentation corpus — the focus of this system, UI kit in `ui_kits/docs/`; (2) the Lab Workbench (local web app) — not recreated here.

---

## CONTENT FUNDAMENTALS

- **Voice:** impersonal, third-person scientific prose. No "we", rarely "you". The organism is "Symbiont" or "the organism"; the apparatus is "Lab". Example: *"A body is not an organism and an embodiment is not a body."*
- **Scope is always visible.** Claims carry their conditions: *"In the current Physics3D runtime, a fresh body is assigned a distinct physical body identity…"* Avoid "proves", "guarantees", "always", "never" unless established by contract.
- **Negative results are first-class.** *"H1 not supported"*, *"These results define the next causal research problem; they are not defects to edit away."* Never soften or hide them visually.
- **What it is not** is stated as plainly as what it is: *"The project does not claim that Symbiont is biologically alive, conscious, sentient or generally intelligent."*
- **Casing:** sentence case for titles and headings (*"World, body and embodiment"*). Identifiers keep code casing (`EmbodimentContract`, `rec.107`). Status words are UPPERCASE in registries (`PREREGISTERED`, `FROZEN`) — rendered as uppercase mono labels.
- **British/Oxford-leaning spelling** appears (*organisation, generalisation, behaviour*) alongside US forms; keep whatever the source uses.
- **Short declarative sentences**, numbered decisions, explicit sources lists ("Principal sources"). Arrows `→` for causal chains; `!=` for boundaries.
- **No emoji. No marketing tone.** No exclamation marks.

## VISUAL FOUNDATIONS

- **Grounds:** warm paper `--paper-0 #fbfaf6` for pages; `--paper-1` for asides/code; never pure white. Dark **night** surfaces (`--night-0 #0e1317`) are reserved for instrument content: runtime figures, telemetry, terminal output.
- **Colour is semantic only.** Five domain hues (oklch, L≈0.5, low chroma) mark ownership. One signal colour (vermilion `--signal-warn`) marks integrity failures and limitations. Everything else — including evidence status — is ink. Logo colours (`--brand-leaf`, `--brand-cell`) are for the mark only.
- **Type:** Source Serif 4 for structure (titles, section heads, abstracts, captions, principles); Schibsted Grotesk for reading (17px/1.62, 68ch); Martian Mono (wdth 87.5) for code, ids, paths, gutter labels and telemetry.
- **Layout:** editorial gutter. A 128px left label column holds §-numbers and block types ("INVARIANT", "ABSTRACT"); content sits in a 68ch column. Docs shell = 272px nav · reading column · 220px TOC; collapses at 1180/820px.
- **Rules, not boxes.** Hairlines (`--rule-1`), rules (`--rule-2`), ink rules (`--rule-ink`). Rule weight/style encodes type: 2px ink = invariant/decision; dashed = hypothesis; hatched ground = superseded; vermilion = warning.
- **Cards:** essentially none. No shadows in documents; `--shadow-pop` only for transient popovers. Radii 0 by default, 2px for inline code/inputs/buttons. No rounded SaaS panels, no glassmorphism, no gradients (the only pattern is the 135° hatch for superseded material — it means something).
- **Shape carries meaning:** domain glyphs (circle/square/diamond/ground/ring) and status glyphs (filled = supported, half = observed/partial, ring = preregistered/unresolved, dashed = intended/planned, minus = negative, strike = superseded) survive greyscale and print.
- **Imagery:** diagrams and runtime captures only, framed by `Figure` with numbered serif captions. No stock photography, no decorative illustration.
- **Motion:** minimal. 120–220ms `cubic-bezier(.2,.6,.2,1)` on hover/focus colours only. No bounces, no pulsing. `prefers-reduced-motion` honoured.
- **Hover:** links darken from blue-ink to ink and the underline becomes solid; secondary buttons gain `--paper-1` ground and ink ring. **Press:** no shrink. **Focus:** 2px modality-blue outline, 2px offset.
- **Transparency/blur:** not used.
- **Tables:** book style — ink rules top/bottom, hairline rows, uppercase mono headers, tabular numerals.
- **Historical material** stays fully legible (≥4.5:1), signalled by strike, ink-2 title, hatch and a "Superseded by" link — never by fading to illegibility.

## ICONOGRAPHY

- The repository has **no icon font or SVG icon set**. The Lab Workbench draws ~6 inline 24px stroke icons (1.6px, round caps) for its rail; they are app chrome and not copied.
- This system deliberately uses **almost no icons**. Meaning is carried by typed labels, rules and two small geometric glyph families drawn in code: `DomainGlyph` and `StatusGlyph` (see `components/core`). The search field uses one magnifier stroke.
- If an icon is unavoidable, use **Lucide** from CDN at 1.5px stroke, 16px, ink-3 — flagged as a substitution, not part of the source.
- Unicode used as typography, not icons: `§` section, `→` causation, `≠`/`!=` boundary, `·` separator, `×` dimensions. **No emoji.**
- Logo: `assets/logo/logo_horizontal.png` (lockup), `logo_graphic.png` (mark), `logo_wordmark.png`, `logo.png`. All have opaque white backgrounds — place on paper/white only.

---

## Index

- `styles.css` — entry point (imports only) → `tokens/fonts.css`, `colors.css`, `typography.css`, `spacing.css`, `base.css` (element defaults + `.sym-prose` long-form styles)
- `guidelines/` — foundation specimen cards (Colors, Type, Spacing)
- `brand/` — logo and domain-glyph cards
- `assets/logo/` — logo PNGs
- `components/` — React primitives (see below), one card per directory
- `ui_kits/docs/` — documentation site recreation (`index.html`)
- `DESIGN.md` — portable design spec: YAML tokens + rules
- `thumbnail.html`, `SKILL.md`, `github.md`

### Components

- **core/** — `DomainTag`, `DomainGlyph`, `StatusMark`, `StatusGlyph`, `EvidenceMeter`
- **blocks/** — `Callout` (note, principle, invariant, hypothesis, evidence, implementation, limitation, warning, decision, superseded), `CodeBlock`, `Figure`, `DataTable`, `DecisionList`
- **document/** — `DocHeader`, `SectionHeading`, `SourceList`, `Lineage`
- **navigation/** — `DocNav`, `Toc`, `Breadcrumb`, `SearchField`, `Button`

No component library exists in the source for documentation, so this set was authored for the brief's information classes. Intentional additions: `DomainGlyph`/`StatusGlyph` (shape encodings used by other components).

### Fonts

Loaded from Google Fonts (no binaries in the repo): Source Serif 4, Schibsted Grotesk, Martian Mono. These are new choices, not substitutions for an existing brand face.
