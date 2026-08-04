import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import { getRoadmap } from "@/lib/api/resumeModules";

export default function RoadmapPage() {
  const [searchParams] = useSearchParams();
  const roadmapId = searchParams.get("id");

  const { data: roadmap, isLoading } = useQuery({
    queryKey: ["roadmap", roadmapId],
    queryFn: () => getRoadmap(roadmapId!),
    enabled: !!roadmapId,
  });

  if (!roadmapId) {
    return (
      <p className="text-sm text-muted-foreground">
        No roadmap selected. Generate one from the Skill Gap Analysis page.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Your Learning Roadmap</h1>
        <p className="text-sm text-muted-foreground">
          {roadmap ? `${roadmap.total_weeks}-week personalized plan` : "Loading..."}
        </p>
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading roadmap...</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {roadmap?.plan.map((week) => (
            <Card key={week.week}>
              <CardHeader>
                <CardTitle className="text-base">Week {week.week}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap gap-1.5">
                  {week.focus_skills.map((skill) => (
                    <Badge key={skill} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
                <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
                  {week.tasks.map((task, i) => (
                    <li key={i}>{task}</li>
                  ))}
                </ul>
                <p className="text-xs text-muted-foreground">~{week.est_hours} hrs this week</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {roadmap && (
        <Card>
          <CardHeader>
            <CardTitle>Milestones</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {roadmap.milestones.map((m) => (
              <div key={m.month} className="flex items-start gap-3 text-sm">
                <Badge>{`Month ${m.month}`}</Badge>
                <div>
                  <p className="font-medium">{m.goal}</p>
                  <p className="text-muted-foreground">{m.deliverable}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
