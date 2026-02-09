import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

const MAX_LENGTH = 10000;

export default function HumanizerForm({ value, onChange, onSubmit, isLoading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim() && !isLoading) {
      onSubmit(value);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <Textarea
        placeholder="Paste your AI-generated text here..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        maxLength={MAX_LENGTH}
        rows={8}
        className="resize-y"
        disabled={isLoading}
      />
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">
          {value.length.toLocaleString()} / {MAX_LENGTH.toLocaleString()} characters
        </span>
        <Button type="submit" disabled={!value.trim() || isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Humanizing...
            </>
          ) : (
            "Humanize"
          )}
        </Button>
      </div>
    </form>
  );
}
