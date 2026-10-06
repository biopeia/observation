export type Status =
  | "implemented" | "tested" | "observed" | "supported" | "intended" | "historical" | "unresolved"
  | "planned" | "preregistered" | "running" | "discovery" | "partial" | "negative" | "inconclusive" | "superseded" | "frozen"
  | "working" | "validated"
  | "proposed" | "accepted" | "partially-superseded"
  | "failing";

/**
 * Epistemic / lifecycle status of a claim, study, artifact or ADR. Monochrome glyph + uppercase mono label.
 * Only "failing" (integrity failure) uses the signal colour; negative results are ink, not red.
 */
export interface StatusMarkProps {
  status?: Status;
  /** Override the label text (defaults to the status name). */
  label?: string;
  /** Trailing scope/detail in sentence case, e.g. "3 seeds". */
  detail?: string;
  size?: "sm" | "md";
}
export function StatusMark(props: StatusMarkProps): JSX.Element;

export interface StatusGlyphProps { status?: Status; size?: number; }
export function StatusGlyph(props: StatusGlyphProps): JSX.Element;
