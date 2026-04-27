import express, { Request, Response, Router } from "express";

const API_URL = process.env.GODSEYE_API_URL || "http://localhost:8000";

export function createGodsEyeProxyRouter(): Router {
  const router = express.Router();

  // Proxy GET requests to /api/dashboard/*
  router.get("/api/dashboard/:endpoint", async (req: Request, res: Response) => {
    try {
      const endpoint = req.params.endpoint;
      const queryString = new URLSearchParams(req.query as Record<string, string>).toString();
      const url = `${API_URL}/api/dashboard/${endpoint}${queryString ? `?${queryString}` : ""}`;

      console.log(`[GodsEye Proxy] GET ${url}`);

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      });

      const data = await response.json();

      res.status(response.status).json(data);
    } catch (error) {
      console.error(`[GodsEye Proxy] Error fetching ${req.path}:`, error);
      res.status(503).json({
        error: "API unreachable",
        message: "Failed to connect to GodsEye backend API",
      });
    }
  });

  // Proxy PATCH requests to /api/dashboard/*
  router.patch("/api/dashboard/:endpoint/:id/:action", async (req: Request, res: Response) => {
    try {
      const endpoint = req.params.endpoint;
      const id = req.params.id;
      const action = req.params.action;
      const url = `${API_URL}/api/dashboard/${endpoint}/${id}/${action}`;

      console.log(`[GodsEye Proxy] PATCH ${url}`);

      const response = await fetch(url, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: req.body ? JSON.stringify(req.body) : undefined,
      });

      const data = await response.json();

      res.status(response.status).json(data);
    } catch (error) {
      console.error(`[GodsEye Proxy] Error patching ${req.path}:`, error);
      res.status(503).json({
        error: "API unreachable",
        message: "Failed to connect to GodsEye backend API",
      });
    }
  });

  return router;
}
