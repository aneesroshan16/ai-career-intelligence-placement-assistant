import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import {
  generateCodingProblem,
  getAptitudeTest,
  submitAptitudeTest,
  submitCode,
} from "@/lib/api/assessmentModules";

function CodingTab() {
  const [code, setCode] = useState("");
  const generateMutation = useMutation({ mutationFn: () => generateCodingProblem(undefined, "medium") });
  const submitMutation = useMutation({
    mutationFn: () => submitCode(generateMutation.data!.id, code),
  });

  return (
    <div className="space-y-4">
      <Button onClick={() => generateMutation.mutate()} disabled={generateMutation.isPending}>
        {generateMutation.isPending ? "Generating..." : "Generate Coding Problem"}
      </Button>

      {generateMutation.data && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {generateMutation.data.title}{" "}
              <Badge variant="secondary" className="ml-2">
                {generateMutation.data.difficulty}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="whitespace-pre-wrap text-sm text-muted-foreground">{generateMutation.data.statement}</p>
            <textarea
              className="w-full rounded-md border bg-background p-3 font-mono text-sm"
              rows={10}
              value={code || generateMutation.data.starter_code?.python || ""}
              onChange={(e) => setCode(e.target.value)}
            />
            <Button onClick={() => submitMutation.mutate()} disabled={submitMutation.isPending}>
              {submitMutation.isPending ? "Running..." : "Submit Solution"}
            </Button>
            {submitMutation.data && (
              <p className="text-sm">
                Passed {submitMutation.data.passed_cases}/{submitMutation.data.total_cases} test cases —{" "}
                <span className="font-semibold">{submitMutation.data.score}%</span>
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function AptitudeTab() {
  const { data: questions } = useQuery({ queryKey: ["aptitude", "test"], queryFn: getAptitudeTest });
  const [answers, setAnswers] = useState<Record<string, number>>({});

  const submitMutation = useMutation({
    mutationFn: () =>
      submitAptitudeTest(Object.entries(answers).map(([question_id, selected_option]) => ({ question_id, selected_option }))),
  });

  return (
    <div className="space-y-4">
      {questions?.map((q) => (
        <Card key={q.id}>
          <CardHeader>
            <CardTitle className="text-sm">
              <Badge variant="secondary" className="mr-2 capitalize">
                {q.category}
              </Badge>
              {q.question}
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-2">
            {q.options.map((opt, i) => (
              <Button
                key={i}
                size="sm"
                variant={answers[q.id] === i ? "default" : "outline"}
                onClick={() => setAnswers((prev) => ({ ...prev, [q.id]: i }))}
              >
                {opt}
              </Button>
            ))}
          </CardContent>
        </Card>
      ))}

      {questions?.length ? (
        <Button onClick={() => submitMutation.mutate()} disabled={submitMutation.isPending}>
          {submitMutation.isPending ? "Scoring..." : "Submit Test"}
        </Button>
      ) : null}

      {submitMutation.data && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-lg font-semibold">Overall: {submitMutation.data.overall_score}%</p>
            <div className="mt-2 flex gap-4 text-sm text-muted-foreground">
              {Object.entries(submitMutation.data.category_scores).map(([cat, score]) => (
                <span key={cat} className="capitalize">
                  {cat}: {score}%
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function AssessmentsPage() {
  const [tab, setTab] = useState<"coding" | "aptitude">("coding");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Assessments</h1>
        <p className="text-sm text-muted-foreground">Coding challenges and aptitude tests.</p>
      </div>
      <div className="flex gap-2">
        <Button variant={tab === "coding" ? "default" : "outline"} size="sm" onClick={() => setTab("coding")}>
          Coding
        </Button>
        <Button variant={tab === "aptitude" ? "default" : "outline"} size="sm" onClick={() => setTab("aptitude")}>
          Aptitude
        </Button>
      </div>
      {tab === "coding" ? <CodingTab /> : <AptitudeTab />}
    </div>
  );
}
