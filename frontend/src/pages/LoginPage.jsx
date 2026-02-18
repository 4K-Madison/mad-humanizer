import { Link, Navigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import GoogleLoginButton from "@/components/auth/GoogleLoginButton";
import { Loader2, Zap, ArrowLeft } from "lucide-react";

export default function LoginPage() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-badger" />
      </div>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Top accent stripe */}
      <div className="h-1 w-full bg-gradient-to-r from-badger-dark via-badger to-badger-light" />

      <div className="px-6 pt-6">
        <Link
          to="/"
          className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-badger-50 hover:text-badger"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to home
        </Link>
      </div>

      <div className="flex flex-1 items-center justify-center px-6">
        <div className="w-full max-w-sm space-y-8">
          {/* Logo */}
          <div className="flex flex-col items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-badger text-white shadow-lg shadow-badger/25">
              <Zap className="h-7 w-7" />
            </div>
            <div className="text-center">
              <h1 className="font-display text-2xl font-extrabold tracking-tight text-foreground">
                MAD<span className="text-badger">-</span>HUMANIZER
              </h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Sign in to transform your AI-generated text
              </p>
            </div>
          </div>

          {/* Login card */}
          <div className="rounded-2xl border border-border/60 bg-white p-8 shadow-sm">
            <div className="space-y-6">
              <div className="space-y-2 text-center">
                <h2 className="font-display text-lg font-bold text-foreground">
                  Welcome back
                </h2>
                <p className="text-sm text-muted-foreground">
                  Choose how you'd like to sign in
                </p>
              </div>

              <GoogleLoginButton />

              {/* Divider for future email+password */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border/60" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-3 text-muted-foreground">
                    More options coming soon
                  </span>
                </div>
              </div>

              <p className="text-center text-xs text-muted-foreground">
                Email &amp; password login will be available soon.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
