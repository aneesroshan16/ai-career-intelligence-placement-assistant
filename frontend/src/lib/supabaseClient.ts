import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string;

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);

if (!isSupabaseConfigured) {
  // eslint-disable-next-line no-console
  console.warn(
    "VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY are not set. " +
      "Auth will not work until these are configured in frontend/.env"
  );
}

// createClient() throws synchronously if the URL is falsy/invalid, which would
// crash the whole app at import time (white screen) before any UI can render.
// Fall back to a harmless placeholder URL so the app still loads; auth calls
// will simply fail until real credentials are set.
export const supabase = createClient(
  isSupabaseConfigured ? supabaseUrl : "https://placeholder.supabase.co",
  isSupabaseConfigured ? supabaseAnonKey : "placeholder-anon-key"
);

export async function signUpWithEmail(email: string, password: string, fullName: string) {
  return supabase.auth.signUp({
    email,
    password,
    options: { data: { full_name: fullName } },
  });
}

export async function signInWithEmail(email: string, password: string) {
  return supabase.auth.signInWithPassword({ email, password });
}

export async function signInWithGoogle() {
  return supabase.auth.signInWithOAuth({
    provider: "google",
    options: { redirectTo: `${window.location.origin}/dashboard` },
  });
}

export async function signOut() {
  if (!isSupabaseConfigured) {
    clearStoredDevToken();
    return { error: null };
  }
  return supabase.auth.signOut();
}

export async function getAccessToken(): Promise<string | null> {
  if (!isSupabaseConfigured) {
    return getStoredDevToken();
  }
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}

// --- Dev-mode auth (AUTH_MODE=dev on the backend, no Supabase project set up) ---
// Backed by POST /auth/dev-token (see backend/app/modules/auth/router.py).
// Used only when VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY are unset.

const DEV_TOKEN_KEY = "career_intel_dev_token";
export const DEV_AUTH_CHANGED_EVENT = "career-intel-dev-auth-changed";

export function getStoredDevToken(): string | null {
  return localStorage.getItem(DEV_TOKEN_KEY);
}

export function setStoredDevToken(token: string): void {
  localStorage.setItem(DEV_TOKEN_KEY, token);
  window.dispatchEvent(new Event(DEV_AUTH_CHANGED_EVENT));
}

export function clearStoredDevToken(): void {
  localStorage.removeItem(DEV_TOKEN_KEY);
  window.dispatchEvent(new Event(DEV_AUTH_CHANGED_EVENT));
}

/** Stable per-browser dev user id so the same "account" persists across reloads. */
export function getOrCreateDevUserId(): string {
  const KEY = "career_intel_dev_user_id";
  let id = localStorage.getItem(KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(KEY, id);
  }
  return id;
}