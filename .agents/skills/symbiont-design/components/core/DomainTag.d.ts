import { ReactNode } from "react";

export type Domain = "symbiont" | "embodiment" | "modality" | "environment" | "lab";

/**
 * Marks which of the five package domains a document, section or entity belongs to.
 * Each domain has a hue AND a shape (circle, square, diamond, ground, ring) so it survives greyscale.
 * @startingPoint section="Core" subtitle="Domain tags for Symbiont, Embodiment, Modality, Environment, Lab" viewport="700x220"
 */
export interface DomainTagProps {
  domain?: Domain;
  /** label: glyph + mono text. filled: tinted chip. glyph: shape only. */
  variant?: "label" | "filled" | "glyph";
  children?: ReactNode;
  title?: string;
}
export function DomainTag(props: DomainTagProps): JSX.Element;

export interface DomainGlyphProps { domain?: Domain; size?: number; color?: string; }
export function DomainGlyph(props: DomainGlyphProps): JSX.Element;
