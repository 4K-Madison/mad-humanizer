import { Loader2 } from "lucide-react";

export default function LoadingSpinner({ message }) {
  return (
    <div className="flex items-center justify-center gap-3 py-8">
      <Loader2 className="h-5 w-5 animate-spin text-badger" />
      {message && (
        <span className="font-display text-sm font-semibold text-muted-foreground">
          {message}
        </span>
      )}
    </div>
  );
}
