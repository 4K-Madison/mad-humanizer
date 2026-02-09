import { Loader2 } from "lucide-react";

export default function LoadingSpinner({ message }) {
  return (
    <div className="flex items-center justify-center gap-2 py-8 text-muted-foreground">
      <Loader2 className="h-5 w-5 animate-spin" />
      {message && <span>{message}</span>}
    </div>
  );
}
