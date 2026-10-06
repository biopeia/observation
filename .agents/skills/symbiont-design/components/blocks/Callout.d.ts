import { ReactNode } from "react";
import { Status } from "../core/StatusMark";

export type CalloutKind = "note" | "principle" | "invariant" | "hypothesis" | "evidence" | "implementation" | "limitation" | "warning" | "decision" | "superseded";

/**
 * Typed block for one information class in a scientific document (invariant, hypothesis, evidence, ADR decision…).
 * The kind is shown as a gutter label; structure (rule weight/dash, ground) encodes the class — never colour alone.
 * @startingPoint section="Blocks" subtitle="Invariants, hypotheses, evidence, decisions, limitations" viewport="700x900"
 */
export interface CalloutProps {
  kind?: CalloutKind;
  title?: ReactNode;
  /** Stable identifier shown under the label, e.g. "INV-03", "H1", "ADR-0013 §3". */
  id?: string;
  status?: Status;
  /** Evidence strength 0–4 (renders EvidenceMeter). */
  strength?: 0 | 1 | 2 | 3 | 4;
  /** Scope for the evidence meter, e.g. "Physics3D, seeds 11–13". */
  scope?: string;
  /** Source path / test / artefact. */
  source?: string;
  /** For kind="superseded": the replacing document id. */
  supersededBy?: string;
  children?: ReactNode;
}
export function Callout(props: CalloutProps): JSX.Element;
