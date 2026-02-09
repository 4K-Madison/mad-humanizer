import { api } from "./client";

export const humanizeText = (text, options = {}) =>
  api.post("/api/humanize", { text, options });
