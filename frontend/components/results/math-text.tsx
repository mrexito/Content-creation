"use client";

import katex from "katex";
import { useMemo } from "react";

const SPLIT_RE = /(\$\$[^$]+\$\$|\$[^$\n]+?\$)/g;

function stripLatex(expr: string): string {
  return expr
    .replace(/\\(bigl|bigr|big|left|right|displaystyle|textstyle)\b/g, "")
    .replace(/\\(,|;|:|!|quad|qquad)/g, " ")
    .replace(/\\\\/g, " ")
    .replace(/[{}]/g, "")
    .replace(/\$/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function tryRender(expr: string, display: boolean): string | null {
  try {
    return katex.renderToString(expr, {
      displayMode: display,
      throwOnError: true,
      strict: false,
      output: "html",
    });
  } catch {
    return null;
  }
}

interface MathTextProps {
  text: string;
  className?: string;
  emptyFallback?: string;
}

export function MathText({
  text,
  className = "",
  emptyFallback = "—",
}: MathTextProps) {
  const parts = useMemo(() => {
    if (!text) return [];
    return text.split(SPLIT_RE).filter((p) => p !== "");
  }, [text]);

  if (!text) {
    return <span className={className}>{emptyFallback}</span>;
  }

  return (
    <span className={className}>
      {parts.map((part, i) => {
        const displayMatch = /^\$\$([\s\S]+)\$\$$/.exec(part);
        const inlineMatch = /^\$([\s\S]+?)\$$/.exec(part);
        const match = displayMatch ?? inlineMatch;

        if (!match) {
          return <span key={i}>{part}</span>;
        }

        const expr = match[1];
        const display = displayMatch != null;
        const html = tryRender(expr, display);

        if (html) {
          return (
            <span
              key={i}
              className="katex-host"
              dangerouslySetInnerHTML={{ __html: html }}
            />
          );
        }

        return (
          <span
            key={i}
            title="Ungültiges LaTeX – als Plaintext angezeigt"
            className="px-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200"
          >
            {stripLatex(expr)}
          </span>
        );
      })}
    </span>
  );
}
