import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import { generateRoadmap } from "@/lib/api/resumeModules";
import { analyzeSkillGap, listResumes, getRecommendedRoles, getMe } from "@/lib/api/resumeModules";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { CheckCircle2, AlertTriangle, Route } from "lucide-react";

export default function SkillGapPage() {
  const navigate = useNavigate();
  const { data: user } = useQuery({ queryKey: ["user"], queryFn: getMe });
  const { data: resumes } = useQuery({ queryKey: ["resumes"], queryFn: listResumes });
  const activeResume = resumes?.find((r) => r.is_active);
  
  const { data: roles } = useQuery({ 
    queryKey: ["roles", activeResume?.id], 
    queryFn: () => getRecommendedRoles(activeResume!.id),
    enabled: !!activeResume,
  });

  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);

  const roadmapMutation = useMutation({
    mutationFn: (gapId: string) => generateRoadmap(gapId, 8),
    onSuccess: (roadmap) => navigate(`/roadmap?id=${roadmap.id}`),
  });

  const gapMutation = useMutation({
    mutationFn: () => analyzeSkillGap(activeResume!.id, selectedRoleId!),
  });

  return (
    <motion.div 
      className="space-y-8 max-w-5xl mx-auto"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="space-y-2">
        <h1 className="text-4xl font-extrabold tracking-tight">Skill Gap Analysis</h1>
        <p className="text-muted-foreground text-lg">
          Compare your current skills against industry requirements for your target role.
        </p>
      </div>

      {!activeResume ? (
        <Card className="glass p-8 text-center">
          <p className="text-muted-foreground">Upload a resume first to run a skill gap analysis.</p>
          <Button className="mt-4" onClick={() => navigate("/resume")}>Go to Resume Upload</Button>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-12">
          
          <Card className="md:col-span-4 h-fit glass">
            <CardHeader>
              <CardTitle>Target Role</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col gap-2">
                {roles?.map((role) => {
                  const isSelected = selectedRoleId === role.id;
                  const isUserTarget = user?.profile?.target_role === role.name;
                  return (
                    <Button
                      key={role.id}
                      variant={isSelected ? "default" : "outline"}
                      className={`justify-start ${isSelected ? "shadow-md" : ""} ${isUserTarget ? "border-primary/50" : ""}`}
                      onClick={() => setSelectedRoleId(role.id)}
                    >
                      {role.name} {role.match_percentage !== undefined ? `(${role.match_percentage}%)` : ""}
                      {isUserTarget && <Badge variant="secondary" className="ml-auto text-[10px]">Target</Badge>}
                    </Button>
                  );
                })}
              </div>
              <Button 
                className="w-full mt-4 shadow-lg"
                disabled={!selectedRoleId || gapMutation.isPending || roadmapMutation.isPending} 
                onClick={() => gapMutation.mutate()}
              >
                {gapMutation.isPending ? "Analyzing..." : "Run Analysis"}
              </Button>
            </CardContent>
          </Card>

          <div className="md:col-span-8 space-y-6">
            {!gapMutation.data && !gapMutation.isPending && (
              <Card className="h-full min-h-[300px] flex items-center justify-center glass bg-primary/5 border-dashed">
                <p className="text-muted-foreground text-sm text-center max-w-sm">
                  Select a role on the left and run the analysis to discover which skills you need to learn.
                </p>
              </Card>
            )}

            {gapMutation.isPending && (
              <Card className="h-full min-h-[300px] flex flex-col items-center justify-center glass animate-pulse space-y-4">
                <div className="h-10 w-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                <p className="text-primary font-medium">Cross-referencing industry skill taxonomies...</p>
              </Card>
            )}

            {gapMutation.data && !gapMutation.isPending && (
              <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
                <Card className="glass overflow-hidden relative">
                  <div className="absolute top-0 right-0 bg-primary text-primary-foreground px-4 py-2 font-bold rounded-bl-xl shadow-lg">
                    {gapMutation.data.match_percentage}% MATCH
                  </div>
                  <CardHeader className="pb-4">
                    <CardTitle className="text-2xl">Analysis Results</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-8">
                    
                    <div>
                      <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
                        <CheckCircle2 className="text-green-500 h-5 w-5" />
                        Skills You Have
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {gapMutation.data.matched_skills.map((s) => (
                          <Badge key={s.skill} variant="success" className="px-3 py-1 text-xs shadow-sm bg-green-500/10 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800">
                            {s.skill}
                          </Badge>
                        ))}
                        {gapMutation.data.matched_skills.length === 0 && (
                          <p className="text-sm text-muted-foreground">No matching skills detected.</p>
                        )}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
                        <AlertTriangle className="text-amber-500 h-5 w-5" />
                        Skills to Learn
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {gapMutation.data.missing_skills.map((s) => (
                          <Badge key={s.skill} variant="warning" className="px-3 py-1 text-xs shadow-sm bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800">
                            {s.skill}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="pt-6 border-t flex items-center justify-between">
                      <div className="space-y-1">
                        <p className="font-semibold">Ready to upskill?</p>
                        <p className="text-xs text-muted-foreground">Generate an AI learning roadmap based on these gaps.</p>
                      </div>
                      <Button 
                        size="lg"
                        className="shadow-xl hover:shadow-primary/25 hover:-translate-y-0.5 transition-all"
                        onClick={() => roadmapMutation.mutate(gapMutation.data.id)}
                        disabled={roadmapMutation.isPending}
                      >
                        <Route className="mr-2 h-4 w-4" />
                        {roadmapMutation.isPending ? "Generating..." : "Create Weekly Roadmap"}
                      </Button>
                    </div>

                  </CardContent>
                </Card>
              </motion.div>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
}
