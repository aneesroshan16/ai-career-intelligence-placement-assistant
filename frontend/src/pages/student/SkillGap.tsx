import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import { generateRoadmap } from "@/lib/api/resumeModules";
import { analyzeSkillGap, listResumes, listRoles } from "@/lib/api/resumeModules";
import { useNavigate } from "react-router-dom";

export default function SkillGapPage() {
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const navigate = useNavigate();

  const { data: resumes } = useQuery({ queryKey: ["resumes"], queryFn: listResumes });
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: listRoles });
  const activeResume = resumes?.find((r) => r.is_active);

  const gapMutation = useMutation({
    mutationFn: () => analyzeSkillGap(activeResume!.id, selectedRoleId!),
  });

  const roadmapMutation = useMutation({
    mutationFn: () => generateRoadmap(gapMutation.data!.id, 8),
    onSuccess: (roadmap) => navigate(`/roadmap?id=${roadmap.id}`),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Skill Gap Analysis</h1>
        <p className="text-sm text-muted-foreground">
          Compare your resume against a target role's skill requirements.
        </p>
      </div>

      {!activeResume ? (
        <p className="text-sm text-muted-foreground">Upload a resume first to run a skill gap analysis.</p>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Choose a Target Role</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {roles?.map((role) => (
                <Button
                  key={role.id}
                  variant={selectedRoleId === role.id ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedRoleId(role.id)}
                >
                  {role.name}
                </Button>
              ))}
            </div>
            <Button disabled={!selectedRoleId || gapMutation.isPending} onClick={() => gapMutation.mutate()}>
              {gapMutation.isPending ? "Analyzing..." : "Analyze Skill Gap"}
            </Button>

            {gapMutation.data && (
              <div className="space-y-4 pt-4">
                <p className="text-sm">
                  Match: <span className="font-semibold">{gapMutation.data.match_percentage}%</span>
                </p>
                <div>
                  <p className="mb-2 text-sm font-medium text-green-600">Matched Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {gapMutation.data.matched_skills.map((s) => (
                      <Badge key={s.skill} variant="success">
                        {s.skill}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="mb-2 text-sm font-medium text-amber-600">Missing Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {gapMutation.data.missing_skills.map((s) => (
                      <Badge key={s.skill} variant="warning">
                        {s.skill}
                      </Badge>
                    ))}
                  </div>
                </div>
                <Button onClick={() => roadmapMutation.mutate()} disabled={roadmapMutation.isPending}>
                  {roadmapMutation.isPending ? "Generating roadmap..." : "Generate Learning Roadmap"}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
