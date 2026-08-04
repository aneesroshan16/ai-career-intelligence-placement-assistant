import { useQuery } from "@tanstack/react-query";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import { getStudentDashboard } from "@/lib/api/assessmentModules";
import { useAuthStore } from "@/store/authStore";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const { data, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: getStudentDashboard });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Welcome back, {user?.full_name?.split(" ")[0] ?? "there"}</h1>
        <p className="text-sm text-muted-foreground">Here's a snapshot of your placement readiness.</p>
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading dashboard...</p>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          <Card className="transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-primary/40 bg-card/60 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>ATS Score Trend</CardTitle>
            </CardHeader>
            <CardContent className="h-64">
              {data?.ats_score_trend.length ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.ats_score_trend}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis dataKey="date" hide />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Line type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full flex-col items-center justify-center space-y-3">
                  <p className="text-sm text-muted-foreground text-center">
                    No ATS reports yet. Upload your resume to see trends here.
                  </p>
                  <Button asChild variant="outline" size="sm">
                    <Link to="/resume">Upload Resume</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-primary/40 bg-card/60 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Readiness Score Trend</CardTitle>
            </CardHeader>
            <CardContent className="h-64">
              {data?.readiness_trend.length ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.readiness_trend}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis dataKey="date" hide />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Line type="monotone" dataKey="overall_score" stroke="hsl(217 91% 60%)" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full flex-col items-center justify-center space-y-3">
                  <p className="text-sm text-muted-foreground text-center">No readiness data yet.</p>
                  <Button asChild variant="outline" size="sm">
                    <Link to="/skills">Analyze Skill Gap</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-primary/40 bg-card/60 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Skill Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-sm text-muted-foreground">
                {data?.skill_progress.total_skills ?? 0} skills detected on your active resume
              </p>
              <div className="flex flex-wrap gap-2">
                {data?.skill_progress.matched_skill_names.slice(0, 15).map((skill) => (
                  <Badge key={skill} variant="secondary">
                    {skill}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-primary/40 bg-card/60 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Recent Interview Sessions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {data?.interview_history.length ? (
                data.interview_history.slice(0, 5).map((session) => (
                  <div key={session.id} className="flex items-center justify-between text-sm">
                    <span className="capitalize">{session.mode} interview</span>
                    <Badge variant={session.status === "completed" ? "success" : "warning"}>
                      {session.score !== null ? `${session.score}%` : session.status}
                    </Badge>
                  </div>
                ))
              ) : (
                <div className="flex h-full flex-col items-center justify-center space-y-3 pt-4">
                  <p className="text-sm text-muted-foreground text-center">No interview sessions yet.</p>
                  <Button asChild variant="outline" size="sm">
                    <Link to="/interview">Start Interview Prep</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
