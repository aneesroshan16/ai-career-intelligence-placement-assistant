import fs from "node:fs";
import { createClient } from "@supabase/supabase-js";

const values = Object.fromEntries(
  fs.readFileSync(".env", "utf8")
    .split(/\r?\n/)
    .map((line) => line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/))
    .filter(Boolean)
    .map(([, key, value]) => [key, value.replace(/^['"]|['"]$/g, "")]),
);

const client = createClient(values.VITE_SUPABASE_URL, values.VITE_SUPABASE_ANON_KEY, {
  auth: { persistSession: false, autoRefreshToken: false },
});
const redirectTo = process.env.AUTH_CALLBACK_URL || "http://localhost:5173/auth/callback";

const { data, error } = await client.auth.signInWithOAuth({
  provider: "google",
  options: {
    redirectTo,
    skipBrowserRedirect: true,
  },
});

if (error || !data.url) {
  console.error("Google OAuth could not be initialized for the local callback URL.");
  process.exit(1);
}

console.log("Google OAuth is enabled and accepts the requested callback URL.");
