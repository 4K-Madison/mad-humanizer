import { useState, useRef, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X, Zap, ScanSearch, LogOut, LogIn, User } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

const navLinks = [
  { to: "/", label: "Humanizer", icon: Zap },
  { to: "/detector", label: "Detector", icon: ScanSearch },
];

export default function Header() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);
  const { user, logout } = useAuth();

  // Close user menu on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

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

          {/* User area (desktop) */}
          <div className="hidden md:block">
            {user ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-badger-50"
                >
                  {user.picture_url ? (
                    <img
                      src={user.picture_url}
                      alt={user.name || user.email}
                      className="h-8 w-8 rounded-full border border-border/60"
                      referrerPolicy="no-referrer"
                    />
                  ) : (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-badger-100 text-badger">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </button>

                {userMenuOpen && (
                  <div className="absolute right-0 top-full z-50 mt-2 w-56 rounded-xl border border-border/60 bg-white py-2 shadow-lg">
                    <div className="border-b border-border/60 px-4 py-3">
                      <p className="truncate font-display text-sm font-semibold text-foreground">
                        {user.name || "User"}
                      </p>
                      <p className="truncate text-xs text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        logout();
                      }}
                      className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-muted-foreground transition-colors hover:bg-badger-50 hover:text-badger"
                    >
                      <LogOut className="h-4 w-4" />
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="flex items-center gap-2 rounded-lg bg-badger px-4 py-2 font-display text-sm font-semibold text-white shadow-md shadow-badger/20 transition-all hover:bg-badger-dark active:scale-[0.98]"
              >
                <LogIn className="h-4 w-4" />
                Sign in
              </Link>
            )}
          </div>

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
              {/* Mobile user info + logout / sign in */}
              <div className="my-2 border-t border-border/60" />
              {user ? (
                <>
                  <div className="flex items-center gap-3 px-4 py-2">
                    {user.picture_url ? (
                      <img
                        src={user.picture_url}
                        alt={user.name || user.email}
                        className="h-8 w-8 rounded-full border border-border/60"
                        referrerPolicy="no-referrer"
                      />
                    ) : (
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-badger-100 text-badger">
                        <User className="h-4 w-4" />
                      </div>
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold text-foreground">
                        {user.name || "User"}
                      </p>
                      <p className="truncate text-xs text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setMobileOpen(false);
                      logout();
                    }}
                    className="flex w-full items-center gap-3 rounded-lg px-4 py-3 font-display text-sm font-semibold text-muted-foreground transition-all hover:bg-red-50 hover:text-red-600"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center gap-3 rounded-lg px-4 py-3 font-display text-sm font-semibold text-badger transition-all hover:bg-badger-50"
                >
                  <LogIn className="h-4 w-4" />
                  Sign in
                </Link>
              )}
            </div>
          </nav>
        )}
      </header>
    </>
  );
}
