import { Link, Navigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

/**
 * Supabase exchanges OAuth/confirmation callback parameters while restoring
 * the browser session. Keeping this route mounted until that finishes avoids
 * routing a user through a protected page before auth state is known.
 */
export default function AuthCallbackPage() {
  const { user, isLoading } = useAuthStore();
  const [searchParams] = useSearchParams();
  const oauthError = searchParams.get("error") || searchParams.get("error_description");

  if (oauthError) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="max-w-md space-y-3 text-center">
          <h1 className="text-lg font-semibold">Sign-in could not be completed</h1>
          <p className="text-sm text-muted-foreground">
            Google sign-in was cancelled or rejected. Please try again.
          </p>
          <Link to="/login" className="text-sm font-medium text-primary hover:underline">
            Return to sign in
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-muted-foreground">
        Completing sign-in...
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === "admin" || user.role === "placement_officer" ? "/admin" : "/dashboard"} replace />;
}
