import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import { startInterview, submitInterviewAnswer } from "@/lib/api/assessmentModules";

export default function InterviewPage() {
  const [mode, setMode] = useState<"hr" | "technical" | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [question, setQuestion] = useState<string | null>(null);
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState<string>("not_started");
  const [lastFeedback, setLastFeedback] = useState<Record<string, unknown> | null>(null);

  const startMutation = useMutation({
    mutationFn: (m: "hr" | "technical") => startInterview(m),
    onSuccess: (result) => {
      setSessionId(result.session.id);
      setQuestion(result.first_question);
      setStatus("in_progress");
    },
  });

  const answerMutation = useMutation({
    mutationFn: () => submitInterviewAnswer(sessionId!, answer),
    onSuccess: (result) => {
      setLastFeedback(result.feedback as Record<string, unknown>);
      setQuestion(result.next_question);
      setStatus(result.session_status);
      setAnswer("");
    },
  });

  if (!mode) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">AI Interview Simulator</h1>
          <p className="text-sm text-muted-foreground">Choose an interview mode to begin.</p>
        </div>
        <div className="flex gap-4">
          <Button onClick={() => setMode("hr")}>HR Interview</Button>
          <Button variant="outline" onClick={() => setMode("technical")}>
            Technical Interview
          </Button>
        </div>
      </div>
    );
  }

  if (!sessionId) {
    return (
      <div className="space-y-4">
        <Button onClick={() => startMutation.mutate(mode)} disabled={startMutation.isPending}>
          {startMutation.isPending ? "Starting..." : `Start ${mode.toUpperCase()} Interview`}
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold capitalize">{mode} Interview</h1>
        <Badge variant={status === "completed" ? "success" : "warning"}>{status}</Badge>
      </div>

      {status !== "completed" && question && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{question}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <textarea
              className="w-full rounded-md border bg-background p-3 text-sm"
              rows={5}
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer..."
            />
            <Button onClick={() => answerMutation.mutate()} disabled={!answer || answerMutation.isPending}>
              {answerMutation.isPending ? "Evaluating..." : "Submit Answer"}
            </Button>
          </CardContent>
        </Card>
      )}

      {lastFeedback && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Feedback on Previous Answer</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex gap-4">
              <span>Clarity: {String(lastFeedback.clarity)}/10</span>
              <span>Correctness: {String(lastFeedback.correctness)}/10</span>
              <span>Confidence: {String(lastFeedback.confidence)}/10</span>
            </div>
            <ul className="list-inside list-disc text-muted-foreground">
              {((lastFeedback.tips as string[]) ?? []).map((tip, i) => (
                <li key={i}>{tip}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {status === "completed" && (
        <p className="text-sm text-muted-foreground">
          Interview complete — check your dashboard for the aggregated feedback summary.
        </p>
      )}
    </div>
  );
}
