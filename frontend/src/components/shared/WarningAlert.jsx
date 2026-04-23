import { AlertTriangle, X } from "lucide-react";

export default function WarningAlert({ message, onDismiss }) {
  if (!message) return null;

  return (
    <div className="flex items-start gap-3 rounded-xl border border-amber-200/80 bg-amber-50 px-5 py-4">
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-500" />
      <div className="flex flex-1 items-start justify-between gap-4">
        <p className="text-sm leading-relaxed text-amber-800">{message}</p>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="shrink-0 rounded-md p-1 text-amber-400 transition-colors hover:bg-amber-100 hover:text-amber-600"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
