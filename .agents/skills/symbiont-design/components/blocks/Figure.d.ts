import { ReactNode } from "react";

/**
 * Numbered figure frame for diagrams, plots and runtime captures, with serif caption and source path.
 */
export interface FigureProps {
  number?: string | number;
  caption?: ReactNode;
  /** Generating script or artefact path. */
  source?: string;
  /** paper: hairline-framed; night: instrument surface for runtime/telemetry views. */
  tone?: "paper" | "night";
  height?: number | string;
  wide?: boolean;
  children?: ReactNode;
}
export function Figure(props: FigureProps): JSX.Element;
