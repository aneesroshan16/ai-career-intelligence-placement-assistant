import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label, Progress } from "@/components/ui/form-elements";
import { predictPlacement } from "@/lib/api/assessmentModules";
import type { PlacementFeatures } from "@/types";

const DEFAULT_FEATURES: PlacementFeatures = {
  cgpa: 8.0,
  internships: 1,
  projects_count: 3,
  certifications_count: 2,
  skills_count: 10,
  coding_score: 65,
  aptitude_score: 60,
  ats_score: 70,
  interview_score: 60,
};

const FIELD_LABELS: Record<keyof PlacementFeatures, string> = {
  cgpa: "CGPA (0-10)",
  internships: "Internships",
  projects_count: "Projects",
  certifications_count: "Certifications",
  skills_count: "Skills Count",
  coding_score: "Coding Score (0-100)",
  aptitude_score: "Aptitude Score (0-100)",
  ats_score: "ATS Score (0-100)",
  interview_score: "Interview Score (0-100)",
};

export default function PlacementPage() {
  const [features, setFeatures] = useState<PlacementFeatures>(DEFAULT_FEATURES);
  const mutation = useMutation({ mutationFn: () => predictPlacement(features) });

  const handleChange = (key: keyof PlacementFeatures, value: string) => {
    setFeatures((prev) => ({ ...prev, [key]: Number(value) }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Placement Probability Prediction</h1>
        <p className="text-sm text-muted-foreground">
          ML-based estimate (Random Forest / XGBoost / CatBoost) of your placement likelihood.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Your Profile</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            {(Object.keys(features) as (keyof PlacementFeatures)[]).map((key) => (
              <div key={key} className="space-y-1.5">
                <Label htmlFor={key}>{FIELD_LABELS[key]}</Label>
                <Input
                  id={key}
                  type="number"
                  value={features[key]}
                  onChange={(e) => handleChange(key, e.target.value)}
                />
              </div>
            ))}
            <Button
              className="col-span-2 mt-2"
              onClick={() => mutation.mutate()}
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Predicting..." : "Predict Placement Probability"}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Prediction Result</CardTitle>
          </CardHeader>
          <CardContent>
            {mutation.data ? (
              <div className="space-y-4">
                <div className="text-center">
                  <p className="text-4xl font-bold">{Math.round(mutation.data.probability * 100)}%</p>
                  <p className="text-sm text-muted-foreground">
                    {mutation.data.predicted_label ? "Likely to be placed" : "Needs improvement"}
                  </p>
                </div>
                <Progress value={mutation.data.probability * 100} />
                <p className="text-center text-xs text-muted-foreground">
                  Model: {mutation.data.model_version}
                </p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                Fill in your profile and run a prediction to see your results here.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
