import { LogOut, UserRound } from "lucide-react";
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
    <header className="flex h-16 items-center justify-between border-b border-border/50 bg-background/60 backdrop-blur-xl px-6">
      <div />
      <div className="flex items-center gap-3">
        <ThemeToggle />
        {user && (
          <div className="flex items-center gap-3">
            <div
              className="flex h-9 w-9 items-center justify-center overflow-hidden rounded-full border border-primary/30 bg-primary/10 text-primary"
              aria-label="Profile"
              title={user.full_name || "Profile"}
            >
              {user.avatar_url ? <img src={user.avatar_url} alt="" className="h-full w-full object-cover" /> : <UserRound className="h-4 w-4" />}
            </div>
            <span className="hidden text-sm font-medium sm:inline">{user.full_name}</span>
            <Button variant="ghost" size="icon" onClick={handleLogout} aria-label="Log out">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
