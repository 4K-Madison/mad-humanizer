import { useState, useEffect } from "react";
import { useDetect } from "@/hooks/useDetect";
import { getDetectors } from "@/api/detect";
import DetectorForm from "@/components/detector/DetectorForm";
import DetectorSelector from "@/components/detector/DetectorSelector";
import DetectorResults from "@/components/detector/DetectorResults";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import ErrorAlert from "@/components/shared/ErrorAlert";

export default function DetectorPage() {
  const [inputText, setInputText] = useState("");
  const [detectors, setDetectors] = useState([]);
  const [selectedDetectors, setSelectedDetectors] = useState([]);
  const { result, isLoading, error, detect, reset } = useDetect();

  useEffect(() => {
    getDetectors()
      .then((data) => {
        setDetectors(data.detectors);
        setSelectedDetectors(
          data.detectors.filter((d) => d.available).map((d) => d.name)
        );
      })
      .catch(() => {
        // Detectors list will be empty; user can still submit without selection
      });
  }, []);

  const handleSubmit = (text) => {
    const selected = selectedDetectors.length > 0 ? selectedDetectors : null;
    detect(text, selected);
  };

  const handleInputChange = (text) => {
    setInputText(text);
    if (result) reset();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">AI Detector</h1>
        <p className="mt-1 text-muted-foreground">
          Run your text against multiple AI detection services and see per-detector
          scores.
        </p>
      </div>

      <DetectorForm
        value={inputText}
        onChange={handleInputChange}
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />

      <DetectorSelector
        detectors={detectors}
        selected={selectedDetectors}
        onChange={setSelectedDetectors}
      />

      <ErrorAlert message={error} onDismiss={reset} />

      {isLoading && <LoadingSpinner message="Running detection..." />}

      {result && (
        <DetectorResults
          results={result.results}
          processingTime={result.processing_time_ms}
        />
      )}
    </div>
  );
}
