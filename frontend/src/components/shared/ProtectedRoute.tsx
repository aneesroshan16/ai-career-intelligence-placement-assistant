import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-muted-foreground">
        Loading your session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

export function AdminRoute() {
  const { user, isLoading } = useAuthStore();

  if (isLoading) return null;
  if (!user || (user.role !== "admin" && user.role !== "placement_officer")) {
    return <Navigate to="/dashboard" replace />;
  }
  return <Outlet />;
}
