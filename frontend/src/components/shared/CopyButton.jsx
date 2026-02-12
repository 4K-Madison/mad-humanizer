import { useState } from "react";
import { Check, Copy } from "lucide-react";

export default function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback silently
    }
  };

  return (
    <button
      onClick={handleCopy}
      className={`
        flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-all
        ${copied
          ? "border-emerald-200 bg-emerald-50 text-emerald-600"
          : "border-border/80 bg-white text-muted-foreground hover:border-badger/40 hover:text-badger"
        }
      `}
    >
      {copied ? (
        <>
          <Check className="h-3.5 w-3.5" />
          Copied
        </>
      ) : (
        <>
          <Copy className="h-3.5 w-3.5" />
          Copy
        </>
      )}
    </button>
  );
}
