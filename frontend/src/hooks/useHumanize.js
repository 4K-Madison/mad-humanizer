import { useState } from "react";
import { humanizeText } from "@/api/humanize";

export function useHumanize() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const humanize = async (text, options = {}) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await humanizeText(text, options);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  return { result, isLoading, error, humanize, reset };
}
