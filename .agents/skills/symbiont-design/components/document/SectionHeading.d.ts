import { ReactNode } from "react";

/**
 * Numbered section heading with § number in the left gutter. Level 2 = serif with rule above; level 3 = sans semibold.
 */
export interface SectionHeadingProps {
  number?: string;
  title: ReactNode;
  level?: 2 | 3;
  id?: string;
  /** Optional uppercase sub-label under the number, e.g. "Specification". */
  kicker?: string;
}
export function SectionHeading(props: SectionHeadingProps): JSX.Element;
