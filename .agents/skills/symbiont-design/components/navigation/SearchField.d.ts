/**
 * Corpus search input: hairline field, 2px radius, keyboard shortcut hint. Focus turns the hairline to ink.
 */
export interface SearchFieldProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  shortcut?: string;
  width?: number | string;
}
export function SearchField(props: SearchFieldProps): JSX.Element;
