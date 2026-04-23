import { useMemo } from "react";
import { computeDiff } from "@/lib/diff";

/**
 * Renders a word-level diff between `original` and `humanized`.
 *
 * mode === "inline": single panel showing the humanized text with added
 * segments highlighted green. Removed segments are hidden for readability.
 *
 * mode === "split": two panels side-by-side. Left shows the original
 * with removed segments highlighted red; right shows the humanized output
 * with added segments highlighted green.
 */
export default function DiffView({ original, humanized, mode = "inline" }) {
  const parts = useMemo(
    () => computeDiff(original, humanized),
    [original, humanized],
  );

  if (mode === "split") {
    return <SplitDiff parts={parts} />;
  }
  return <InlineDiff parts={parts} />;
}

function InlineDiff({ parts }) {
  return (
    <div className="h-full w-full overflow-auto rounded-xl border border-emerald-200/80 bg-emerald-50/30 px-5 py-4">
      <p className="whitespace-pre-wrap font-body text-sm leading-relaxed text-foreground">
        {parts.map((p, i) => {
          if (p.type === "removed") return null;
          if (p.type === "added") {
            return (
              <mark
                key={i}
                className="rounded bg-emerald-200/70 px-0.5 text-emerald-900"
              >
                {p.text}
              </mark>
            );
          }
          return (
            <span key={i} className="text-muted-foreground">
              {p.text}
            </span>
          );
        })}
      </p>
    </div>
  );
}

function SplitDiff({ parts }) {
  return (
    <div className="grid h-full gap-3 sm:grid-cols-2">
      <div className="overflow-auto rounded-xl border border-rose-200/80 bg-rose-50/30 px-5 py-4">
        <div className="mb-2 font-display text-xs font-bold uppercase tracking-wide text-rose-700">
          Original
        </div>
        <p className="whitespace-pre-wrap font-body text-sm leading-relaxed text-foreground">
          {parts.map((p, i) => {
            if (p.type === "added") return null;
            if (p.type === "removed") {
              return (
                <mark
                  key={i}
                  className="rounded bg-rose-200/70 px-0.5 text-rose-900 line-through decoration-rose-400"
                >
                  {p.text}
                </mark>
              );
            }
            return (
              <span key={i} className="text-muted-foreground">
                {p.text}
              </span>
            );
          })}
        </p>
      </div>
      <div className="overflow-auto rounded-xl border border-emerald-200/80 bg-emerald-50/30 px-5 py-4">
        <div className="mb-2 font-display text-xs font-bold uppercase tracking-wide text-emerald-700">
          Humanized
        </div>
        <p className="whitespace-pre-wrap font-body text-sm leading-relaxed text-foreground">
          {parts.map((p, i) => {
            if (p.type === "removed") return null;
            if (p.type === "added") {
              return (
                <mark
                  key={i}
                  className="rounded bg-emerald-200/70 px-0.5 text-emerald-900"
                >
                  {p.text}
                </mark>
              );
            }
            return (
              <span key={i} className="text-muted-foreground">
                {p.text}
              </span>
            );
          })}
        </p>
      </div>
    </div>
  );
}
