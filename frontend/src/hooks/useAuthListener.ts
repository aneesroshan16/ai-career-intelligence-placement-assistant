import { useEffect } from "react";
import type { Session, User as SupabaseUser } from "@supabase/supabase-js";
import { isSupabaseConfigured, supabase } from "@/lib/supabaseClient";
import { getMe } from "@/lib/api/resumeModules";
import { useAuthStore } from "@/store/authStore";
import type { User } from "@/types";

function userFromSession(user: SupabaseUser): User {
  const requestedRole = user.app_metadata?.role;
  const role = requestedRole === "admin" || requestedRole === "placement_officer" ? requestedRole : "student";

  return {
    id: user.id,
    email: user.email ?? "",
    full_name: user.user_metadata?.full_name ?? user.user_metadata?.name ?? user.email?.split("@")[0] ?? "Student",
    avatar_url: user.user_metadata?.avatar_url ?? user.user_metadata?.picture ?? null,
    role,
    profile: null,
  };
}

export function useAuthListener() {
  const setUser = useAuthStore((s) => s.setUser);
  const setLoading = useAuthStore((s) => s.setLoading);
  const setAuthError = useAuthStore((s) => s.setAuthError);

  useEffect(() => {
    let mounted = true;
    let latestSync = 0;

    async function syncUser(sessionFromEvent?: Session | null) {
      const syncId = ++latestSync;
      setLoading(true);
      if (mounted) setAuthError(null);
      try {
        if (!isSupabaseConfigured) {
          if (mounted && syncId === latestSync) setUser(null);
          return;
        }
        
        const session = sessionFromEvent === undefined
          ? (await supabase.auth.getSession()).data.session
          : sessionFromEvent;
        if (!session) {
          if (mounted && syncId === latestSync) setUser(null);
          return;
        }

        // Supabase is the source of truth for whether the user is signed in.
        // The API profile enriches UI data, but a temporary API/CORS/database
        // failure must never discard a valid browser session or redirect to login.
        if (mounted && syncId === latestSync) setUser(userFromSession(session.user));
        if (mounted && syncId === latestSync) setLoading(false);

        try {
          const profile = await getMe();
          if (mounted && syncId === latestSync) setUser(profile);
        } catch (error) {
          if (mounted && syncId === latestSync) {
            const detail = error instanceof Error ? error.message : "The backend profile service is unavailable.";
            setAuthError(`You are signed in, but your profile could not be loaded: ${detail}`);
          }
        }
      } catch (error) {
        // A delayed initial getSession call can finish after an OAuth
        // SIGNED_IN event. Never let that stale failure clear a fresh session.
        if (mounted && syncId === latestSync) {
          setUser(null);
          const msg = error instanceof Error ? error.message : "Failed to load user profile. Is the backend server running?";
          setAuthError(msg);
        }
      } finally {
        if (mounted && syncId === latestSync) setLoading(false);
      }
    }

    syncUser();

    if (!isSupabaseConfigured) return;

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, session) => {
      void syncUser(session);
    });

    return () => {
      mounted = false;
      subscription.subscription.unsubscribe();
    };
  }, [setUser, setLoading, setAuthError]);
}
