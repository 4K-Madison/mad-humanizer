import { api } from "./client";

export const detectText = (text, detectors = null) =>
  api.post("/api/detect", { text, detectors });

export const getDetectors = () => api.get("/api/detectors");
