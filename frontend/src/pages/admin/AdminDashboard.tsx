import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api/client";

interface DepartmentAnalytics {
  department_id: number;
  department_name: string;
  student_count: number;
  avg_cgpa: number | null;
  avg_internships: number | null;
  avg_readiness_score: number | null;
  avg_placement_probability: number | null;
}

async function getDepartmentAnalytics(): Promise<DepartmentAnalytics[]> {
  const res = await apiClient.get("/admin/analytics/department");
  return res.data.data;
}

export default function AdminDashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ["admin", "department-analytics"], queryFn: getDepartmentAnalytics });

  const handleExport = () => {
    window.open(`${apiClient.defaults.baseURL}/admin/analytics/export?format=csv`, "_blank");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Admin Analytics</h1>
          <p className="text-sm text-muted-foreground">Department-level placement readiness overview.</p>
        </div>
        <Button variant="outline" onClick={handleExport}>
          Export CSV
        </Button>
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading...</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data?.map((dept) => (
            <Card key={dept.department_id}>
              <CardHeader>
                <CardTitle className="text-base">{dept.department_name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1 text-sm text-muted-foreground">
                <p>Students: {dept.student_count}</p>
                <p>Avg CGPA: {dept.avg_cgpa ?? "—"}</p>
                <p>Avg Internships: {dept.avg_internships ?? "—"}</p>
                <p>Avg Readiness: {dept.avg_readiness_score ?? "—"}%</p>
                <p>Avg Placement Probability: {dept.avg_placement_probability ?? "—"}%</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
