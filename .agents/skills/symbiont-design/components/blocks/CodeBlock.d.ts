/**
 * Code, schema, boundary diagram (ASCII) or telemetry block. Paper tone for source and schemas; night tone for runtime output.
 */
export interface CodeBlockProps {
  code: string;
  /** Shown top-right in uppercase mono, e.g. "python", "toml", "text". */
  language?: string;
  /** File path or block title, top-left. */
  title?: string;
  caption?: string;
  tone?: "paper" | "night";
  lineNumbers?: boolean;
  /** 1-based line numbers to highlight. */
  highlight?: number[];
}
export function CodeBlock(props: CodeBlockProps): JSX.Element;
