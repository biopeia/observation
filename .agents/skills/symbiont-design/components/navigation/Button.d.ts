import { ReactNode } from "react";

/**
 * Minimal action button. primary = ink fill; secondary = hairline; quiet = underlined text. 2px radius, no shadow.
 */
export interface ButtonProps {
  variant?: "primary" | "secondary" | "quiet";
  size?: "sm" | "md";
  disabled?: boolean;
  onClick?: () => void;
  type?: "button" | "submit";
  children?: ReactNode;
}
export function Button(props: ButtonProps): JSX.Element;
