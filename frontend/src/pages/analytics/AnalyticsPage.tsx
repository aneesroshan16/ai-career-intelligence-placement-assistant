import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api/client";

interface SkillDemand {
  skill: string;
  demand_count: number;
}
interface PlacementTrend {
  month: string;
  avg_predicted_probability: number;
  sample_size: number;
}

async function getSkillDemand(): Promise<SkillDemand[]> {
  return (await apiClient.get("/analytics/skill-demand")).data.data;
}
async function getPlacementTrends(): Promise<PlacementTrend[]> {
  return (await apiClient.get("/analytics/placement-trends")).data.data;
}

export default function AnalyticsPage() {
  const { data: skillDemand } = useQuery({ queryKey: ["analytics", "skill-demand"], queryFn: getSkillDemand });
  const { data: placementTrends } = useQuery({ queryKey: ["analytics", "placement-trends"], queryFn: getPlacementTrends });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Platform Analytics</h1>
        <p className="text-sm text-muted-foreground">Skill demand and placement probability trends across the cohort.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Top In-Demand Skills</CardTitle>
        </CardHeader>
        <CardContent className="h-80">
          {skillDemand?.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={skillDemand} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="skill" width={100} />
                <Tooltip />
                <Bar dataKey="demand_count" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-muted-foreground">No active job postings with skill data yet.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Placement Probability Trend (Monthly)</CardTitle>
        </CardHeader>
        <CardContent className="h-80">
          {placementTrends?.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={placementTrends}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="month" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="avg_predicted_probability" fill="hsl(217 91% 60%)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-muted-foreground">No placement predictions recorded yet.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
