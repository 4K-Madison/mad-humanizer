import DetectorScoreCard from "./DetectorScoreCard";
import { Clock } from "lucide-react";

export default function DetectorResults({ results, processingTime }) {
  if (!results || results.length === 0) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-500" />
          <span className="font-display text-sm font-bold uppercase tracking-wide text-foreground">
            Results
          </span>
        </div>
        {processingTime != null && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            <span>{(processingTime / 1000).toFixed(1)}s</span>
          </div>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {results.map((result) => (
          <DetectorScoreCard key={result.detector} result={result} />
        ))}
      </div>
    </div>
  );
}
