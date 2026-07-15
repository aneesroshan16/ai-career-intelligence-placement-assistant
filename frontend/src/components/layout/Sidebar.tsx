import {
  BarChart3,
  Briefcase,
  FileText,
  LayoutDashboard,
  MessageSquare,
  Route,
  ShieldCheck,
  Sigma,
  Target,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/authStore";

const studentNav = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/resume", label: "Resume & ATS", icon: FileText },
  { to: "/skills", label: "Skill Gap", icon: Target },
  { to: "/roadmap", label: "Roadmap", icon: Route },
  { to: "/placement", label: "Placement Prediction", icon: BarChart3 },
  { to: "/jobs", label: "Jobs", icon: Briefcase },
  { to: "/interview", label: "Interview Prep", icon: MessageSquare },
  { to: "/assessments", label: "Assessments", icon: Sigma },
];

const adminNav = [
  { to: "/admin", label: "Admin Analytics", icon: ShieldCheck },
  { to: "/analytics", label: "Platform Analytics", icon: BarChart3 },
];

export function Sidebar() {
  const user = useAuthStore((s) => s.user);
  const isAdmin = user?.role === "admin" || user?.role === "placement_officer";

  return (
    <aside className="hidden w-64 shrink-0 border-r bg-card md:block">
      <div className="flex h-full flex-col gap-1 p-4">
        <div className="mb-4 px-2">
          <p className="text-sm font-semibold">Career Intelligence</p>
          <p className="text-xs text-muted-foreground">Placement Assistant</p>
        </div>
        {studentNav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
        {isAdmin && (
          <>
            <div className="my-2 border-t" />
            {adminNav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
                  )
                }
              >
                <Icon className="h-4 w-4" />
                {label}
              </NavLink>
            ))}
          </>
        )}
      </div>
    </aside>
  );
}
