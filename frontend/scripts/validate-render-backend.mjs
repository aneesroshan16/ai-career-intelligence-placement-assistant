const frontendOrigin = "https://frontend-eight-omega-61.vercel.app";

async function request(url, options = {}) {
  const response = await fetch(url, { redirect: "follow", ...options });
  return response;
}

const page = await request(frontendOrigin);
if (!page.ok) throw new Error(`Production frontend request failed (HTTP ${page.status}).`);

const html = await page.text();
const scriptPath = html.match(/src="([^"?]+\.js)"/)?.[1];
if (!scriptPath) throw new Error("Could not find the deployed frontend JavaScript bundle.");

const bundle = await (await request(new URL(scriptPath, frontendOrigin))).text();
const apiBase = bundle.match(/https:\/\/[^"'\s]+\.onrender\.com\/api\/v1/)?.[0];
if (!apiBase) throw new Error("No Render /api/v1 base URL is embedded in the deployed frontend.");

const backendOrigin = apiBase.replace(/\/api\/v1$/, "");
const health = await request(`${backendOrigin}/health`, { headers: { Origin: frontendOrigin } });
let healthJson = false;
try {
  const data = await health.clone().json();
  healthJson = typeof data === "object" && data !== null;
} catch {
  // The status check below reports a non-JSON health response precisely.
}

const apiRoute = `${apiBase}/auth/session`;
const api = await request(apiRoute, { headers: { Origin: frontendOrigin } });
const preflight = await request(apiRoute, {
  method: "OPTIONS",
  headers: {
    Origin: frontendOrigin,
    "Access-Control-Request-Method": "GET",
    "Access-Control-Request-Headers": "authorization",
  },
});

const corsAllowed = preflight.headers.get("access-control-allow-origin") === frontendOrigin;
console.log(`RENDER_HEALTH_HTTP=${health.status}`);
console.log(`RENDER_HEALTH_JSON=${healthJson}`);
console.log(`RENDER_AUTH_SESSION_HTTP=${api.status}`);
console.log(`RENDER_CORS_ALLOWS_PRODUCTION_ORIGIN=${corsAllowed}`);

if (health.status !== 200 || !healthJson || api.status !== 401 || !corsAllowed) process.exit(1);
