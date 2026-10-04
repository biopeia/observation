# Current architecture

This page is the repository-level entry point for architecture. The former
version described a legacy package layout and runtime that no longer match the
current implementation. It has been replaced rather than retained as a
current-state specification.

## Canonical sources

- [Scientific description of Symbiont](../symbiont/docs/index.md) is the
  canonical explanation of the organism, its boundaries, processes, state
  ownership and evidence limits.
- [Repository overview](../README.md) describes the workspace and its packages.
- [Architecture decision records](adr/README.md) record accepted decisions;
  they explain rationale but do not override current implementation evidence.
- [Design documents](design/README.md) describe proposals, specifications and
  implementation audits. A design document is not evidence that its behavior
  is implemented.
- [Open migration issues](../migration/open-issues.md) records the remaining
  migration and audit work.

## Verification rule

Use the current source and tests to verify implementation claims. In
particular, do not infer current package boundaries, checkpoint compatibility,
organism capabilities or scientific utility from historical package names,
design milestones or architecture prose alone. The canonical scientific
description distinguishes implemented mechanisms from unverified utility and
causal claims.
