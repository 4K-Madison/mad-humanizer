import { Button } from "@/components/ui/button";
import { Loader2, Zap } from "lucide-react";

const MAX_LENGTH = 10000;

export default function HumanizerForm({ value, onChange, onSubmit, isLoading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim() && !isLoading) {
      onSubmit(value);
    }
  };

  const charPercent = (value.length / MAX_LENGTH) * 100;

  return (
    <form onSubmit={handleSubmit} className="flex flex-1 flex-col">
      <div className="relative flex-1">
        <textarea
          placeholder="Paste your AI-generated text here..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          maxLength={MAX_LENGTH}
          rows={12}
          disabled={isLoading}
          className="w-full resize-none rounded-xl border border-border/80 bg-white px-5 py-4 font-body text-sm leading-relaxed text-foreground placeholder:text-muted-foreground/60 focus:border-badger focus:outline-none focus:ring-2 focus:ring-badger/10 disabled:cursor-not-allowed disabled:opacity-60"
        />
      </div>

      <div className="mt-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-muted-foreground">
            {value.length.toLocaleString()} / {MAX_LENGTH.toLocaleString()}
          </span>
          {/* Micro progress bar for character count */}
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
              Humanizing...
            </>
          ) : (
            <>
              <Zap className="h-4 w-4" />
              Humanize
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
