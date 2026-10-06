import { ReactNode } from "react";
import { Status } from "../core/StatusMark";

export interface LineageItem {
  id: string;
  title?: ReactNode;
  /** Relation to the next (older) item, e.g. "supersedes decision 3 of". */
  relation?: string;
  status?: Status;
  date?: string;
}

/**
 * Vertical descent line for supersession and version history, newest first. Uses status glyphs as nodes.
 */
export interface LineageProps {
  items: LineageItem[];
  title?: string;
}
export function Lineage(props: LineageProps): JSX.Element;
