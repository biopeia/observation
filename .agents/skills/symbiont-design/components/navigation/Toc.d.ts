import { ReactNode } from "react";

/**
 * "On this page" outline for the right margin. Level-3 entries indent; active entry gets the ink hairline.
 */
export interface TocProps {
  items: { id: string; label: ReactNode; number?: string; level?: 2 | 3 }[];
  activeId?: string;
  title?: string;
  onSelect?: (id: string) => void;
}
export function Toc(props: TocProps): JSX.Element;
