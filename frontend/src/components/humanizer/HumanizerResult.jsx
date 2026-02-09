import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import CopyButton from "@/components/shared/CopyButton";

export default function HumanizerResult({ result }) {
  if (!result) return null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="text-base font-semibold">Humanized Output</CardTitle>
        <CopyButton text={result.humanized_text} />
      </CardHeader>
      <Separator />
      <CardContent className="pt-4">
        <Textarea
          value={result.humanized_text}
          readOnly
          rows={8}
          className="resize-y"
        />
        <div className="mt-3 flex flex-wrap gap-4 text-sm text-muted-foreground">
          <span>Input: {result.input_length} chars</span>
          <span>Output: {result.output_length} chars</span>
          <span>Time: {(result.processing_time_ms / 1000).toFixed(1)}s</span>
        </div>
      </CardContent>
    </Card>
  );
}
