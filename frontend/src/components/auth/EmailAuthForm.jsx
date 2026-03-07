import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import {
  emailSignup,
  verifyEmailCode,
  emailLogin,
  resendVerificationCode,
} from "@/api/auth";
import VerificationCodeInput from "./VerificationCodeInput";

export default function EmailAuthForm() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState("login"); // "login" | "signup" | "verify"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await emailLogin(email, password);
      login(data.user);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await emailSignup(email, password, name || undefined);
      setMode("verify");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await verifyEmailCode(email, code);
      login(data.user);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setError("");
    setLoading(true);
    try {
      await resendVerificationCode(email);
      setCode("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    "w-full rounded-xl border border-border/60 bg-white px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/60 focus:border-badger focus:outline-none focus:ring-2 focus:ring-badger/20 disabled:opacity-50";

  if (mode === "verify") {
    return (
      <form onSubmit={handleVerify} className="space-y-4">
        <div className="space-y-1 text-center">
          <p className="text-sm font-medium text-foreground">
            Check your email
          </p>
          <p className="text-xs text-muted-foreground">
            We sent a 6-digit code to <span className="font-medium">{email}</span>
          </p>
        </div>

        <VerificationCodeInput value={code} onChange={setCode} disabled={loading} />

        {error && (
          <p className="text-center text-xs text-red-500">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading || code.length !== 6}
          className="w-full rounded-xl bg-badger px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-badger-dark disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="mx-auto h-4 w-4 animate-spin" />
          ) : (
            "Verify & Create Account"
          )}
        </button>

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <button
            type="button"
            onClick={() => setMode("signup")}
            className="hover:text-badger"
          >
            ← Back
          </button>
          <button
            type="button"
            onClick={handleResend}
            disabled={loading}
            className="hover:text-badger disabled:opacity-50"
          >
            Resend code
          </button>
        </div>
      </form>
    );
  }

  if (mode === "signup") {
    return (
      <form onSubmit={handleSignup} className="space-y-3">
        <input
          type="text"
          placeholder="Name (optional)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          disabled={loading}
          className={inputClass}
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={loading}
          className={inputClass}
        />
        <input
          type="password"
          placeholder="Password (min 8 characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          disabled={loading}
          className={inputClass}
        />

        {error && (
          <p className="text-xs text-red-500">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl bg-badger px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-badger-dark disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="mx-auto h-4 w-4 animate-spin" />
          ) : (
            "Sign Up"
          )}
        </button>

        <p className="text-center text-xs text-muted-foreground">
          Already have an account?{" "}
          <button
            type="button"
            onClick={() => { setMode("login"); setError(""); }}
            className="font-medium text-badger hover:underline"
          >
            Sign In
          </button>
        </p>
      </form>
    );
  }

  // Login mode (default)
  return (
    <form onSubmit={handleLogin} className="space-y-3">
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        disabled={loading}
        className={inputClass}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        disabled={loading}
        className={inputClass}
      />

      {error && (
        <p className="text-xs text-red-500">{error}</p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-xl bg-badger px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-badger-dark disabled:opacity-50"
      >
        {loading ? (
          <Loader2 className="mx-auto h-4 w-4 animate-spin" />
        ) : (
          "Sign In"
        )}
      </button>

      <p className="text-center text-xs text-muted-foreground">
        Don&apos;t have an account?{" "}
        <button
          type="button"
          onClick={() => { setMode("signup"); setError(""); }}
          className="font-medium text-badger hover:underline"
        >
          Sign Up
        </button>
      </p>
    </form>
  );
}
