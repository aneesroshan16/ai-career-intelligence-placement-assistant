import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { analyzeATS, getMe, updateMe, listResumes, getRecommendedRoles } from "@/lib/api/resumeModules";
import type { Role } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, ArrowRight } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export default function TargetRoleSelectionPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: user } = useQuery({ queryKey: ["user"], queryFn: getMe });
  const { data: resumes } = useQuery({ queryKey: ["resumes"], queryFn: listResumes });
  const activeResume = resumes?.find((r) => r.is_active);

  const { data: roles, isLoading } = useQuery({
    queryKey: ["recommendedRoles", activeResume?.id],
    queryFn: () => getRecommendedRoles(activeResume!.id),
    enabled: !!activeResume && activeResume.parse_status === "completed",
    retry: false
  });

  const updateRoleMutation = useMutation({
    mutationFn: async (role: Role) => {
      await updateMe({ target_role: role.name });
      // Keep the persisted ATS report aligned with the newly selected role.
      if (activeResume) await analyzeATS(activeResume.id, role.id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
      navigate("/skills");
    }
  });

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto py-12">
        <Skeleton className="h-12 w-1/2 mx-auto mb-10" />
        <div className="grid md:grid-cols-3 gap-6">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (!roles?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center space-y-4 max-w-lg mx-auto">
        <h2 className="text-2xl font-bold">No Role Recommendations Found</h2>
        <p className="text-muted-foreground">
          You need to upload your resume and run the ATS analyzer to get personalized career role recommendations.
        </p>
        <Button onClick={() => navigate("/resume")}>Go to Resume Analyzer</Button>
      </div>
    );
  }

  return (
    <motion.div 
      className="space-y-8 max-w-5xl mx-auto pb-12 relative"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="relative z-10 text-center space-y-2 mb-10">
        <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
          Choose Your Career Goal
        </h1>
        <p className="text-base text-muted-foreground mt-1 max-w-2xl mx-auto">
          Based on your resume, our AI has identified the following career roles as your best matches. Select your target role to generate your personalized learning roadmap.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {roles.map((role, i) => (
          <motion.div 
            key={i} 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="h-full flex flex-col relative overflow-hidden group glass glass-hover hover:-translate-y-2 border-2 border-transparent hover:border-primary/50 transition-all cursor-pointer"
                  onClick={() => updateRoleMutation.mutate(role)}>
              <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="absolute top-0 right-0 bg-gradient-to-l from-primary to-blue-500 text-primary-foreground px-4 py-1.5 text-xs font-bold rounded-bl-xl shadow-md">
                {role.match_percentage}% MATCH
              </div>
              <CardHeader className="pb-3 pt-6">
                <CardTitle className="text-lg pr-12">{role.name}</CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col gap-4 text-sm z-10">
                <div className="space-y-1">
                  <p className="font-semibold text-xs uppercase text-muted-foreground tracking-wider">Why it matches</p>
                  <ul className="space-y-1">
                    {(role.matched_skills?.length ? role.matched_skills : [role.reasoning || "Resume evidence is being evaluated."]).map((w, j) => (
                      <li key={j} className="flex items-start gap-1.5">
                        <CheckCircle2 className="h-3.5 w-3.5 text-green-500 mt-0.5 shrink-0" />
                        <span className="leading-snug">{w}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                {(role.missing_skills?.length ?? 0) > 0 && (
                  <div className="space-y-1 mt-auto pt-4 border-t">
                    <p className="font-semibold text-xs uppercase text-muted-foreground tracking-wider">Skills to add</p>
                    <p className="text-muted-foreground text-xs leading-relaxed">
                      {role.missing_skills?.join(", ")}
                    </p>
                  </div>
                )}
                
                <Button 
                  className="w-full mt-4 group-hover:bg-primary group-hover:text-primary-foreground transition-all"
                  variant={user?.profile?.target_role === role.name ? "default" : "outline"}
                  disabled={updateRoleMutation.isPending}
                >
                  {updateRoleMutation.isPending && updateRoleMutation.variables?.name === role.name ? (
                    "Setting Role..."
                  ) : user?.profile?.target_role === role.name ? (
                    "Current Target"
                  ) : (
                    <>Select Role <ArrowRight className="ml-2 h-4 w-4" /></>
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
