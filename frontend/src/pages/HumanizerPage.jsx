import { useState } from "react";
import { useHumanize } from "@/hooks/useHumanize";
import HumanizerForm from "@/components/humanizer/HumanizerForm";
import HumanizerResult from "@/components/humanizer/HumanizerResult";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import ErrorAlert from "@/components/shared/ErrorAlert";
import { Zap, ArrowRight } from "lucide-react";

export default function HumanizerPage() {
  const [inputText, setInputText] = useState("");
  const { result, isLoading, error, humanize, reset } = useHumanize();

  const handleSubmit = (text) => {
    humanize(text);
  };

  const handleInputChange = (text) => {
    setInputText(text);
    if (result) reset();
  };

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-badger/10">
            <Zap className="h-5 w-5 text-badger" />
          </div>
          <div>
            <h1 className="font-display text-3xl font-extrabold tracking-tight text-foreground">
              AI Text Humanizer
            </h1>
          </div>
        </div>
        <p className="max-w-2xl text-base leading-relaxed text-muted-foreground">
          Paste AI-generated text on the left, get natural human-sounding content on the right. Powered by fine-tuned Llama 3.2 with LoRA adapters.
        </p>
      </div>

      {/* Side-by-side panels */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Input panel */}
        <div className="flex flex-col">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-badger" />
              <span className="font-display text-sm font-bold uppercase tracking-wide text-foreground">
                Input
              </span>
            </div>
            <span className="text-xs font-medium text-muted-foreground">
              AI-Generated Text
            </span>
          </div>
          <HumanizerForm
            value={inputText}
            onChange={handleInputChange}
            onSubmit={handleSubmit}
            isLoading={isLoading}
          />
        </div>

        {/* Output panel */}
        <div className="flex flex-col">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="font-display text-sm font-bold uppercase tracking-wide text-foreground">
                Output
              </span>
            </div>
            <span className="text-xs font-medium text-muted-foreground">
              Humanized Text
            </span>
          </div>
          <HumanizerResult result={result} isLoading={isLoading} />
        </div>
      </div>

      {/* Arrow indicator between panels (visible on lg+) */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 hidden -translate-x-1/2 -translate-y-1/2 lg:block" aria-hidden="true">
        {/* Decorative — hidden because the grid gap is sufficient */}
      </div>

      <ErrorAlert message={error} onDismiss={reset} />

      {isLoading && <LoadingSpinner message="Humanizing your text..." />}

      {/* Stats bar */}
      {result && (
        <div className="flex flex-wrap items-center gap-6 rounded-xl border border-border/60 bg-white px-6 py-4">
          <div className="flex items-center gap-2">
            <ArrowRight className="h-4 w-4 text-badger" />
            <span className="font-display text-xs font-bold uppercase tracking-wide text-muted-foreground">Stats</span>
          </div>
          <div className="flex flex-wrap gap-6 text-sm">
            <span className="text-muted-foreground">
              Input: <strong className="text-foreground">{result.input_length}</strong> chars
            </span>
            <span className="text-muted-foreground">
              Output: <strong className="text-foreground">{result.output_length}</strong> chars
            </span>
            <span className="text-muted-foreground">
              Time: <strong className="text-foreground">{(result.processing_time_ms / 1000).toFixed(1)}s</strong>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
