import DetectorScoreCard from "./DetectorScoreCard";

export default function DetectorResults({ results, processingTime }) {
  if (!results || results.length === 0) return null;

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {results.map((result) => (
          <DetectorScoreCard key={result.detector} result={result} />
        ))}
      </div>
      {processingTime != null && (
        <p className="text-sm text-muted-foreground">
          Processing time: {(processingTime / 1000).toFixed(1)}s
        </p>
      )}
    </div>
  );
}
