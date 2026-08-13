import { useEffect } from "react";
import { isSupabaseConfigured, supabase } from "@/lib/supabaseClient";
import { getMe } from "@/lib/api/resumeModules";
import { useAuthStore } from "@/store/authStore";

export function useAuthListener() {
  const setUser = useAuthStore((s) => s.setUser);
  const setLoading = useAuthStore((s) => s.setLoading);
  const setAuthError = useAuthStore((s) => s.setAuthError);

  useEffect(() => {
    let mounted = true;

    async function syncUser() {
      setLoading(true);
      if (mounted) setAuthError(null);
      try {
        if (!isSupabaseConfigured) {
          if (mounted) setUser(null);
          return;
        }
        
        const { data } = await supabase.auth.getSession();
        if (!data.session) {
          if (mounted) setUser(null);
          return;
        }
        
        const profile = await getMe();
        if (mounted) setUser(profile);
      } catch (error) {
        if (mounted) {
          setUser(null);
          const msg = error instanceof Error ? error.message : "Failed to load user profile. Is the backend server running?";
          setAuthError(msg);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    syncUser();

    if (!isSupabaseConfigured) return;

    const { data: subscription } = supabase.auth.onAuthStateChange(() => {
      syncUser();
    });

    return () => {
      mounted = false;
      subscription.subscription.unsubscribe();
    };
  }, [setUser, setLoading]);
}
