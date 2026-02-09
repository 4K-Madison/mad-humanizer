import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

export default function DetectorSelector({ detectors, selected, onChange }) {
  if (!detectors || detectors.length === 0) return null;

  const handleToggle = (name) => {
    if (selected.includes(name)) {
      onChange(selected.filter((d) => d !== name));
    } else {
      onChange([...selected, name]);
    }
  };

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium">Select detectors:</p>
      <div className="flex flex-wrap gap-4">
        {detectors.map((detector) => (
          <div key={detector.name} className="flex items-center gap-2">
            <Checkbox
              id={`detector-${detector.name}`}
              checked={selected.includes(detector.name)}
              onCheckedChange={() => handleToggle(detector.name)}
              disabled={!detector.available}
            />
            <Label
              htmlFor={`detector-${detector.name}`}
              className={!detector.available ? "text-muted-foreground line-through" : ""}
            >
              {detector.display_name}
            </Label>
          </div>
        ))}
      </div>
    </div>
  );
}
