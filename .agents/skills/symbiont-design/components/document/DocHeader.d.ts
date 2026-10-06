import { ReactNode } from "react";
import { Domain } from "../core/DomainTag";
import { Status } from "../core/StatusMark";

export type DocType = "chapter" | "adr" | "specification" | "study" | "protocol" | "reference" | "anatomy" | "history" | "audit";

/**
 * Document masthead: type + id + status rule line, domain tags, serif title, gutter-labelled abstract and a metadata grid.
 * @startingPoint section="Document" subtitle="Title, abstract and metadata for any spec, ADR or study" viewport="900x520"
 */
export interface DocHeaderProps {
  docType?: DocType;
  /** e.g. "ADR-0011", "§03", "E1". */
  id?: string;
  title: ReactNode;
  subtitle?: ReactNode;
  abstract?: ReactNode;
  domains?: Domain[];
  status?: Status;
  meta?: { label: string; value: ReactNode; mono?: boolean }[];
  supersededBy?: string;
}
export function DocHeader(props: DocHeaderProps): JSX.Element;
