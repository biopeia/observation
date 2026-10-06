import { ReactNode } from "react";
import { Domain } from "../core/DomainTag";
import { Status } from "../core/StatusMark";

export interface DocNavItem { id: string; label: ReactNode; number?: string; status?: Status; }
export interface DocNavSection { label: string; domain?: Domain; items: DocNavItem[]; }

/**
 * Corpus sidebar: sections (optionally domain-coded) of numbered documents with trailing status glyphs. Active item = ink hairline.
 * @startingPoint section="Navigation" subtitle="Corpus sidebar with domains and status glyphs" viewport="320x640"
 */
export interface DocNavProps {
  sections: DocNavSection[];
  activeId?: string;
  onSelect?: (id: string) => void;
  /** Slot above sections (brand, search). */
  header?: ReactNode;
}
export function DocNav(props: DocNavProps): JSX.Element;
