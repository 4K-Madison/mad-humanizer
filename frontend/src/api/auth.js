import { api } from "./client";

export const googleLogin = (code, codeVerifier) =>
  api.post("/api/auth/google/login", { code, code_verifier: codeVerifier });

export const getMe = () => api.get("/api/auth/me");

export const logout = () => api.post("/api/auth/logout", {});

export const emailSignup = (email, password, name) =>
  api.post("/api/auth/email/signup", { email, password, name });

export const verifyEmailCode = (email, code) =>
  api.post("/api/auth/email/verify", { email, code });

export const emailLogin = (email, password) =>
  api.post("/api/auth/email/login", { email, password });

export const resendVerificationCode = (email) =>
  api.post("/api/auth/email/resend", { email });

export const linkGoogleAccount = (code, codeVerifier, password) =>
  api.post("/api/auth/link/google", { code, code_verifier: codeVerifier, password });
