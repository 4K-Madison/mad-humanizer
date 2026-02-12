import CopyButton from "@/components/shared/CopyButton";
import { FileText } from "lucide-react";

export default function HumanizerResult({ result, isLoading }) {
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

  return (
    <div className="flex flex-1 flex-col">
      <div className="relative flex-1">
        <textarea
          value={result.humanized_text}
          readOnly
          rows={12}
          className="w-full resize-none rounded-xl border border-emerald-200/80 bg-emerald-50/30 px-5 py-4 font-body text-sm leading-relaxed text-foreground focus:outline-none"
        />
        <div className="absolute right-3 top-3">
          <CopyButton text={result.humanized_text} />
        </div>
      </div>
    </div>
  );
}
