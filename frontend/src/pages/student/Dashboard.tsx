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
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from "framer-motion";

const container: any = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const item: any = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const { data, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: getStudentDashboard });

  return (
    <motion.div 
      className="space-y-8 relative"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Animated blob background */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob pointer-events-none"></div>
      <div className="absolute top-0 -right-4 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000 pointer-events-none"></div>

      <div className="relative z-10 space-y-2">
        <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
          Welcome back, {user?.full_name?.split(" ")[0] ?? "there"}
        </h1>
        <p className="text-base text-muted-foreground">Here's a snapshot of your placement readiness.</p>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 relative z-10">
          <Skeleton className="h-72 w-full rounded-2xl bg-muted/50" />
          <Skeleton className="h-72 w-full rounded-2xl bg-muted/50" />
          <Skeleton className="h-48 w-full rounded-2xl bg-muted/50" />
          <Skeleton className="h-48 w-full rounded-2xl bg-muted/50" />
        </div>
      ) : (
        <motion.div 
          className="grid gap-6 md:grid-cols-2 relative z-10"
          variants={container}
          initial="hidden"
          animate="show"
        >
          <motion.div variants={item}>
            <Card className="h-full overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-primary/20 hover:-translate-y-1 bg-background/60 backdrop-blur-xl border-white/10 dark:border-white/5 relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <CardHeader>
                <CardTitle className="text-lg">ATS Score Trend</CardTitle>
              </CardHeader>
              <CardContent className="h-64 relative z-10">
                {data?.ats_score_trend.length ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data.ats_score_trend}>
                      <defs>
                        <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted/30" vertical={false} />
                      <XAxis dataKey="date" hide />
                      <YAxis domain={[0, 100]} className="text-xs" axisLine={false} tickLine={false} />
                      <Tooltip 
                        contentStyle={{ borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: 'rgba(0,0,0,0.8)' }} 
                        itemStyle={{ color: '#fff' }} 
                      />
                      <Line type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full flex-col items-center justify-center space-y-4">
                    <p className="text-sm text-muted-foreground text-center">
                      No ATS reports yet. Upload your resume to see trends here.
                    </p>
                    <Button asChild variant="default" size="sm" className="rounded-full shadow-lg hover:shadow-primary/50 transition-all">
                      <Link to="/resume">Upload Resume</Link>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={item}>
            <Card className="h-full overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/20 hover:-translate-y-1 bg-background/60 backdrop-blur-xl border-white/10 dark:border-white/5 relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <CardHeader>
                <CardTitle className="text-lg">Readiness Score Trend</CardTitle>
              </CardHeader>
              <CardContent className="h-64 relative z-10">
                {data?.readiness_trend.length ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data.readiness_trend}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted/30" vertical={false} />
                      <XAxis dataKey="date" hide />
                      <YAxis domain={[0, 100]} className="text-xs" axisLine={false} tickLine={false} />
                      <Tooltip 
                        contentStyle={{ borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: 'rgba(0,0,0,0.8)' }} 
                        itemStyle={{ color: '#fff' }} 
                      />
                      <Line type="monotone" dataKey="overall_score" stroke="hsl(217 91% 60%)" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full flex-col items-center justify-center space-y-4">
                    <p className="text-sm text-muted-foreground text-center">No readiness data yet.</p>
                    <Button asChild variant="outline" size="sm" className="rounded-full hover:bg-blue-500/10 hover:text-blue-600 transition-colors">
                      <Link to="/skills">Analyze Skill Gap</Link>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={item}>
            <Card className="h-full overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-emerald-500/10 bg-background/60 backdrop-blur-xl border-white/10 dark:border-white/5 relative">
              <CardHeader>
                <CardTitle className="text-lg">Skill Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 mb-4">
                  <div className="text-3xl font-bold text-emerald-500">{data?.skill_progress.total_skills ?? 0}</div>
                  <span className="text-sm text-muted-foreground leading-tight">skills detected on<br/>your active resume</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {data?.skill_progress.matched_skill_names.slice(0, 15).map((skill, i) => (
                    <motion.div key={skill} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }}>
                      <Badge variant="secondary" className="bg-secondary/50 hover:bg-secondary transition-colors">
                        {skill}
                      </Badge>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={item}>
            <Card className="h-full overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-orange-500/10 bg-background/60 backdrop-blur-xl border-white/10 dark:border-white/5 relative">
              <CardHeader>
                <CardTitle className="text-lg">Recent Interview Sessions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {data?.interview_history.length ? (
                  data.interview_history.slice(0, 5).map((session, i) => (
                    <motion.div 
                      key={session.id} 
                      className="flex items-center justify-between p-3 rounded-lg bg-muted/20 hover:bg-muted/40 transition-colors"
                      initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                    >
                      <span className="capitalize font-medium text-sm">{session.mode} interview</span>
                      <Badge variant={session.status === "completed" ? "success" : "warning"} className="shadow-sm">
                        {session.score !== null ? `${session.score}%` : session.status}
                      </Badge>
                    </motion.div>
                  ))
                ) : (
                  <div className="flex h-full flex-col items-center justify-center space-y-4 pt-6">
                    <p className="text-sm text-muted-foreground text-center">No interview sessions yet.</p>
                    <Button asChild variant="outline" size="sm" className="rounded-full">
                      <Link to="/interview">Start Interview Prep</Link>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      )}
    </motion.div>
  );
}
