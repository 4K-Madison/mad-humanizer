export default function Footer() {
  return (
    <footer className="border-t py-6 text-center text-sm text-muted-foreground">
      <div className="mx-auto max-w-5xl px-4">
        MAD-HUMANIZER &copy; {new Date().getFullYear()}
      </div>
    </footer>
  );
}
