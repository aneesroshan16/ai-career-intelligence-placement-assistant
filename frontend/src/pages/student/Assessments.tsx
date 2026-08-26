import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import { Skeleton } from "@/components/ui/skeleton";
import {
  generateCodingProblem,
  getAptitudeTest,
  submitAptitudeTest,
  submitCode,
} from "@/lib/api/assessmentModules";
import { motion, AnimatePresence } from "framer-motion";
import { Code2, BrainCircuit, CheckCircle2, Trophy, Clock } from "lucide-react";
import { Progress } from "@/components/ui/progress";

import { getMe, listRoles } from "@/lib/api/resumeModules";

function CodingTab() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState<"python" | "java" | "c" | "cpp">("python");
  const { data: user } = useQuery({ queryKey: ["user"], queryFn: getMe });
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: listRoles });
  const targetRoleId = roles?.find((role) => role.name === user?.profile?.target_role)?.id;

  const generateMutation = useMutation({ mutationFn: () => generateCodingProblem(targetRoleId, "medium") });
  const submitMutation = useMutation({
    mutationFn: () => submitCode(generateMutation.data!.id, code, language),
  });
  const startChallenge = () => {
    setCode("");
    generateMutation.mutate();
  };

  const editorCode = code || generateMutation.data?.starter_code?.[language] || "";

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      {!generateMutation.data ? (
        <Card className="glass min-h-[300px] flex flex-col items-center justify-center p-8 text-center space-y-4">
          <Code2 className="h-16 w-16 text-primary/40" />
          <h3 className="text-xl font-bold">Coding Assessment</h3>
          <p className="text-muted-foreground max-w-md">
            Test your programming skills with an AI-generated coding challenge tailored to your target role.
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {(["python", "java", "c", "cpp"] as const).map((option) => (
              <Button key={option} type="button" variant={language === option ? "default" : "outline"} size="sm" onClick={() => setLanguage(option)}>
                {{ python: "Python", java: "Java", c: "C", cpp: "C++" }[option]}
              </Button>
            ))}
          </div>
          {generateMutation.isError && (
            <p className="text-sm text-destructive font-medium">
              Failed to generate coding challenge. Please check your connection and try again.
            </p>
          )}
          <Button size="lg" onClick={startChallenge} disabled={generateMutation.isPending} className="shadow-lg">
            {generateMutation.isPending ? "Generating Challenge..." : "Start Coding Test"}
          </Button>
        </Card>
      ) : (

        <Card className="glass overflow-hidden border-t-4 border-t-blue-500">
          <CardHeader className="bg-muted/10 border-b">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-xl mb-2">{generateMutation.data.title}</CardTitle>
                <Badge variant="secondary" className="bg-blue-500/10 text-blue-600 border-blue-200">
                  {generateMutation.data.difficulty}
                </Badge>
              </div>
              <Badge variant="outline" className="flex items-center gap-1 font-mono">
                <Clock className="h-3 w-3" /> 45:00
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            <div className="bg-muted/30 p-4 rounded-lg border text-sm text-foreground/90 leading-relaxed font-mono whitespace-pre-wrap">
              {generateMutation.data.statement}
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs font-semibold uppercase text-muted-foreground tracking-wider">Solution Workspace</span>
                <select aria-label="Programming language" value={language} onChange={(e) => { setLanguage(e.target.value as typeof language); setCode(""); }} className="rounded-md border bg-background px-2 py-1 text-xs font-medium">
                  <option value="python">Python 3</option>
                  <option value="java">Java</option>
                  <option value="c">C</option>
                  <option value="cpp">C++</option>
                </select>
              </div>
              <textarea
                className="w-full rounded-lg border bg-background/50 p-4 font-mono text-sm shadow-inner min-h-[300px] focus:ring-2 focus:ring-primary focus:border-primary transition-all resize-y"
                placeholder="Write your solution here..."
                value={editorCode}
                onChange={(e) => setCode(e.target.value)}
                spellCheck={false}
              />
            </div>
            
            <div className="flex justify-between items-center pt-4 border-t">
              <div>
                {submitMutation.data && (
                  <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
                    <div className="flex items-center gap-1 text-sm font-medium">
                      <Trophy className={`h-4 w-4 ${submitMutation.data.score === 100 ? "text-yellow-500" : "text-muted-foreground"}`} />
                      Score: {submitMutation.data.score}%
                    </div>
                    <Badge variant={submitMutation.data.passed_cases === submitMutation.data.total_cases ? "success" : "warning"}>
                      {submitMutation.data.passed_cases} / {submitMutation.data.total_cases} Cases
                    </Badge>
                  </motion.div>
                )}
                {submitMutation.data?.execution_log?.find((entry) => entry.stderr || entry.error) && (
                  <p className="mt-2 max-w-md text-xs text-destructive">
                    {submitMutation.data.execution_log.find((entry) => entry.stderr || entry.error)?.stderr || submitMutation.data.execution_log.find((entry) => entry.stderr || entry.error)?.error}
                  </p>
                )}
                {submitMutation.isError && <p className="text-sm text-destructive">The code could not be run. Check the selected language and try again.</p>}
              </div>
              <Button size="lg" onClick={() => submitMutation.mutate()} disabled={submitMutation.isPending || submitMutation.data?.score === 100}>
                {submitMutation.isPending ? "Running Tests..." : submitMutation.data ? "Submit Again" : "Run Code"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </motion.div>
  );
}

function AptitudeTab() {
  const { data: questions, isLoading } = useQuery({ queryKey: ["aptitude", "test"], queryFn: getAptitudeTest });
  const [answers, setAnswers] = useState<Record<string, number>>({});

  const submitMutation = useMutation({
    mutationFn: () =>
      submitAptitudeTest(Object.entries(answers).map(([question_id, selected_option]) => ({ question_id, selected_option }))),
  });

  const progressPercent = questions ? Math.round((Object.keys(answers).length / questions.length) * 100) : 0;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      
      {!submitMutation.data && (
        <Card className="glass sticky top-6 z-10">
          <CardContent className="p-4 flex items-center justify-between">
            <div className="flex-1 mr-8">
              <div className="flex justify-between text-xs font-medium mb-2">
                <span>Progress</span>
                <span>{Object.keys(answers).length} / {questions?.length || 0} Answered</span>
              </div>
              <Progress value={progressPercent} className="h-2" />
            </div>
            <Button 
              onClick={() => submitMutation.mutate()} 
              disabled={submitMutation.isPending || Object.keys(answers).length === 0}
            >
              {submitMutation.isPending ? "Scoring..." : "Submit Test"}
            </Button>
          </CardContent>
          {submitMutation.isError && (
            <p className="p-4 text-sm text-destructive font-medium text-center border-t bg-destructive/5">
              Failed to submit aptitude test. Please try again.
            </p>
          )}
        </Card>
      )}


      {submitMutation.data && (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
          <Card className="glass overflow-hidden border-t-4 border-t-emerald-500 mb-8">
            <div className="absolute top-0 right-0 p-8 text-emerald-500/10 pointer-events-none">
              <Trophy className="h-32 w-32" />
            </div>
            <CardHeader>
              <CardTitle className="text-2xl flex items-center gap-2">
                <CheckCircle2 className="h-6 w-6 text-emerald-500" />
                Assessment Complete
              </CardTitle>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="flex items-end gap-2 mb-8">
                <span className="text-5xl font-extrabold tracking-tight">{submitMutation.data.overall_score}%</span>
                <span className="text-muted-foreground font-medium mb-1">Overall Score</span>
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                {Object.entries(submitMutation.data.category_scores).map(([cat, score]) => (
                  <div key={cat} className="bg-muted/30 p-4 rounded-xl border">
                    <p className="text-xs uppercase tracking-wider text-muted-foreground font-semibold mb-1">{cat}</p>
                    <p className="text-2xl font-bold">{score}%</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-48 w-full rounded-xl" />
          <Skeleton className="h-48 w-full rounded-xl" />
          <Skeleton className="h-48 w-full rounded-xl" />
        </div>
      ) : (
        <div className="space-y-6">
          {questions?.map((q, index) => (
            <Card key={q.id} className={`transition-all duration-300 ${answers[q.id] !== undefined ? "glass border-primary/20" : "bg-card border-border"}`}>
              <CardHeader className="pb-4">
                <div className="flex gap-4">
                  <div className="h-8 w-8 shrink-0 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">
                    {index + 1}
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="secondary" className="capitalize text-xs">{q.category}</Badge>
                      <Badge variant="outline" className="text-xs text-muted-foreground">{q.difficulty || "medium"}</Badge>
                    </div>
                    <CardTitle className="text-base leading-relaxed">{q.question}</CardTitle>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pl-16">
                <div className="grid sm:grid-cols-2 gap-3">
                  {q.options.map((opt, i) => {
                    const isSelected = answers[q.id] === i;
                    return (
                      <Button
                        key={i}
                        variant="outline"
                        className={`h-auto min-h-12 py-3 px-4 justify-start text-left whitespace-normal border-2 ${isSelected ? "border-primary bg-primary/5 text-primary" : "hover:border-primary/40 hover:bg-muted/50"}`}
                        onClick={() => !submitMutation.data && setAnswers((prev) => ({ ...prev, [q.id]: i }))}
                        disabled={!!submitMutation.data}
                      >
                        <div className="flex gap-3">
                          <span className="font-mono text-muted-foreground shrink-0">{String.fromCharCode(65 + i)}.</span>
                          <span>{opt}</span>
                        </div>
                      </Button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </motion.div>
  );
}

export default function AssessmentsPage() {
  const [tab, setTab] = useState<"coding" | "aptitude">("coding");

  return (
    <motion.div 
      className="space-y-8 max-w-4xl mx-auto pb-12"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="space-y-2 text-center mb-8 relative z-10">
        <h1 className="text-4xl font-extrabold tracking-tight">Assessments</h1>
        <p className="text-lg text-muted-foreground">
          Validate your skills with dynamic coding challenges and aptitude tests.
        </p>
      </div>

      <div className="flex justify-center mb-8 relative z-10">
        <div className="inline-flex bg-muted/50 p-1 rounded-lg backdrop-blur-md border">
          <Button 
            variant={tab === "coding" ? "default" : "ghost"} 
            className={`rounded-md px-8 ${tab === "coding" ? "shadow-sm" : ""}`}
            onClick={() => setTab("coding")}
          >
            <Code2 className="mr-2 h-4 w-4" /> Coding Challenge
          </Button>
          <Button 
            variant={tab === "aptitude" ? "default" : "ghost"} 
            className={`rounded-md px-8 ${tab === "aptitude" ? "shadow-sm" : ""}`}
            onClick={() => setTab("aptitude")}
          >
            <BrainCircuit className="mr-2 h-4 w-4" /> Aptitude Test
          </Button>
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={tab}
          initial={{ opacity: 0, x: tab === "coding" ? -20 : 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: tab === "coding" ? 20 : -20 }}
          transition={{ duration: 0.3 }}
        >
          {tab === "coding" ? <CodingTab /> : <AptitudeTab />}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
}
