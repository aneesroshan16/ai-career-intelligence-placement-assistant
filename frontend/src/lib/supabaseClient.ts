import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string;
const authCallbackUrl = `${window.location.origin}/auth/callback`;

function getSupabaseConfigurationError(): string | null {
  if (!supabaseUrl || !supabaseAnonKey) {
    return "VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must both be configured.";
  }

  try {
    const url = new URL(supabaseUrl);
    if (url.protocol !== "https:" || !url.hostname.endsWith(".supabase.co")) {
      return "VITE_SUPABASE_URL must be the HTTPS project URL from Supabase (https://<project-ref>.supabase.co).";
    }
  } catch {
    return "VITE_SUPABASE_URL must be a valid HTTPS Supabase project URL.";
  }

  return null;
}

export const supabaseConfigurationError = getSupabaseConfigurationError();
export const isSupabaseConfigured = supabaseConfigurationError === null;

if (!isSupabaseConfigured) {
  console.error(
    "VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY are not set. " +
      `Auth will not work until they are corrected. ${supabaseConfigurationError}`
  );
}

export const supabase = createClient(
  supabaseUrl || "https://placeholder.supabase.co",
  supabaseAnonKey || "placeholder-anon-key"
);

/** Converts browser/network failures into a message that a student can act on. */
export function authErrorMessage(error: unknown): string {
  if (error instanceof TypeError && /fetch|network/i.test(error.message)) {
    return "Unable to reach Supabase. Check your internet connection and verify VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY, then restart the frontend server.";
  }
  if (error instanceof Error) {
    const message = error.message.toLowerCase();
    if (message.includes("invalid login credentials")) return "Incorrect email or password.";
    if (message.includes("email not confirmed")) return "Please confirm your email before signing in.";
    if (message.includes("user already registered")) return "An account already exists for this email. Try signing in instead.";
    if (message.includes("redirect") || message.includes("callback")) return "This sign-in redirect is not allowed. Please contact support.";
    return error.message;
  }
  return "Authentication could not be completed. Please try again.";
}

function requireSupabaseConfiguration() {
  if (!isSupabaseConfigured) {
    throw new Error(supabaseConfigurationError ?? "Supabase is not configured.");
  }
}

export async function signUpWithEmail(email: string, password: string, fullName: string) {
  requireSupabaseConfiguration();
  return supabase.auth.signUp({
    email,
    password,
    options: {
      data: { full_name: fullName },
      // Supabase must allow this URL in Authentication > URL Configuration.
      emailRedirectTo: authCallbackUrl,
    },
  });
}

export async function signInWithEmail(email: string, password: string) {
  requireSupabaseConfiguration();
  return supabase.auth.signInWithPassword({ email, password });
}

export async function signInWithGoogle() {
  requireSupabaseConfiguration();
  return supabase.auth.signInWithOAuth({
    provider: "google",
    // OAuth and email confirmation both return here so the SDK can exchange
    // the callback code before protected routes request the backend profile.
    options: { redirectTo: authCallbackUrl },
  });
}

export async function signOut() {
  return supabase.auth.signOut();
}

export async function getAccessToken(): Promise<string | null> {
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}
