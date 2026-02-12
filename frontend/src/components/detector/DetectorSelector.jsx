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
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <div className="h-2 w-2 rounded-full bg-badger" />
        <span className="font-display text-sm font-bold uppercase tracking-wide text-foreground">
          Detectors
        </span>
        <span className="text-xs text-muted-foreground">
          ({selected.length} selected)
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {detectors.map((detector) => {
          const isSelected = selected.includes(detector.name);
          const isAvailable = detector.available;

          return (
            <button
              key={detector.name}
              type="button"
              disabled={!isAvailable}
              onClick={() => handleToggle(detector.name)}
              className={`
                rounded-lg border px-4 py-2 font-display text-sm font-semibold transition-all
                ${!isAvailable
                  ? "cursor-not-allowed border-border/40 bg-muted/50 text-muted-foreground/40 line-through"
                  : isSelected
                    ? "border-badger bg-badger text-white shadow-sm shadow-badger/20"
                    : "border-border/80 bg-white text-foreground hover:border-badger/40 hover:bg-badger-50"
                }
              `}
            >
              {detector.display_name}
            </button>
          );
        })}
      </div>
    </div>
  );
}
