import fs from "fs";
import path from "path";
import dotenv from "dotenv";

let envLoaded = false;

function loadEnvFiles() {
  if (envLoaded) return;

  const rootDir = process.cwd();
  for (const fileName of [".env.local", ".env"]) {
    const filePath = path.resolve(rootDir, fileName);
    if (fs.existsSync(filePath)) {
      dotenv.config({ path: filePath, override: false });
    }
  }

  envLoaded = true;
}

export function getBackendApiUrl(): string {
  loadEnvFiles();
  return (
    process.env.GODSEYE_API_URL ||
    process.env.VITE_API_BASE_URL ||
    "http://localhost:8000"
  );
}
