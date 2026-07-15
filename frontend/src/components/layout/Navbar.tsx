import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { signOut } from "@/lib/supabaseClient";
import { useAuthStore } from "@/store/authStore";

export function Navbar() {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await signOut();
    setUser(null);
    navigate("/login");
  };

  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6">
      <div />
      <div className="flex items-center gap-3">
        <ThemeToggle />
        {user && (
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium">{user.full_name}</span>
            <Button variant="ghost" size="icon" onClick={handleLogout} aria-label="Log out">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
