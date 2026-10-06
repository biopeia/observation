/**
 * "Principal sources" block that closes a chapter: repository paths tagged by kind (design, src, test, adr, study).
 */
export interface SourceItem {
  path: string;
  kind?: "design" | "code" | "test" | "adr" | "study" | "doc" | "config";
  note?: string;
  href?: string;
}
export interface SourceListProps {
  title?: string;
  items: SourceItem[];
}
export function SourceList(props: SourceListProps): JSX.Element;
