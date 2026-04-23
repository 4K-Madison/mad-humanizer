import { ShieldCheck, ShieldAlert, ShieldX, Shield } from "lucide-react";

export default function AIScoreBadge({ score, threshold = 0.35 }) {
  if (score === null || score === undefined) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-border/80 bg-muted px-3 py-1 text-xs font-semibold text-muted-foreground">
        <Shield className="h-3.5 w-3.5" />
        AI score unavailable
      </span>
    );
  }

  const pct = Math.round(score * 100);
  let Icon = ShieldCheck;
  let classes = "border-emerald-200 bg-emerald-50 text-emerald-800";

  if (score > 0.5) {
    Icon = ShieldX;
    classes = "border-red-200 bg-red-50 text-red-700";
  } else if (score > threshold) {
    Icon = ShieldAlert;
    classes = "border-amber-200 bg-amber-50 text-amber-800";
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${classes}`}
      title={`AI detection score: ${pct}% (threshold ${Math.round(threshold * 100)}%)`}
    >
      <Icon className="h-3.5 w-3.5" />
      AI score: {pct}%
    </span>
  );
}
