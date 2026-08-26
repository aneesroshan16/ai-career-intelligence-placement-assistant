import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { getRecommendedJobs, listJobs, getMyReadiness, recomputeReadiness } from "@/lib/api/assessmentModules";
import { motion } from "framer-motion";
import { Briefcase, Target, Building2, MapPin, Search, BarChart3, RefreshCw, Zap } from "lucide-react";

export default function JobsPage() {
  const queryClient = useQueryClient();

  const { data: readiness, isLoading: loadingReadiness } = useQuery({
    queryKey: ["readiness", "me"],
    queryFn: getMyReadiness,
    retry: false,
  });

  const recomputeMutation = useMutation({
    mutationFn: recomputeReadiness,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["readiness", "me"] });
    }
  });

  const { data: recommended, isLoading: loadingRecommended } = useQuery({
    queryKey: ["jobs", "recommended"],
    queryFn: getRecommendedJobs,
    retry: false,
  });

  const { data: allJobs, isLoading: loadingAll } = useQuery({ queryKey: ["jobs", "all"], queryFn: () => listJobs() });

  const readinessScore = readiness?.overall_score || 0;
  
  // Determine color based on score
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-amber-500";
    return "text-destructive";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-amber-500";
    return "bg-destructive";
  };

  return (
    <motion.div 
      className="space-y-8 max-w-6xl mx-auto pb-12"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 relative z-10">
        <div className="space-y-2">
          <h1 className="text-4xl font-extrabold tracking-tight">Jobs & Readiness</h1>
          <p className="text-lg text-muted-foreground">
            Track your placement readiness and discover personalized job matches.
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-12">
        {/* Readiness Score Section */}
        <Card className="md:col-span-4 h-fit glass relative overflow-hidden">
          <div className="absolute right-0 top-0 w-32 h-32 bg-primary/5 rounded-bl-full pointer-events-none"></div>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" /> 
              Placement Readiness
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {loadingReadiness ? (
              <div className="space-y-4">
                <Skeleton className="h-32 w-full rounded-xl" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : (
              <>
                <div className="flex flex-col items-center justify-center p-6 bg-background/50 rounded-xl border border-border/50 shadow-inner">
                  <div className="relative flex items-center justify-center mb-2">
                    <svg className="w-32 h-32 transform -rotate-90">
                      <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="transparent" className="text-muted/30" />
                      <circle 
                        cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="transparent" 
                        strokeDasharray={351.86} strokeDashoffset={351.86 - (351.86 * readinessScore) / 100}
                        className={`${getScoreColor(readinessScore)} transition-all duration-1000 ease-out`} 
                      />
                    </svg>
                    <div className="absolute flex flex-col items-center justify-center text-center">
                      <span className={`text-3xl font-extrabold tracking-tighter ${getScoreColor(readinessScore)}`}>{readinessScore}</span>
                      <span className="text-[10px] uppercase font-bold text-muted-foreground">Score</span>
                    </div>
                  </div>
                  
                  <div className="w-full space-y-4 mt-4">
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="text-muted-foreground">Technical</span>
                        <span>{readiness?.technical_score || 0}%</span>
                      </div>
                      <Progress value={readiness?.technical_score || 0} className="h-1.5" />
                    </div>
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="text-muted-foreground">Aptitude</span>
                        <span>{readiness?.aptitude_score || 0}%</span>
                      </div>
                      <Progress value={readiness?.aptitude_score || 0} className="h-1.5" />
                    </div>
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="text-muted-foreground">Interview</span>
                        <span>{readiness?.interview_score || 0}%</span>
                      </div>
                      <Progress value={readiness?.interview_score || 0} className="h-1.5" />
                    </div>
                  </div>
                </div>

                <Button 
                  className="w-full shadow-md transition-all active:scale-95" 
                  onClick={() => recomputeMutation.mutate()}
                  disabled={recomputeMutation.isPending}
                >
                  <RefreshCw className={`mr-2 h-4 w-4 ${recomputeMutation.isPending ? "animate-spin" : ""}`} />
                  {recomputeMutation.isPending ? "Updating Score..." : "Recalculate Score"}
                </Button>
                
                <p className="text-xs text-muted-foreground text-center">
                  Score is calculated across ATS, Coding, Aptitude, and Interview modules.
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Jobs List Section */}
        <div className="md:col-span-8 space-y-6">
          <Card className="glass">
            <CardHeader className="pb-3 border-b bg-muted/20">
              <CardTitle className="text-xl flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-500" /> 
                Recommended For You
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {loadingRecommended ? (
                <div className="space-y-4">
                  {[1, 2].map((i) => (
                    <Skeleton key={i} className="h-24 w-full rounded-xl" />
                  ))}
                </div>
              ) : recommended?.length ? (
                <div className="space-y-4">
                  {recommended.map((match, i) => (
                    <motion.div 
                      key={match.job_id} 
                      initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                      className="group flex flex-col sm:flex-row sm:items-center justify-between rounded-xl border p-4 bg-background/50 hover:bg-muted/30 transition-all shadow-sm hover:shadow-md hover:border-blue-500/30 gap-4"
                    >
                      <div className="space-y-2 flex-1">
                        <div className="flex items-center gap-2">
                          <div className="h-8 w-8 rounded-lg bg-blue-500/10 text-blue-600 flex items-center justify-center shrink-0">
                            <Briefcase className="h-4 w-4" />
                          </div>
                          <h3 className="text-base font-bold text-foreground group-hover:text-blue-600 transition-colors">
                            {match.title}
                          </h3>
                        </div>
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-muted-foreground pl-10">
                          <span className="flex items-center gap-1"><Building2 className="h-3.5 w-3.5" /> {match.company_name}</span>
                          <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {match.location}</span>
                          <Badge variant="outline" className="text-[10px] font-normal">{match.job_type}</Badge>
                        </div>
                      </div>
                      
                      <div className="flex flex-row sm:flex-col items-center justify-between sm:justify-center gap-2 pl-10 sm:pl-0 sm:border-l sm:border-t-0 border-t pt-3 sm:pt-0 sm:w-28 shrink-0">
                        <div className="flex flex-col items-center">
                          <span className="text-xl font-bold text-blue-600">{Math.round(match.similarity_score * 100)}%</span>
                          <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">Match</span>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-10 text-center space-y-3 bg-muted/20 rounded-xl border border-dashed">
                  <Zap className="h-10 w-10 text-muted-foreground/40" />
                  <p className="text-muted-foreground font-medium">No personalized recommendations yet.</p>
                  <p className="text-xs text-muted-foreground max-w-sm">
                    Upload your resume and complete skill gap analysis to generate AI-matched roles.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="glass">
            <CardHeader className="pb-3 border-b">
              <div className="flex justify-between items-center">
                <CardTitle className="text-xl flex items-center gap-2">
                  <Search className="h-5 w-5 text-muted-foreground" /> 
                  All Open Positions
                </CardTitle>
                <Badge variant="secondary">{allJobs?.length || 0} Openings</Badge>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              {loadingAll ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-24 w-full rounded-xl" />
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {allJobs?.map((job) => (
                    <div key={job.id} className="flex flex-col md:flex-row justify-between rounded-xl border p-4 bg-background/50 hover:bg-muted/10 transition-colors gap-4">
                      <div className="space-y-3 flex-1">
                        <div>
                          <h3 className="text-base font-semibold">{job.title}</h3>
                          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground mt-1">
                            <span className="flex items-center gap-1"><Building2 className="h-3.5 w-3.5" /> {job.company_name}</span>
                            <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {job.location}</span>
                            <span className="font-mono bg-muted px-1.5 py-0.5 rounded text-[10px]">{job.experience_min}-{job.experience_max ?? "∞"} Yrs</span>
                          </div>
                        </div>
                        
                        <div className="flex flex-wrap gap-1.5">
                          {job.required_skills?.slice(0, 4).map((s) => (
                            <Badge key={s} variant="outline" className="bg-background/50 text-[10px]">
                              {s}
                            </Badge>
                          ))}
                          {job.required_skills && job.required_skills.length > 4 && (
                            <Badge variant="outline" className="bg-background/50 text-[10px] text-muted-foreground">
                              +{job.required_skills.length - 4}
                            </Badge>
                          )}
                        </div>
                      </div>
                      
                    </div>
                  ))}
                  
                  {allJobs?.length === 0 && (
                    <p className="text-center text-muted-foreground py-8">No open positions found.</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </motion.div>
  );
}
