import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { googleLogin, linkGoogleAccount } from "@/api/auth";
import { useAuth } from "@/context/AuthContext";
import { Loader2, AlertCircle, Link2 } from "lucide-react";

export default function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState(null);
  const [linkPrompt, setLinkPrompt] = useState(null); // { email }
  const [password, setPassword] = useState("");
  const [linkLoading, setLinkLoading] = useState(false);
  const [linkError, setLinkError] = useState("");
  const calledRef = useRef(false);

  useEffect(() => {
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

    // Check if we're returning from a link flow
    const isLinkMode = sessionStorage.getItem("link_mode") === "true";
    const savedPassword = sessionStorage.getItem("link_password");

    if (isLinkMode && savedPassword) {
      sessionStorage.removeItem("link_mode");
      sessionStorage.removeItem("link_password");
      setLinkLoading(true);

      linkGoogleAccount(code, codeVerifier, savedPassword)
        .then((data) => {
          sessionStorage.removeItem("pkce_code_verifier");
          login(data.user);
          navigate("/", { replace: true });
        })
        .catch((err) => {
          setLinkError(err.message);
          setLinkLoading(false);
          // Show the link prompt again so user can retry
          setLinkPrompt({ email: "" });
        });
      return;
    }

    // Normal Google login flow
    googleLogin(code, codeVerifier)
      .then((data) => {
        sessionStorage.removeItem("pkce_code_verifier");
        login(data.user);
        navigate("/", { replace: true });
      })
      .catch((err) => {
        if (err.data?.code === "EMAIL_ACCOUNT_EXISTS") {
          setLinkPrompt({ email: err.data.email });
        } else {
          setError("Login failed. Please try again.");
        }
      });
  }, [searchParams, navigate, login]);

  const handleLink = async (e) => {
    e.preventDefault();
    setLinkError("");
    setLinkLoading(true);

    // Store password and redirect back to Google OAuth for a fresh code
    sessionStorage.setItem("link_password", password);
    sessionStorage.setItem("link_mode", "true");

    const { generatePKCE } = await import("@/utils/pkce");
    const { codeVerifier, codeChallenge } = await generatePKCE();
    sessionStorage.setItem("pkce_code_verifier", codeVerifier);

    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    const redirectUri = `${window.location.origin}/auth/callback`;
    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: "code",
      scope: "openid email profile",
      access_type: "offline",
      prompt: "consent",
      code_challenge: codeChallenge,
      code_challenge_method: "S256",
    });

    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
  };

  // Account linking prompt
  if (linkPrompt) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-6">
        <div className="w-full max-w-sm space-y-6">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-50 text-amber-500">
            <Link2 className="h-7 w-7" />
          </div>
          <div className="text-center">
            <h2 className="font-display text-lg font-bold text-foreground">
              Account already exists
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {linkPrompt.email && (
                <>
                  <span className="font-medium text-foreground">{linkPrompt.email}</span>{" "}
                  is already registered with email/password.{" "}
                </>
              )}
              Enter your password to link your Google account.
            </p>
          </div>

          <form onSubmit={handleLink} className="space-y-4">
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={linkLoading}
              className="w-full rounded-xl border border-border/60 bg-white px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/60 focus:border-badger focus:outline-none focus:ring-2 focus:ring-badger/20 disabled:opacity-50"
            />

            {linkError && (
              <p className="text-center text-xs text-red-500">{linkError}</p>
            )}

            <button
              type="submit"
              disabled={linkLoading || !password}
              className="w-full rounded-xl bg-badger px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-badger-dark disabled:opacity-50"
            >
              {linkLoading ? (
                <Loader2 className="mx-auto h-4 w-4 animate-spin" />
              ) : (
                "Link Google Account"
              )}
            </button>

            <a
              href="/login"
              className="block text-center text-xs text-muted-foreground hover:text-badger"
            >
              Cancel and go back to login
            </a>
          </form>
        </div>
      </div>
    );
  }

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
        {linkLoading ? "Linking your accounts..." : "Signing you in..."}
      </p>
    </div>
  );
}
