# UI kit — Symbiont documentation site

A click-through recreation of how the Symbiont Markdown corpus reads when rendered with this design system. There is no existing documentation website in the repository (only Markdown and the dark Lab Workbench), so the layout is new; **all body copy is quoted from repository Markdown**.

Screens (switch via the sidebar):
- `ScreenIndex.jsx` — `symbiont/docs/index.md` corpus entry + five-domain table
- `ScreenChapter.jsx` — `§ 03 World, body and embodiment` with a night-tone boundary figure
- `ScreenAdr.jsx` — `ADR-0011` with partial supersession, DecisionList, Lineage
- `ScreenEvidence.jsx` — E1–E8 falsification battery, evidence lifecycle
- `ScreenGlossary.jsx` — `docs/glossary.md`

`Shell.jsx` holds the three-column frame: 272px nav · reading column (128px gutter + 68ch) · 220px TOC. Prose blocks are indented 152px so they align with the content column of Callouts and SectionHeadings.
