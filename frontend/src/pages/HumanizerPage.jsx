import { useMemo, useState } from "react";
import { useHumanize } from "@/hooks/useHumanize";
import HumanizerForm from "@/components/humanizer/HumanizerForm";
import HumanizerResult from "@/components/humanizer/HumanizerResult";
import AIScoreBadge from "@/components/humanizer/AIScoreBadge";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import ErrorAlert from "@/components/shared/ErrorAlert";
import WarningAlert from "@/components/shared/WarningAlert";
import { computeDiff, diffStats } from "@/lib/diff";
import { Zap, ArrowRight, Repeat, Edit3 } from "lucide-react";

export default function HumanizerPage() {
  const [inputText, setInputText] = useState("");
  const [submittedText, setSubmittedText] = useState("");
  const { result, isLoading, error, humanize, reset } = useHumanize();

  const handleSubmit = (text) => {
    setSubmittedText(text);
    humanize(text);
  };

  const handleInputChange = (text) => {
    setInputText(text);
    if (result) {
      reset();
      setSubmittedText("");
    }
  };

  const attemptsCount = result?.attempts?.length ?? 0;
  const attemptsLabel =
    attemptsCount <= 1
      ? "Humanized in 1 attempt"
      : result?.threshold_met
        ? `Humanized in ${attemptsCount} attempts`
        : `Humanized in ${attemptsCount} attempts (best of ${attemptsCount})`;

  const changeStats = useMemo(() => {
    if (!result?.humanized_text || !submittedText) return null;
    return diffStats(computeDiff(submittedText, result.humanized_text));
  }, [result?.humanized_text, submittedText]);

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
          Paste AI-generated text on the left, get natural human-sounding content on the right. Powered by fine-tuned Gemma-2-9B with LoRA & DPO adapters.
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
          <HumanizerResult
            result={result}
            isLoading={isLoading}
            original={submittedText}
          />
        </div>
      </div>

      <ErrorAlert message={error} onDismiss={reset} />

      {result?.warning && <WarningAlert message={result.warning} />}

      {isLoading && (
        <LoadingSpinner message="Humanizing and verifying (this may take up to ~60s)..." />
      )}

      {/* Stats bar */}
      {result && (
        <div className="flex flex-wrap items-center gap-6 rounded-xl border border-border/60 bg-white px-6 py-4">
          <div className="flex items-center gap-2">
            <ArrowRight className="h-4 w-4 text-badger" />
            <span className="font-display text-xs font-bold uppercase tracking-wide text-muted-foreground">Stats</span>
          </div>
          <div className="flex flex-wrap items-center gap-6 text-sm">
            <span className="text-muted-foreground">
              Input: <strong className="text-foreground">{result.input_length}</strong> chars
            </span>
            <span className="text-muted-foreground">
              Output: <strong className="text-foreground">{result.output_length}</strong> chars
            </span>
            <span className="text-muted-foreground">
              Time: <strong className="text-foreground">{(result.processing_time_ms / 1000).toFixed(1)}s</strong>
            </span>
            {attemptsCount > 0 && (
              <span className="inline-flex items-center gap-1.5 text-muted-foreground">
                <Repeat className="h-3.5 w-3.5" />
                {attemptsLabel}
              </span>
            )}
            {changeStats && (
              <span
                className="inline-flex items-center gap-1.5 text-muted-foreground"
                title={`+${changeStats.added} chars added, -${changeStats.removed} chars removed`}
              >
                <Edit3 className="h-3.5 w-3.5" />
                Changed: <strong className="text-foreground">{Math.round(changeStats.changeRatio * 100)}%</strong>
              </span>
            )}
            <AIScoreBadge
              score={result.ai_score}
              threshold={result.threshold ?? 0.35}
            />
          </div>
        </div>
      )}
    </div>
  );
}
