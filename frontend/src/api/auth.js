import { api } from "./client";

export const googleLogin = (code, codeVerifier) =>
  api.post("/api/auth/google/login", { code, code_verifier: codeVerifier });

export const getMe = () => api.get("/api/auth/me");

export const logout = () => api.post("/api/auth/logout", {});
