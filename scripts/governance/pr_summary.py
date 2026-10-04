#!/usr/bin/env python3
"""Render the governed CI/authority summary for a pull request body."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from governance.ci_plan import build_plan  # noqa: E402

BEGIN = "<!-- BEGIN GOVERNED PR SUMMARY -->"
END = "<!-- END GOVERNED PR SUMMARY -->"


def render(base: str, head: str) -> str:
    plan = build_plan(base, head)
    authority = plan.classification
    if authority == "ORDINARY":
        disposition = "May auto-promote after governed CI if still current."
    elif authority == "SCIENTIFIC":
        disposition = "External owner/scientific review required before integration."
    elif authority == "CONSTITUTIONAL":
        disposition = "Accepted ADR and external owner review required before integration."
    else:
        disposition = "FROZEN evidence must not be modified in place."

    lanes = ", ".join(f"`{lane}`" for lane in plan.selected_lanes) or "none"
    reasons = (
        "\n".join(f"- {reason}" for reason in plan.reasons) or "- no elevated authority reason"
    )
    paths = "\n".join(f"- `{path}`" for path in plan.changed_paths[:25])
    if len(plan.changed_paths) > 25:
        paths += f"\n- … {len(plan.changed_paths) - 25} more"

    return f"""{BEGIN}
## Governed publication summary

- **Authority class:** `{authority}`
- **Disposition:** {disposition}
- **Selected technical lanes:** {lanes}
- **Engineering validation budget target:** {plan.budget_seconds}s
- **Impact planner:** observe-only — it records hypothetical targeted tests but cannot skip the authoritative lane yet.

### Why this authority class
{reasons}

### Changed surfaces
{paths or "- none"}

Authority and technical impact are deliberately independent: review requirements come from the authority class; test lanes come from the versioned impact matrix.
{END}"""


def merge_body(body: str, summary: str) -> str:
    if BEGIN in body and END in body:
        before = body.split(BEGIN, 1)[0].rstrip()
        after = body.split(END, 1)[1].lstrip()
        parts = [part for part in (before, summary, after) if part]
        return "\n\n".join(parts).rstrip() + "\n"
    if not body.strip():
        return summary.rstrip() + "\n"
    return body.rstrip() + "\n\n" + summary.rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--body-file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summary = render(args.base, args.head)
    output = summary
    if args.body_file:
        output = merge_body(args.body_file.read_text(encoding="utf-8"), summary)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
