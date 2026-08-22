import fs from "node:fs";
import path from "node:path";

const frontendEnv = path.resolve(process.cwd(), ".env");
const backendEnv = path.resolve(process.cwd(), "..", "backend", ".env");
const vercelEnv = path.resolve(process.cwd(), ".env.vercel");

function readValue(file, key) {
  const match = fs.readFileSync(file, "utf8").match(new RegExp(`^\\s*${key}\\s*=\\s*(.*)\\s*$`, "m"));
  return match?.[1]?.trim().replace(/^['"]|['"]$/g, "") ?? "";
}

if (!fs.existsSync(frontendEnv) || !fs.existsSync(backendEnv)) {
  console.error("Both frontend/.env and backend/.env are required.");
  process.exit(1);
}

const backendUrl = readValue(backendEnv, "SUPABASE_URL");
if (!/^https:\/\/[a-z0-9-]+\.supabase\.co\/?$/.test(backendUrl)) {
  console.error("backend/.env does not contain a valid SUPABASE_URL; no change was made.");
  process.exit(1);
}

const source = fs.readFileSync(frontendEnv, "utf8");
const replacement = `VITE_SUPABASE_URL=${backendUrl}`;
const next = /^\s*VITE_SUPABASE_URL\s*=.*$/m.test(source)
  ? source.replace(/^\s*VITE_SUPABASE_URL\s*=.*$/m, replacement)
  : `${source.replace(/\s*$/, "")}\n${replacement}\n`;

let finalEnv = next;

// `vercel env pull` creates .env.vercel. Reuse its public anon key only when
// both its URL and JWT issuer prove it belongs to the backend's project.
if (fs.existsSync(vercelEnv)) {
  const vercelUrl = readValue(vercelEnv, "VITE_SUPABASE_URL").replace(/\/$/, "");
  const vercelAnonKey = readValue(vercelEnv, "VITE_SUPABASE_ANON_KEY");
  let issuer = "";
  try {
    issuer = JSON.parse(Buffer.from(vercelAnonKey.split(".")[1] ?? "", "base64url").toString("utf8")).iss?.replace(/\/$/, "") ?? "";
  } catch {
    // New opaque publishable keys cannot be verified locally, so leave them untouched.
  }

  if (vercelUrl === backendUrl.replace(/\/$/, "") && issuer === vercelUrl) {
    finalEnv = finalEnv.replace(/^\s*VITE_SUPABASE_ANON_KEY\s*=.*$/m, `VITE_SUPABASE_ANON_KEY=${vercelAnonKey}`);
    console.log("Synchronized the matching public anon key from frontend/.env.vercel.");
  }
}

fs.writeFileSync(frontendEnv, finalEnv);
console.log("Synchronized frontend VITE_SUPABASE_URL with backend SUPABASE_URL.");
