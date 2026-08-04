import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import { getRecommendedJobs, listJobs } from "@/lib/api/assessmentModules";

export default function JobsPage() {
  const { data: recommended, isLoading: loadingRecommended } = useQuery({
    queryKey: ["jobs", "recommended"],
    queryFn: getRecommendedJobs,
    retry: false,
  });
  const { data: allJobs } = useQuery({ queryKey: ["jobs", "all"], queryFn: () => listJobs() });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Jobs & Recommendations</h1>
        <p className="text-sm text-muted-foreground">
          Personalized matches (via resume embeddings) and all open postings.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recommended For You</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {loadingRecommended ? (
            <p className="text-sm text-muted-foreground">Loading recommendations...</p>
          ) : recommended?.length ? (
            recommended.map((match) => (
              <div key={match.job_id} className="flex items-center justify-between rounded-md border p-3">
                <div>
                  <p className="text-sm font-medium">{match.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {match.company_name} · {match.location} · {match.job_type}
                  </p>
                </div>
                <Badge>{Math.round(match.similarity_score * 100)}% match</Badge>
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">
              Upload and process a resume to see personalized job matches.
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>All Open Positions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {allJobs?.map((job) => (
            <div key={job.id} className="flex items-center justify-between rounded-md border p-3">
              <div>
                <p className="text-sm font-medium">{job.title}</p>
                <p className="text-xs text-muted-foreground">
                  {job.location} · {job.job_type} · {job.experience_min}-{job.experience_max ?? "∞"} yrs
                </p>
              </div>
              <div className="flex flex-wrap gap-1">
                {job.required_skills?.slice(0, 3).map((s) => (
                  <Badge key={s} variant="secondary">
                    {s}
                  </Badge>
                ))}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
