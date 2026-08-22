import fs from "node:fs";
import path from "node:path";

const envPath = path.resolve(process.cwd(), ".env");
const required = ["VITE_SUPABASE_URL", "VITE_SUPABASE_ANON_KEY"];

if (!fs.existsSync(envPath)) {
  console.error("Missing frontend/.env. Copy .env.example and add the public Supabase values.");
  process.exit(1);
}

const values = Object.fromEntries(
  fs.readFileSync(envPath, "utf8")
    .split(/\r?\n/)
    .map((line) => line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/))
    .filter(Boolean)
    .map(([, key, value]) => [key, value.replace(/^['"]|['"]$/g, "")]),
);

const missing = required.filter((key) => !values[key]);
if (missing.length) {
  console.error(`Missing required frontend environment variable(s): ${missing.join(", ")}`);
  process.exit(1);
}

try {
  const url = new URL(values.VITE_SUPABASE_URL);
  if (url.protocol !== "https:" || !url.hostname.endsWith(".supabase.co")) throw new Error();
} catch {
  console.error("VITE_SUPABASE_URL must be https://<project-ref>.supabase.co.");
  process.exit(1);
}

// Legacy anon keys are JWTs. When one is in use, its issuer must belong to the
// same project URL. New `sb_publishable_...` keys are opaque and are validated
// by Supabase when the application connects.
if (values.VITE_SUPABASE_ANON_KEY.split(".").length === 3) {
  try {
    const payload = JSON.parse(Buffer.from(values.VITE_SUPABASE_ANON_KEY.split(".")[1], "base64url").toString("utf8"));
    if (payload.iss && payload.iss.replace(/\/$/, "") !== values.VITE_SUPABASE_URL.replace(/\/$/, "")) {
      console.error("VITE_SUPABASE_ANON_KEY belongs to a different Supabase project than VITE_SUPABASE_URL.");
      process.exit(1);
    }
  } catch {
    console.error("VITE_SUPABASE_ANON_KEY is not a readable Supabase JWT.");
    process.exit(1);
  }
}

console.log("Frontend auth configuration has the required public Supabase values.");

if (process.argv.includes("--remote")) {
  try {
    const response = await fetch(`${values.VITE_SUPABASE_URL.replace(/\/$/, "")}/auth/v1/settings`, {
      headers: { apikey: values.VITE_SUPABASE_ANON_KEY },
    });
    if (!response.ok) {
      console.error(`Supabase Auth settings request failed (HTTP ${response.status}).`);
      process.exit(1);
    }
    console.log("Supabase Auth endpoint accepted the configured public key.");
  } catch {
    console.error("Could not reach the configured Supabase Auth endpoint.");
    process.exit(1);
  }
}
