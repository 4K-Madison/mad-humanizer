export default function VerificationCodeInput({ value, onChange, disabled }) {
  return (
    <input
      type="text"
      inputMode="numeric"
      pattern="[0-9]*"
      maxLength={6}
      value={value}
      onChange={(e) => onChange(e.target.value.replace(/\D/g, ""))}
      placeholder="000000"
      disabled={disabled}
      className="w-full rounded-xl border border-border/60 bg-white px-4 py-3 text-center text-2xl font-mono tracking-[0.5em] text-foreground placeholder:text-muted-foreground/40 focus:border-badger focus:outline-none focus:ring-2 focus:ring-badger/20 disabled:opacity-50"
    />
  );
}
