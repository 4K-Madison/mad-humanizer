import { Button } from "@/components/ui/button";
import { Loader2, ScanSearch } from "lucide-react";

const MAX_LENGTH = 10000;

export default function DetectorForm({ value, onChange, onSubmit, isLoading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim() && !isLoading) {
      onSubmit(value);
    }
  };

  const charPercent = (value.length / MAX_LENGTH) * 100;

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <textarea
        placeholder="Paste text to analyze for AI detection..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        maxLength={MAX_LENGTH}
        rows={8}
        disabled={isLoading}
        className="w-full resize-none rounded-xl border border-border/80 bg-white px-5 py-4 font-body text-sm leading-relaxed text-foreground placeholder:text-muted-foreground/60 focus:border-badger focus:outline-none focus:ring-2 focus:ring-badger/10 disabled:cursor-not-allowed disabled:opacity-60"
      />
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-muted-foreground">
            {value.length.toLocaleString()} / {MAX_LENGTH.toLocaleString()}
          </span>
          <div className="h-1 w-16 overflow-hidden rounded-full bg-border/60">
            <div
              className="h-full rounded-full bg-badger/40 transition-all duration-300"
              style={{ width: `${Math.min(charPercent, 100)}%` }}
            />
          </div>
        </div>

        <Button type="submit" disabled={!value.trim() || isLoading} className="gap-2">
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Detecting...
            </>
          ) : (
            <>
              <ScanSearch className="h-4 w-4" />
              Run Detection
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
