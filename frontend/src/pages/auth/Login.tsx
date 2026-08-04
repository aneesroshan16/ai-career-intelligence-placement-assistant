import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/form-elements";
import { signInWithEmail, signInWithGoogle, isSupabaseConfigured, getOrCreateDevUserId } from "@/lib/supabaseClient";
import { devLogin } from "@/lib/api/authModules";
import { useAuthStore } from "@/store/authStore";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [devRole, setDevRole] = useState<"student" | "admin" | "placement_officer">("student");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    if (user) {
      navigate(user.role === "admin" || user.role === "placement_officer" ? "/admin" : "/dashboard");
    }
  }, [user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const { error: signInError } = await signInWithEmail(email, password);
    setLoading(false);
    if (signInError) {
      setError(signInError.message);
    }
  };

  const handleDevLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await devLogin({
        user_id: getOrCreateDevUserId(),
        email: email || "dev-student@example.com",
        role: devRole,
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Dev login failed. Is the backend running with AUTH_MODE=dev?"
      );
    } finally {
      setLoading(false);
    }
  };

  if (!isSupabaseConfigured) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Dev mode sign-in</CardTitle>
            <CardDescription>
              VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY aren&apos;t set, so real Supabase auth is
              disabled. This issues a local dev token instead (requires the backend running with
              AUTH_MODE=dev).
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleDevLogin} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="dev-email">Email (any value)</Label>
                <Input
                  id="dev-email"
                  type="email"
                  placeholder="dev-student@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="dev-role">Role</Label>
                <select
                  id="dev-role"
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={devRole}
                  onChange={(e) => setDevRole(e.target.value as typeof devRole)}
                >
                  <option value="student">Student</option>
                  <option value="admin">Admin</option>
                  <option value="placement_officer">Placement Officer</option>
                </select>
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Signing in..." : "Continue in dev mode"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Welcome back</CardTitle>
          <CardDescription>Sign in to your Career Intelligence account</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing in..." : "Sign in"}
            </Button>
          </form>
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">Or</span>
            </div>
          </div>
          <Button variant="outline" className="w-full" onClick={() => signInWithGoogle()}>
            Continue with Google
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link to="/signup" className="font-medium text-primary hover:underline">
              Sign up
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
