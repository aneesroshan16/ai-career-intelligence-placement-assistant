import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge, Progress } from "@/components/ui/form-elements";
import { analyzeATS, listResumes, listRoles, uploadResume } from "@/lib/api/resumeModules";

export default function ResumeUploadPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const { data: resumes } = useQuery({ queryKey: ["resumes"], queryFn: listResumes });
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: listRoles });

  const activeResume = resumes?.find((r) => r.is_active);

  const uploadMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["resumes"] }),
  });

  const atsMutation = useMutation({
    mutationFn: () => analyzeATS(activeResume!.id, selectedRoleId!),
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadMutation.mutate(file);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Resume & ATS Analyzer</h1>
        <p className="text-sm text-muted-foreground">Upload your resume to extract skills and check ATS readiness.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload Resume</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            onChange={handleFileChange}
          />
          <Button onClick={() => fileInputRef.current?.click()} disabled={uploadMutation.isPending}>
            {uploadMutation.isPending ? "Uploading & parsing..." : "Choose PDF or DOCX"}
          </Button>

          {activeResume && (
            <div className="rounded-md border p-4">
              <p className="text-sm font-medium">{activeResume.original_filename}</p>
              <Badge variant={activeResume.parse_status === "completed" ? "success" : "warning"} className="mt-2">
                {activeResume.parse_status}
              </Badge>
            </div>
          )}
        </CardContent>
      </Card>

      {activeResume?.parse_status === "completed" && (
        <Card>
          <CardHeader>
            <CardTitle>Run ATS Analysis</CardTitle>
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
            <Button
              disabled={!selectedRoleId || atsMutation.isPending}
              onClick={() => atsMutation.mutate()}
            >
              {atsMutation.isPending ? "Analyzing..." : "Analyze Resume"}
            </Button>

            {atsMutation.data && (
              <div className="space-y-4 pt-4">
                <div>
                  <div className="mb-1 flex justify-between text-sm">
                    <span>Overall ATS Score</span>
                    <span className="font-semibold">{atsMutation.data.overall_score}%</span>
                  </div>
                  <Progress value={atsMutation.data.overall_score} />
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Keyword Match</p>
                    <p className="font-semibold">{atsMutation.data.keyword_score}%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Formatting</p>
                    <p className="font-semibold">{atsMutation.data.formatting_score}%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Sections</p>
                    <p className="font-semibold">{atsMutation.data.section_score}%</p>
                  </div>
                </div>
                {atsMutation.data.suggestions && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Suggestions</p>
                    {atsMutation.data.suggestions.map((s, i) => (
                      <div key={i} className="rounded-md border p-3 text-sm">
                        <div className="mb-1 flex items-center gap-2">
                          <Badge
                            variant={
                              s.severity === "high" ? "destructive" : s.severity === "medium" ? "warning" : "secondary"
                            }
                          >
                            {s.severity}
                          </Badge>
                          <span className="font-medium">{s.issue}</span>
                        </div>
                        <p className="text-muted-foreground">{s.recommendation}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
