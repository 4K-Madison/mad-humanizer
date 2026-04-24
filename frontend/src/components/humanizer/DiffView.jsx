import { useMemo } from "react";
import { computeDiff } from "@/lib/diff";

export default function DiffView({ original, humanized }) {
  const parts = useMemo(
    () => computeDiff(original, humanized),
    [original, humanized],
  );

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
