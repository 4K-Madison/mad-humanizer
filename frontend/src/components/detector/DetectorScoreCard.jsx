import { AlertCircle, ShieldCheck, ShieldAlert, ShieldQuestion } from "lucide-react";

function getScoreConfig(score) {
  if (score < 0.3) {
    return {
      color: "text-emerald-600",
      bg: "bg-emerald-50",
      border: "border-emerald-200/80",
      ring: "ring-emerald-100",
      label: "Likely Human",
      icon: ShieldCheck,
      iconColor: "text-emerald-500",
      barColor: "bg-emerald-500",
    };
  }
  if (score < 0.7) {
    return {
      color: "text-amber-600",
      bg: "bg-amber-50",
      border: "border-amber-200/80",
      ring: "ring-amber-100",
      label: "Uncertain",
      icon: ShieldQuestion,
      iconColor: "text-amber-500",
      barColor: "bg-amber-500",
    };
  }
  return {
    color: "text-badger",
    bg: "bg-badger-50",
    border: "border-badger-100",
    ring: "ring-badger-50",
    label: "Likely AI",
    icon: ShieldAlert,
    iconColor: "text-badger",
    barColor: "bg-badger",
  };
}

export default function DetectorScoreCard({ result }) {
  if (result.error) {
    return (
      <div className="rounded-xl border border-red-200/80 bg-red-50/50 p-5">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-sm font-bold text-foreground">{result.detector}</h3>
          <AlertCircle className="h-4 w-4 text-red-400" />
        </div>
        <p className="mt-2 text-sm text-red-600">{result.error}</p>
      </div>
    );
  }

  const scorePercent = result.score != null ? Math.round(result.score * 100) : null;
  const config = result.score != null ? getScoreConfig(result.score) : null;
  const Icon = config?.icon;

  return (
    <div className={`rounded-xl border p-5 transition-all hover:shadow-md ${config ? `${config.bg} ${config.border}` : "border-border/80 bg-white"}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-display text-sm font-bold text-foreground">{result.detector}</h3>
        {Icon && <Icon className={`h-5 w-5 ${config.iconColor}`} />}
      </div>

      {/* Score */}
      {scorePercent != null && (
        <div className="mt-3">
          <div className="flex items-baseline gap-1">
            <span className={`font-display text-4xl font-black ${config.color}`}>
              {scorePercent}
            </span>
            <span className={`font-display text-lg font-bold ${config.color}`}>%</span>
          </div>

          {/* Progress bar */}
          <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/80">
            <div
              className={`h-full rounded-full ${config.barColor} transition-all duration-500`}
              style={{ width: `${scorePercent}%` }}
            />
          </div>

          {/* Label */}
          <p className="mt-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            {result.label || config.label}
          </p>
        </div>
      )}
    </div>
  );
}
