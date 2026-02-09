import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";

const navLinks = [
  { to: "/", label: "Humanizer" },
  { to: "/detector", label: "Detector" },
];

export default function Header() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
        <Link to="/" className="text-lg font-bold tracking-tight">
          MAD-HUMANIZER
        </Link>

        {/* Desktop nav */}
        <nav className="hidden gap-1 md:flex">
          {navLinks.map((link) => (
            <Button
              key={link.to}
              variant={location.pathname === link.to ? "secondary" : "ghost"}
              size="sm"
              asChild
            >
              <Link to={link.to}>{link.label}</Link>
            </Button>
          ))}
        </nav>

        {/* Mobile toggle */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      </div>

      {/* Mobile nav */}
      {mobileOpen && (
        <nav className="flex flex-col gap-1 border-t px-4 pb-3 pt-2 md:hidden">
          {navLinks.map((link) => (
            <Button
              key={link.to}
              variant={location.pathname === link.to ? "secondary" : "ghost"}
              size="sm"
              className="justify-start"
              asChild
              onClick={() => setMobileOpen(false)}
            >
              <Link to={link.to}>{link.label}</Link>
            </Button>
          ))}
        </nav>
      )}
    </header>
  );
}
