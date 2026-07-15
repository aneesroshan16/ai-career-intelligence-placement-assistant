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
          <Card>
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
                <p className="text-sm text-muted-foreground">
                  No ATS reports yet — upload a resume and run an analysis to see trends here.
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
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
                <p className="text-sm text-muted-foreground">No readiness data yet.</p>
              )}
            </CardContent>
          </Card>

          <Card>
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

          <Card>
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
                <p className="text-sm text-muted-foreground">No interview sessions yet.</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
