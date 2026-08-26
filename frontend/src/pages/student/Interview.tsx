import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/form-elements";
import { getInterviewSession, listInterviewSessions, startInterview, submitInterviewAnswer } from "@/lib/api/assessmentModules";
import { getMe, listRoles } from "@/lib/api/resumeModules";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, User, Mic, Send, Lightbulb, Activity, CheckCircle2, AlertTriangle, ShieldCheck } from "lucide-react";

export default function InterviewPage() {
  const [mode, setMode] = useState<"hr" | "technical" | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [question, setQuestion] = useState<string | null>(null);
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState<string>("not_started");
  const [lastFeedback, setLastFeedback] = useState<Record<string, unknown> | null>(null);
  const [history, setHistory] = useState<{q: string, a: string, f?: Record<string, unknown>}[]>([]);
  const { data: user } = useQuery({ queryKey: ["user"], queryFn: getMe });
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: listRoles });
  const { data: sessions } = useQuery({ queryKey: ["interview", "sessions"], queryFn: listInterviewSessions });
  const resumableSession = sessions?.find((item) => item.status === "in_progress");
  const { data: savedSession } = useQuery({
    queryKey: ["interview", "session", resumableSession?.id],
    queryFn: () => getInterviewSession(resumableSession!.id),
    enabled: !!resumableSession && !sessionId,
  });
  const targetRoleId = roles?.find((role) => role.name === user?.profile?.target_role)?.id;

  useEffect(() => {
    if (!savedSession || sessionId) return;

    const turns = [...savedSession.turns].sort((a, b) => a.turn_number - b.turn_number);
    const currentTurn = turns.at(-1);
    setMode(savedSession.mode);
    setSessionId(savedSession.id);
    setStatus(savedSession.status);
    setQuestion(currentTurn?.answer ? null : currentTurn?.question ?? null);
    setHistory(turns.filter((turn) => turn.answer).map((turn) => ({
      q: turn.question,
      a: turn.answer!,
      f: turn.feedback ?? undefined,
    })));
  }, [savedSession, sessionId]);

  const startMutation = useMutation({
    mutationFn: (m: "hr" | "technical") => startInterview(m, targetRoleId),
    onSuccess: (result) => {
      setSessionId(result.session.id);
      setQuestion(result.first_question);
      setStatus("in_progress");
      setHistory([]);
      setLastFeedback(null);
    },
  });

  const answerMutation = useMutation({
    mutationFn: () => submitInterviewAnswer(sessionId!, answer),
    onSuccess: (result) => {
      const feedback = result.feedback as Record<string, unknown>;
      setHistory(prev => [...prev, { q: question!, a: answer, f: feedback }]);
      setLastFeedback(feedback);
      setQuestion(result.next_question);
      setStatus(result.session_status);
      setAnswer("");
    },
  });

  if (!mode) {
    return (
      <motion.div 
        className="space-y-8 max-w-4xl mx-auto pb-12 text-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="space-y-2 mb-12">
          <h1 className="text-4xl font-extrabold tracking-tight">AI Interview Simulator</h1>
          <p className="text-lg text-muted-foreground">Practice real-world interview scenarios with our AI recruiter.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto">
          <Card className="glass glass-hover cursor-pointer transition-all hover:border-primary/50 group" onClick={() => setMode("hr")}>
            <CardContent className="p-8 flex flex-col items-center justify-center space-y-4">
              <div className="h-16 w-16 rounded-full bg-blue-500/10 text-blue-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                <User className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-bold">HR Interview</h3>
              <p className="text-sm text-muted-foreground">Behavioral questions, culture fit, and soft skills assessment.</p>
            </CardContent>
          </Card>

          <Card className="glass glass-hover cursor-pointer transition-all hover:border-primary/50 group" onClick={() => setMode("technical")}>
            <CardContent className="p-8 flex flex-col items-center justify-center space-y-4">
              <div className="h-16 w-16 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                <ShieldCheck className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-bold">Technical Interview</h3>
              <p className="text-sm text-muted-foreground">Role-specific concepts, problem-solving, and system design.</p>
            </CardContent>
          </Card>
        </div>
      </motion.div>
    );
  }

  if (!sessionId) {
    return (
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="max-w-2xl mx-auto mt-20">
        <Card className="glass p-12 text-center flex flex-col items-center space-y-6">
          <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center">
            <Bot className="h-10 w-10 text-primary animate-pulse" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-bold capitalize">{mode} Interview Initialization</h2>
            <p className="text-muted-foreground">The AI is reviewing your resume and target role to prepare specific questions.</p>
          </div>
          <Button size="lg" onClick={() => startMutation.mutate(mode)} disabled={startMutation.isPending} className="mt-4 shadow-lg">
            {startMutation.isPending ? "Connecting to AI..." : "Start Interview Session"}
          </Button>
          <Button variant="ghost" onClick={() => setMode(null)} disabled={startMutation.isPending}>Back</Button>
        </Card>
      </motion.div>
    );
  }

  return (
    <motion.div 
      className="max-w-4xl mx-auto space-y-6 pb-12 flex flex-col h-[calc(100vh-120px)]"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }}
    >
      <div className="flex items-center justify-between bg-card border rounded-xl p-4 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
            <Bot className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-lg font-bold capitalize leading-tight">AI Recruiter ({mode})</h1>
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <span className="relative flex h-2 w-2">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${status === 'in_progress' ? 'bg-green-400' : 'bg-muted'}`}></span>
                <span className={`relative inline-flex rounded-full h-2 w-2 ${status === 'in_progress' ? 'bg-green-500' : 'bg-muted-foreground'}`}></span>
              </span>
              {status === 'in_progress' ? 'Active Session' : 'Completed'}
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={() => { setMode(null); setSessionId(null); }}>End Session</Button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-6 p-2 scroll-smooth pr-4 custom-scrollbar">
        {history.map((item, idx) => (
          <div key={idx} className="space-y-6">
            {/* AI Question */}
            <div className="flex gap-4">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-1">
                <Bot className="h-4 w-4 text-primary" />
              </div>
              <div className="bg-muted/50 border rounded-2xl rounded-tl-sm p-4 text-sm max-w-[80%]">
                {item.q}
              </div>
            </div>

            {/* User Answer */}
            <div className="flex gap-4 justify-end">
              <div className="bg-primary text-primary-foreground rounded-2xl rounded-tr-sm p-4 text-sm max-w-[80%]">
                {item.a}
              </div>
              <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center shrink-0 mt-1">
                <User className="h-4 w-4" />
              </div>
            </div>

            {/* AI Feedback */}
            {item.f && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="pl-12 pr-12">
                <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-4 text-xs space-y-3">
                  <div className="flex items-center gap-2 font-semibold text-amber-700 dark:text-amber-400">
                    <Activity className="h-4 w-4" /> Instant Feedback
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="bg-background/50 rounded p-2 text-center border">
                      <p className="text-muted-foreground mb-0.5">Clarity</p>
                      <p className="font-bold text-sm">{String(item.f.clarity)}/10</p>
                    </div>
                    <div className="bg-background/50 rounded p-2 text-center border">
                      <p className="text-muted-foreground mb-0.5">Correctness</p>
                      <p className="font-bold text-sm">{String(item.f.correctness)}/10</p>
                    </div>
                    <div className="bg-background/50 rounded p-2 text-center border">
                      <p className="text-muted-foreground mb-0.5">Confidence</p>
                      <p className="font-bold text-sm">{String(item.f.confidence)}/10</p>
                    </div>
                  </div>
                  {Array.isArray(item.f.tips) && item.f.tips.length > 0 && (
                    <ul className="space-y-1 mt-2">
                      {(item.f.tips as string[]).map((tip, i) => (
                        <li key={i} className="flex gap-1.5 items-start text-muted-foreground">
                          <Lightbulb className="h-3.5 w-3.5 text-amber-500 shrink-0 mt-0.5" /> <span>{String(tip)}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        ))}

        {status !== "completed" && question && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex gap-4 pt-4">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-1">
              <Bot className="h-4 w-4 text-primary" />
            </div>
            <div className="bg-muted/50 border rounded-2xl rounded-tl-sm p-4 text-sm max-w-[80%] shadow-sm">
              {question}
            </div>
          </motion.div>
        )}

        {status === "completed" && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center justify-center py-12 text-center space-y-4">
            <div className="h-16 w-16 rounded-full bg-success/20 text-success flex items-center justify-center">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <h3 className="text-2xl font-bold">Interview Completed</h3>
            <p className="text-muted-foreground max-w-md">Your responses have been recorded. Check your dashboard for the aggregated feedback summary.</p>
            <Button onClick={() => { setMode(null); setSessionId(null); }}>Return to Menu</Button>
          </motion.div>
        )}
      </div>

      {status !== "completed" && (
        <div className="pt-4 border-t bg-background relative z-10">
          <div className="relative flex items-end gap-2">
            <textarea
              className="w-full rounded-2xl border bg-muted/20 p-4 pr-12 text-sm resize-none focus:ring-1 focus:ring-primary min-h-[60px] max-h-[150px]"
              rows={2}
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your response... (or use voice)"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (answer && !answerMutation.isPending) answerMutation.mutate();
                }
              }}
            />
            <div className="absolute right-14 bottom-3">
              <Button size="icon" variant="ghost" className="h-8 w-8 rounded-full text-muted-foreground hover:text-primary">
                <Mic className="h-4 w-4" />
              </Button>
            </div>
            <Button 
              size="icon" 
              className="h-[52px] w-[52px] rounded-full shrink-0 shadow-md" 
              onClick={() => answerMutation.mutate()} 
              disabled={!answer || answerMutation.isPending}
            >
              <Send className="h-5 w-5 ml-1" />
            </Button>
          </div>
          <p className="text-[10px] text-center text-muted-foreground mt-2">Press Enter to send, Shift+Enter for new line.</p>
        </div>
      )}
    </motion.div>
  );
}
