import { useState, useEffect } from "react";
import { useDetect } from "@/hooks/useDetect";
import { getDetectors } from "@/api/detect";
import DetectorForm from "@/components/detector/DetectorForm";
import DetectorSelector from "@/components/detector/DetectorSelector";
import DetectorResults from "@/components/detector/DetectorResults";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import ErrorAlert from "@/components/shared/ErrorAlert";
import { ScanSearch } from "lucide-react";

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
      .catch(() => {});
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
    <div className="space-y-8">
      {/* Page header */}
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-badger/10">
            <ScanSearch className="h-5 w-5 text-badger" />
          </div>
          <div>
            <h1 className="font-display text-3xl font-extrabold tracking-tight text-foreground">
              AI Detector
            </h1>
          </div>
        </div>
        <p className="max-w-2xl text-base leading-relaxed text-muted-foreground">
          Analyze text against multiple AI detection services. See per-detector confidence scores and identify AI-generated content.
        </p>
      </div>

      {/* Input section */}
      <div>
        <div className="mb-3 flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-badger" />
          <span className="font-display text-sm font-bold uppercase tracking-wide text-foreground">
            Text to Analyze
          </span>
        </div>
        <DetectorForm
          value={inputText}
          onChange={handleInputChange}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
      </div>

      {/* Detector selector */}
      <DetectorSelector
        detectors={detectors}
        selected={selectedDetectors}
        onChange={setSelectedDetectors}
      />

      <ErrorAlert message={error} onDismiss={reset} />

      {isLoading && <LoadingSpinner message="Running detection across all selected services..." />}

      {result && (
        <DetectorResults
          results={result.results}
          processingTime={result.processing_time_ms}
        />
      )}
    </div>
  );
}
