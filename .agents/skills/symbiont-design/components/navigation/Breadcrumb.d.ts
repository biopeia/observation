import { ReactNode } from "react";

/**
 * Path-style breadcrumb in mono, slash-separated — mirrors the repository path of the document.
 */
export interface BreadcrumbProps {
  items: { label: ReactNode; href?: string }[];
  onSelect?: (item: { label: ReactNode; href?: string }, index: number) => void;
}
export function Breadcrumb(props: BreadcrumbProps): JSX.Element;
