import { useState } from "react";
import { useHumanize } from "@/hooks/useHumanize";
import HumanizerForm from "@/components/humanizer/HumanizerForm";
import HumanizerResult from "@/components/humanizer/HumanizerResult";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import ErrorAlert from "@/components/shared/ErrorAlert";

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
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">AI Text Humanizer</h1>
        <p className="mt-1 text-muted-foreground">
          Transform AI-generated text into natural, human-sounding content.
        </p>
      </div>

      <HumanizerForm
        value={inputText}
        onChange={handleInputChange}
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />

      <ErrorAlert message={error} onDismiss={reset} />

      {isLoading && <LoadingSpinner message="Humanizing your text..." />}

      <HumanizerResult result={result} />
    </div>
  );
}
