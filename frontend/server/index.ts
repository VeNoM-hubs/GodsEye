import "dotenv/config";
import express from "express";
import cors from "cors";
import { handleDemo } from "./routes/demo";
import { createGodsEyeProxyRouter } from "./routes/godseye-proxy";

const API_URL = process.env.GODSEYE_API_URL || "http://localhost:8000";

export function createServer() {
  const app = express();

  // Middleware
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Example API routes
  app.get("/api/ping", (_req, res) => {
    const ping = process.env.PING_MESSAGE ?? "ping";
    res.json({ message: ping });
  });

  app.get("/api/demo", handleDemo);

  // GodsEye proxy routes
  app.use(createGodsEyeProxyRouter());

  // Health check endpoint for GodsEye backend
  app.get("/api/godseye/health", async (_req, res) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      const response = await fetch(`${API_URL}/health`, {
        method: "GET",
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (response.ok) {
        res.status(200).json({ status: "healthy", backend: API_URL });
      } else {
        res.status(503).json({ status: "unhealthy", backend: API_URL });
      }
    } catch (error) {
      console.error("[Health Check] Failed to reach GodsEye backend:", error);
      res.status(503).json({
        status: "unreachable",
        backend: API_URL,
        error: "Could not connect to GodsEye backend",
      });
    }
  });

  return app;
}
