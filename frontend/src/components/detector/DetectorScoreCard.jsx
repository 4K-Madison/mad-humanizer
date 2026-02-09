import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle } from "lucide-react";

function getScoreColor(score) {
  if (score < 0.3) return "text-green-600";
  if (score < 0.7) return "text-yellow-600";
  return "text-red-600";
}

function getScoreBg(score) {
  if (score < 0.3) return "bg-green-50 border-green-200";
  if (score < 0.7) return "bg-yellow-50 border-yellow-200";
  return "bg-red-50 border-red-200";
}

export default function DetectorScoreCard({ result }) {
  if (result.error) {
    return (
      <Card className="border-destructive/50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold">{result.detector}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-sm text-destructive">
            <AlertCircle className="h-4 w-4" />
            <span>{result.error}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const scorePercent = result.score != null ? Math.round(result.score * 100) : null;

  return (
    <Card className={result.score != null ? getScoreBg(result.score) : ""}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">{result.detector}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {scorePercent != null && (
          <p className={`text-3xl font-bold ${getScoreColor(result.score)}`}>
            {scorePercent}%
          </p>
        )}
        {result.label && (
          <Badge variant="secondary">{result.label}</Badge>
        )}
      </CardContent>
    </Card>
  );
}
