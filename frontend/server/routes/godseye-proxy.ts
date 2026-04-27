import express, { Request, Response, Router } from "express";
import { getBackendApiUrl } from "../backend-url";

const API_URL = getBackendApiUrl();

async function proxyRequest(req: Request, res: Response) {
  try {
    const targetUrl = new URL(req.originalUrl, API_URL);
    const headers: Record<string, string> = {
      Accept: "application/json",
    };

    if (req.method !== "GET" && req.method !== "HEAD") {
      headers["Content-Type"] = "application/json";
    }

    const response = await fetch(targetUrl.toString(), {
      method: req.method,
      headers,
      body: req.method === "GET" || req.method === "HEAD"
        ? undefined
        : (typeof req.body === "string" ? req.body : JSON.stringify(req.body ?? {})),
    });

    const contentType = response.headers.get("content-type") || "";
    const payload = response.status === 204
      ? null
      : contentType.includes("application/json")
        ? await response.json()
        : await response.text();

    console.log(`[GodsEye Proxy] ${req.method} ${targetUrl.toString()}`);

    if (payload === null) {
      res.status(response.status).send();
    } else if (typeof payload === "string") {
      res.status(response.status).send(payload);
    } else {
      res.status(response.status).json(payload);
    }
  } catch (error) {
    console.error(`[GodsEye Proxy] Error fetching ${req.method} ${req.originalUrl}:`, error);
    res.status(503).json({
      error: "API unreachable",
      message: "Failed to connect to GodsEye backend API",
    });
  }
}

export function createGodsEyeProxyRouter(): Router {
  const router = express.Router();

  router.all(/^\/api\/.*$/, proxyRequest);
  router.all(/^\/honeypot\/.*$/, proxyRequest);

  return router;
}
