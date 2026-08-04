import { useEffect } from "react";
import {
  DEV_AUTH_CHANGED_EVENT,
  getStoredDevToken,
  isSupabaseConfigured,
  supabase,
} from "@/lib/supabaseClient";
import { getMe } from "@/lib/api/resumeModules";
import { useAuthStore } from "@/store/authStore";

/**
 * On mount, and whenever the auth state changes, fetches the backend-owned
 * user profile (which lazily provisions the `users` row on first sight —
 * see core/security.py) and syncs it into the auth store.
 *
 * Two identity sources, mutually exclusive:
 *  - Supabase session, when VITE_SUPABASE_URL/ANON_KEY are configured.
 *  - Dev-mode token in localStorage, when they are not (AUTH_MODE=dev
 *    backend flow — see lib/api/authModules.ts).
 */
export function useAuthListener() {
  const setUser = useAuthStore((s) => s.setUser);
  const setLoading = useAuthStore((s) => s.setLoading);

  useEffect(() => {
    let mounted = true;

    async function syncUser() {
      setLoading(true);
      try {
        if (!isSupabaseConfigured) {
          if (!getStoredDevToken()) {
            if (mounted) setUser(null);
            return;
          }
        } else {
          const { data } = await supabase.auth.getSession();
          if (!data.session) {
            if (mounted) setUser(null);
            return;
          }
        }
        const profile = await getMe();
        if (mounted) setUser(profile);
      } catch {
        if (mounted) setUser(null);
      } finally {
        if (mounted) setLoading(false);
      }
    }

    syncUser();

    if (!isSupabaseConfigured) {
      window.addEventListener(DEV_AUTH_CHANGED_EVENT, syncUser);
      return () => {
        mounted = false;
        window.removeEventListener(DEV_AUTH_CHANGED_EVENT, syncUser);
      };
    }

    const { data: subscription } = supabase.auth.onAuthStateChange(() => {
      syncUser();
    });

    return () => {
      mounted = false;
      subscription.subscription.unsubscribe();
    };
  }, [setUser, setLoading]);
}
