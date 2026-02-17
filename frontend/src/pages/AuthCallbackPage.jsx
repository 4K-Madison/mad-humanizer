import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { googleLogin } from "@/api/auth";
import { useAuth } from "@/context/AuthContext";
import { Loader2, AlertCircle } from "lucide-react";

export default function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState(null);
  const calledRef = useRef(false);

  useEffect(() => {
    // Guard against React strict mode double-firing (auth codes are single-use)
    if (calledRef.current) return;
    calledRef.current = true;

    const code = searchParams.get("code");
    const errorParam = searchParams.get("error");

    if (errorParam) {
      setError("Google login was cancelled or failed.");
      return;
    }

    if (!code) {
      setError("No authorization code received.");
      return;
    }

    const codeVerifier = sessionStorage.getItem("pkce_code_verifier");
    if (!codeVerifier) {
      setError("PKCE verifier not found. Please try logging in again.");
      return;
    }

    googleLogin(code, codeVerifier)
      .then((data) => {
        sessionStorage.removeItem("pkce_code_verifier");
        login(data.user);
        navigate("/", { replace: true });
      })
      .catch(() => {
        setError("Login failed. Please try again.");
      });
  }, [searchParams, navigate, login]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-6">
        <div className="w-full max-w-sm space-y-6 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50 text-red-500">
            <AlertCircle className="h-7 w-7" />
          </div>
          <div>
            <h2 className="font-display text-lg font-bold text-foreground">
              Sign in failed
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">{error}</p>
          </div>
          <a
            href="/login"
            className="inline-flex items-center justify-center rounded-xl bg-badger px-6 py-3 font-display text-sm font-semibold text-white shadow-md shadow-badger/20 transition-all hover:bg-badger-dark active:scale-[0.98]"
          >
            Back to login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background">
      <Loader2 className="h-8 w-8 animate-spin text-badger" />
      <p className="font-display text-sm font-medium text-muted-foreground">
        Signing you in...
      </p>
    </div>
  );
}
