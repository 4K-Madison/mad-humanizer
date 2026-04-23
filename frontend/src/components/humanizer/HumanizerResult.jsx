import { useState } from "react";
import CopyButton from "@/components/shared/CopyButton";
import DiffView from "@/components/humanizer/DiffView";
import { FileText, Eye, SplitSquareHorizontal, Layers } from "lucide-react";

const VIEW_MODES = [
  { id: "clean", label: "Clean", icon: Eye },
  { id: "inline", label: "Diff", icon: Layers },
  { id: "split", label: "Split", icon: SplitSquareHorizontal },
];

export default function HumanizerResult({ result, isLoading, original = "" }) {
  const [viewMode, setViewMode] = useState("clean");

  if (!result && !isLoading) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-dashed border-border/80 bg-white/50 px-5 py-12">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-muted">
          <FileText className="h-6 w-6 text-muted-foreground/50" />
        </div>
        <p className="mt-3 text-center text-sm text-muted-foreground/60">
          Humanized text will appear here
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-border/80 bg-white px-5 py-12">
        <div className="flex items-center gap-3">
          <div className="h-2 w-2 animate-pulse-red rounded-full bg-badger" />
          <div className="h-2 w-2 animate-pulse-red rounded-full bg-badger" style={{ animationDelay: "0.3s" }} />
          <div className="h-2 w-2 animate-pulse-red rounded-full bg-badger" style={{ animationDelay: "0.6s" }} />
        </div>
        <p className="mt-4 text-sm font-medium text-muted-foreground">Processing...</p>
      </div>
    );
  }

  const humanized = result.humanized_text ?? "";
  const hasOriginal = Boolean(original && original.length > 0);
  const hasOutput = humanized.length > 0;
  const isIdentical = hasOriginal && hasOutput && original === humanized;
  const canDiff = hasOriginal && hasOutput;

  const effectiveMode = canDiff ? viewMode : "clean";

  return (
    <div className="flex flex-1 flex-col gap-3">
      {canDiff && (
        <div className="flex items-center justify-between gap-3">
          <div
            role="tablist"
            aria-label="Output view mode"
            className="inline-flex items-center gap-1 rounded-lg border border-border/80 bg-muted/40 p-1"
          >
            {VIEW_MODES.map((m) => {
              const Icon = m.icon;
              const active = effectiveMode === m.id;
              return (
                <button
                  key={m.id}
                  role="tab"
                  aria-selected={active}
                  onClick={() => setViewMode(m.id)}
                  className={
                    "inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-semibold transition-colors " +
                    (active
                      ? "bg-white text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground")
                  }
                >
                  <Icon className="h-3.5 w-3.5" />
                  {m.label}
                </button>
              );
            })}
          </div>
          {isIdentical && (
            <span className="text-xs font-medium text-amber-700">
              No changes detected — try raising temperature
            </span>
          )}
        </div>
      )}

      <div className="relative flex flex-1 flex-col">
        {effectiveMode === "clean" ? (
          <>
            <textarea
              value={humanized}
              readOnly
              rows={12}
              className="w-full resize-none rounded-xl border border-emerald-200/80 bg-emerald-50/30 px-5 py-4 font-body text-sm leading-relaxed text-foreground focus:outline-none"
            />
            <div className="absolute right-3 top-3">
              <CopyButton text={humanized} />
            </div>
          </>
        ) : (
          <div className="relative min-h-[18rem] flex-1">
            <DiffView
              original={original}
              humanized={humanized}
              mode={effectiveMode}
            />
            <div className="absolute right-3 top-3">
              <CopyButton text={humanized} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
