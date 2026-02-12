import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X, Zap, ScanSearch } from "lucide-react";

const navLinks = [
  { to: "/", label: "Humanizer", icon: Zap },
  { to: "/detector", label: "Detector", icon: ScanSearch },
];

export default function Header() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Top accent stripe */}
      <div className="h-1 w-full bg-gradient-to-r from-badger-dark via-badger to-badger-light" />

      <header className="sticky top-0 z-50 w-full border-b border-border/60 bg-white/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          {/* Logo */}
          <Link to="/" className="group flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-badger text-white shadow-md shadow-badger/25 transition-transform group-hover:scale-105">
              <span className="font-display text-sm font-black leading-none tracking-tight">M</span>
            </div>
            <div className="flex flex-col">
              <span className="font-display text-lg font-extrabold tracking-tight text-foreground">
                MAD<span className="text-badger">-</span>HUMANIZER
              </span>
              <span className="hidden text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground sm:block">
                AI Text Transformer
              </span>
            </div>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-1 md:flex">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.to;
              const Icon = link.icon;
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`
                    relative flex items-center gap-2 rounded-lg px-4 py-2 font-display text-sm font-semibold transition-all
                    ${isActive
                      ? "bg-badger text-white shadow-md shadow-badger/20"
                      : "text-muted-foreground hover:bg-badger-50 hover:text-badger"
                    }
                  `}
                >
                  <Icon className="h-4 w-4" />
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Mobile toggle */}
          <button
            className="flex h-10 w-10 items-center justify-center rounded-lg text-foreground transition-colors hover:bg-badger-50 md:hidden"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile nav */}
        {mobileOpen && (
          <nav className="border-t border-border/60 px-6 pb-4 pt-3 md:hidden">
            <div className="flex flex-col gap-1">
              {navLinks.map((link) => {
                const isActive = location.pathname === link.to;
                const Icon = link.icon;
                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    onClick={() => setMobileOpen(false)}
                    className={`
                      flex items-center gap-3 rounded-lg px-4 py-3 font-display text-sm font-semibold transition-all
                      ${isActive
                        ? "bg-badger text-white"
                        : "text-muted-foreground hover:bg-badger-50 hover:text-badger"
                      }
                    `}
                  >
                    <Icon className="h-4 w-4" />
                    {link.label}
                  </Link>
                );
              })}
            </div>
          </nav>
        )}
      </header>
    </>
  );
}
