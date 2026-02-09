import { useState } from "react";
import { detectText } from "@/api/detect";

export function useDetect() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const detect = async (text, detectors = null) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await detectText(text, detectors);
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

  return { result, isLoading, error, detect, reset };
}
