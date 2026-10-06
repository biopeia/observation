# ADR-0071 — Symbiont documentation design system

- **Status:** Accepted
- **Date:** 2026-10-06
- **Decision owner:** project owner
- **Relates to:** ADR-0054, `DESIGN.md`, `.agents/skills/symbiont-design/`, `AGENTS.md`, `CLAUDE.md`
- **Scope:** Visual identity and implementation guidance for the Symbiont documentation interface. This does not set visual or operational requirements for the organism, scientific apparatus, or Lab Workbench.

## Context

Symbiont's scientific corpus needs a consistent documentation identity across
specifications, ADRs, experiments, evidence and reference material. The pending
design-system work includes a root tokenized specification (`DESIGN.md`), CSS
token bindings, reusable React examples and a documentation UI kit. The repository
also provides the `symbiont-design` skill for work in this domain.

The specification and examples initially diverged: the CSS exposed semantic and
domain color variants absent from the YAML tokens; layout spacing differed from
the specified editorial gutter; and the button example used an unspecified,
low-opacity disabled treatment. Agent instructions also did not require using the
domain skill. Those gaps make visual behavior ambiguous and allow the example
implementation to drift from its own design contract.

## Decision

1. The root `DESIGN.md` is the normative source for visual decisions in the
   Symbiont documentation interface. Its YAML front matter defines the available
   color, typography, spacing, shape, motion and component tokens. CSS custom
   properties and React examples implement those tokens; they do not add
   competing visual decisions.
2. Before work on Symbiont visual identity, the documentation UI, or its design
   system, agents must use the `symbiont-design` skill. The skill is implementation
   guidance and examples; if it conflicts with `DESIGN.md`, the design document
   governs.
3. Resolve implementation/specification drift by recording the currently used
   CSS values in the YAML token system and aligning the CSS bindings and examples
   to those tokens. Preserve the specified 128px editorial label gutter and 4px
   spacing base.
4. Disabled buttons use the design's aside surface, meta text color and standard
   rule border, remain fully legible without opacity reduction, and retain native
   disabled semantics. Hover and focus remain defined independently.
5. These requirements apply only to the documentation interface. They do not
   authorize visual changes to the organism, scientific apparatus, or Lab
   Workbench, nor do they establish scientific claims or experiment authority.

## Alternatives considered

- **Leave the visual language only in the skill or component examples.** Rejected:
  those are implementation aids and cannot serve as a stable, portable authority.
- **Let CSS or the UI kit make unspecified choices.** Rejected: that permits
  drift and contradicts the requirement that the design tokens govern the UI.
- **Apply the documentation look to every project interface.** Rejected: the
  documentation identity does not define the Lab Workbench or scientific
  apparatus interfaces.
- **Dim disabled buttons with opacity.** Rejected: it was not specified and can
  reduce legibility. Use explicit semantic tokens instead.

## Consequences

- The root design specification, CSS token bindings and reference UI kit must be
  maintained together when visual decisions change.
- Agents have a clear, mandatory skill entry point for this design domain, while
  the design document remains the final visual authority.
- The design now defines the disabled button treatment explicitly; missing future
  component states remain specification gaps rather than invitations to guess.
- This decision does not claim that a production documentation website or
  component library is deployed.

## Acceptance

The project owner accepted this bounded decision on 2026-10-06. Acceptance covers
the documentation design authority, skill requirement and token-alignment work
described here only. It does not approve broader visual redesign or runtime
changes.
