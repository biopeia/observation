import { ReactNode } from "react";

export interface DataTableColumn {
  key: string;
  label: string;
  align?: "left" | "right" | "center";
  /** Render cells in the mono face (ids, paths, numbers with units). */
  mono?: boolean;
  width?: number | string;
}

/**
 * Book-style table: ink rules top/bottom, hairline row separators, no fills or zebra striping.
 */
export interface DataTableProps {
  columns: DataTableColumn[];
  rows: Record<string, ReactNode>[];
  number?: string | number;
  caption?: ReactNode;
  dense?: boolean;
}
export function DataTable(props: DataTableProps): JSX.Element;
