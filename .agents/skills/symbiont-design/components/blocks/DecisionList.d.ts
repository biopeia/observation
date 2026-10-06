import { ReactNode } from "react";
import { Status } from "../core/StatusMark";

export interface DecisionItem {
  title: ReactNode;
  body?: ReactNode;
  /** Per-decision state, e.g. "superseded" for a decision replaced by a later ADR. */
  status?: Status;
  statusDetail?: string;
}

/**
 * Numbered ADR decisions (D01, D02…) in a gutter layout; individual decisions can carry their own status.
 */
export interface DecisionListProps {
  items: DecisionItem[];
  start?: number;
}
export function DecisionList(props: DecisionListProps): JSX.Element;
