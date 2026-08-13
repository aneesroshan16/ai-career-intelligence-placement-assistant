import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import { Skeleton } from "@/components/ui/skeleton";
import { getRoadmap, updateRoadmapProgress } from "@/lib/api/resumeModules";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { motion } from "framer-motion";

export default function RoadmapPage() {
  const [searchParams] = useSearchParams();
  const roadmapId = searchParams.get("id");
  const queryClient = useQueryClient();

  const { data: roadmap, isLoading } = useQuery({
    queryKey: ["roadmap", roadmapId],
    queryFn: () => getRoadmap(roadmapId!),
    enabled: !!roadmapId,
  });

  const progressMutation = useMutation({
    mutationFn: ({ week, taskIndex, completed }: { week: number, taskIndex: number, completed: boolean }) => 
      updateRoadmapProgress(roadmapId!, week, taskIndex, completed),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roadmap", roadmapId] });
    }
  });

  if (!roadmapId) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground">
          No roadmap selected. Generate one from the Skill Gap Analysis page.
        </p>
      </div>
    );
  }

  const totalTasks = roadmap?.plan.reduce((acc, week) => acc + week.tasks.length, 0) || 0;
  const completedTasks = roadmap?.plan.reduce((acc, week) => 
    acc + (week.tasks_completed?.filter(Boolean).length || 0), 0) || 0;
  const progressPercent = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <motion.div 
      className="space-y-8 max-w-5xl mx-auto pb-12"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="space-y-2 relative z-10">
        <h1 className="text-4xl font-extrabold tracking-tight">Your Learning Roadmap</h1>
        <p className="text-lg text-muted-foreground">
          {roadmap ? `${roadmap.total_weeks}-week personalized plan designed to close your skill gaps.` : "Loading..."}
        </p>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-64 w-full rounded-xl" />
          <Skeleton className="h-64 w-full rounded-xl" />
        </div>
      ) : (
        <>
          <Card className="glass mb-8">
            <CardContent className="pt-6">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold text-lg">Overall Progress</h3>
                <span className="font-bold text-primary">{progressPercent}%</span>
              </div>
              <Progress value={progressPercent} className="h-3 rounded-full" />
              <p className="text-xs text-muted-foreground mt-3">
                {completedTasks} of {totalTasks} tasks completed
              </p>
            </CardContent>
          </Card>

          <div className="grid gap-6 md:grid-cols-2">
            {roadmap?.plan.map((week, wIndex) => {
              const weekCompleted = week.tasks_completed?.filter(Boolean).length;
              const isAllDone = weekCompleted === week.tasks.length && week.tasks.length > 0;

              return (
                <motion.div 
                  key={week.week} 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: wIndex * 0.1 }}
                >
                  <Card className={`h-full flex flex-col relative overflow-hidden transition-all duration-300 ${isAllDone ? "bg-primary/5 border-primary/20 shadow-primary/10 shadow-lg" : "glass glass-hover"}`}>
                    <CardHeader className="pb-3 border-b border-border/50 bg-muted/20">
                      <div className="flex justify-between items-center">
                        <CardTitle className="text-xl flex items-center gap-2">
                          Week {week.week}
                          {isAllDone && <Badge variant="success" className="text-[10px] uppercase tracking-wider ml-2">Completed</Badge>}
                        </CardTitle>
                        <Badge variant="outline" className="font-mono text-xs">{week.est_hours} hrs</Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-5 flex-1 flex flex-col gap-4">
                      
                      {week.focus_skills.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wider">Focus Skills</p>
                          <div className="flex flex-wrap gap-1.5">
                            {week.focus_skills.map((skill) => (
                              <Badge key={skill} variant="secondary" className="bg-primary/10 hover:bg-primary/20 text-primary transition-colors">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="space-y-2 mt-auto">
                        <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wider">Weekly Tasks</p>
                        <div className="space-y-3">
                          {week.tasks.map((task, i) => {
                            const isChecked = week.tasks_completed?.[i] || false;
                            return (
                              <div key={i} className={`flex items-start space-x-3 group p-2 rounded-md transition-colors ${isChecked ? "bg-muted/30" : "hover:bg-muted/10"}`}>
                                <Checkbox 
                                  id={`task-${week.week}-${i}`} 
                                  checked={isChecked}
                                  onCheckedChange={(checked) => 
                                    progressMutation.mutate({ week: week.week, taskIndex: i, completed: !!checked })
                                  }
                                  disabled={progressMutation.isPending}
                                  className="mt-1 flex-shrink-0 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
                                />
                                <label 
                                  htmlFor={`task-${week.week}-${i}`}
                                  className={`text-sm leading-snug cursor-pointer transition-colors ${isChecked ? "text-muted-foreground line-through opacity-70" : "text-foreground group-hover:text-primary"}`}
                                >
                                  {task}
                                </label>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>

          {roadmap && roadmap.milestones.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="mt-8">
              <Card className="glass relative overflow-hidden">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500 to-indigo-500"></div>
                <CardHeader>
                  <CardTitle className="text-2xl">Monthly Milestones</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {roadmap.milestones.map((m, i) => (
                    <div key={m.month} className="flex gap-4 items-start relative">
                      {i !== roadmap.milestones.length - 1 && (
                        <div className="absolute left-4 top-10 bottom-[-24px] w-0.5 bg-border"></div>
                      )}
                      <div className="h-8 w-8 rounded-full bg-blue-500/10 text-blue-600 flex items-center justify-center font-bold text-sm shrink-0 border border-blue-200 dark:border-blue-800 z-10">
                        {m.month}
                      </div>
                      <div className="bg-muted/20 p-4 rounded-xl flex-1 border border-border/50">
                        <p className="font-semibold text-lg text-foreground mb-1">{m.goal}</p>
                        <div className="flex items-start gap-2">
                          <span className="text-xs uppercase font-bold text-muted-foreground tracking-wider mt-0.5">Deliverable</span>
                          <p className="text-sm text-muted-foreground leading-relaxed">{m.deliverable}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          )}
        </>
      )}
    </motion.div>
  );
}
