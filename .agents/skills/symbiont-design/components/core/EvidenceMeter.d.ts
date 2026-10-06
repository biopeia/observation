/**
 * Four-step evidence strength indicator: 0 none → 4 preregistered & replicated.
 */
export interface EvidenceMeterProps {
  /** 0–4 */
  level?: 0 | 1 | 2 | 3 | 4;
  /** Override the default level description. */
  label?: string;
  /** Scope qualifier, e.g. "Physics3D, 3 seeds". */
  scope?: string;
  /** Bars only. */
  compact?: boolean;
}
export function EvidenceMeter(props: EvidenceMeterProps): JSX.Element;
