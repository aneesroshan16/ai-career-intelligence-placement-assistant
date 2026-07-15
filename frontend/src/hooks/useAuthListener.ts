import { useEffect } from "react";
import { supabase } from "@/lib/supabaseClient";
import { getMe } from "@/lib/api/resumeModules";
import { useAuthStore } from "@/store/authStore";

/**
 * On mount, and whenever the Supabase auth state changes, fetches the
 * backend-owned user profile (which lazily provisions the `users` row on
 * first sight — see core/security.py) and syncs it into the auth store.
 */
export function useAuthListener() {
  const setUser = useAuthStore((s) => s.setUser);
  const setLoading = useAuthStore((s) => s.setLoading);

  useEffect(() => {
    let mounted = true;

    async function syncUser() {
      setLoading(true);
      try {
        const { data } = await supabase.auth.getSession();
        if (!data.session) {
          if (mounted) setUser(null);
          return;
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

    const { data: subscription } = supabase.auth.onAuthStateChange(() => {
      syncUser();
    });

    return () => {
      mounted = false;
      subscription.subscription.unsubscribe();
    };
  }, [setUser, setLoading]);
}
