import { useRef, useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge, Progress } from "@/components/ui/form-elements";
import { analyzeATS, listResumes, uploadResume, getLatestATSReport, getMe, listRoles } from "@/lib/api/resumeModules";
import { CheckCircle2, AlertTriangle, FileText, Search, ArrowRight, UploadCloud, XCircle, Sparkles } from "lucide-react";
import type { ComprehensiveATSAnalysis, ResumeSummary } from "@/types";
import { motion } from "framer-motion";

const containerVars = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.15 } }
};

const itemVars: any = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export default function ResumeUploadPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const [loadingStateIndex, setLoadingStateIndex] = useState(0);

  const loadingMessages = [
    "Analyzing your resume...",
    "Extracting resume content...",
    "Checking ATS compatibility...",
    "Matching your skills with career roles...",
    "Finalizing report..."
  ];

  const { data: resumes } = useQuery<ResumeSummary[]>({ queryKey: ["resumes"], queryFn: listResumes });
  const { data: user } = useQuery({ queryKey: ["user"], queryFn: getMe });
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: listRoles });
  const activeResume = resumes?.find((r) => r.is_active);
  const targetRoleId = roles?.find((role) => role.name === user?.profile?.target_role)?.id;

  const { data: latestReport, refetch: refetchReport } = useQuery({
    queryKey: ["atsReport", activeResume?.id],
    queryFn: () => getLatestATSReport(activeResume!.id),
    enabled: !!activeResume && activeResume.parse_status === "completed",
    retry: false
  });

  const uploadMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["resumes"] }),
  });

  const atsMutation = useMutation({
    mutationFn: () => analyzeATS(activeResume!.id, targetRoleId),
    onSuccess: () => {
      refetchReport();
    }
  });

  useEffect(() => {
    let interval: number | ReturnType<typeof setInterval>;
    if (atsMutation.isPending) {
      interval = setInterval(() => {
        setLoadingStateIndex((prev) => (prev < loadingMessages.length - 1 ? prev + 1 : prev));
      }, 1500);
    } else {
      setLoadingStateIndex(0);
    }
    return () => clearInterval(interval);
  }, [atsMutation.isPending]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadMutation.mutate(file);
  };

  const comprehensiveAnalysis: ComprehensiveATSAnalysis | null = 
    latestReport?.suggestions && latestReport.suggestions.length > 0 && 'category_scores' in latestReport.suggestions[0] 
      ? (latestReport.suggestions[0] as ComprehensiveATSAnalysis) 
      : null;

  return (
    <motion.div 
      className="space-y-8 max-w-5xl mx-auto pb-12 relative"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Subtle animated background elements */}
      <div className="absolute top-20 -left-10 w-64 h-64 bg-primary/20 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob pointer-events-none"></div>
      <div className="absolute top-40 -right-10 w-64 h-64 bg-blue-500/20 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-2000 pointer-events-none"></div>

      <div className="relative z-10 text-center space-y-2 mb-10">
        <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
          Resume & ATS Analyzer
        </h1>
        <p className="text-base text-muted-foreground mt-1 max-w-2xl mx-auto">
          Upload your resume to extract skills, instantly check ATS readiness, and get personalized career role recommendations powered by AI.
        </p>
      </div>

      {/* Always render the hidden input so it can be triggered from anywhere */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx"
        className="hidden"
        onChange={handleFileChange}
      />

      {!activeResume && (
      <Card className="glass glass-hover relative overflow-hidden group z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <CardContent className="p-10 flex flex-col items-center justify-center text-center space-y-6 relative z-10">
          <UploadCloud className="h-12 w-12 text-muted-foreground" />
          <div className="space-y-1">
            <h3 className="font-semibold text-lg">Upload your Resume</h3>
            <p className="text-sm text-muted-foreground">Supported formats: PDF, DOCX</p>
          </div>
          <Button 
            onClick={() => fileInputRef.current?.click()} 
            disabled={uploadMutation.isPending}
            size="lg"
            className="w-full sm:w-auto"
          >
            {uploadMutation.isPending ? "Uploading & parsing..." : "Choose PDF or DOCX"}
          </Button>

          {uploadMutation.isError && (
            <p className="text-sm text-destructive mt-2 flex items-center gap-1">
              <XCircle className="h-4 w-4" /> An error occurred during upload. Check your connection or try a different file.
            </p>
          )}
        </CardContent>
      </Card>
      )}

      {activeResume && (
        <Card className="border-primary/20 shadow-md">
          <CardHeader className="bg-muted/30 pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              Uploaded Resume
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 border rounded-lg bg-card">
              <div className="flex items-center gap-3">
                <FileText className="h-8 w-8 text-blue-500" />
                <div>
                  <p className="font-medium">{activeResume.original_filename}</p>
                  <p className="text-xs text-muted-foreground uppercase">{activeResume.file_type} Document</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={activeResume.parse_status === "completed" ? "success" : "warning"}>
                  {activeResume.parse_status === "completed" ? "Ready for Analysis" : "Parsing..."}
                </Badge>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => activeResume.file_url ? window.open(activeResume.file_url, "_blank") : alert("Resume file URL not available.")}
                >
                  View Resume
                </Button>
                <Button 
                  variant="default" 
                  size="sm" 
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadMutation.isPending}
                >
                  {uploadMutation.isPending ? "Uploading..." : "Upload New Resume"}
                </Button>
              </div>
            </div>

            {activeResume.parse_status === "completed" && (
              <div className="flex flex-col items-center justify-center p-6 border rounded-lg bg-muted/10 space-y-4">
                <h3 className="text-xl font-semibold">Resume Analysis</h3>
                <p className="text-sm text-muted-foreground text-center max-w-md">
                  Run our AI-powered ATS analyzer to score your resume, identify gaps, and discover your best-fit career roles.
                </p>
                <Button
                  size="lg"
                  disabled={atsMutation.isPending}
                  onClick={() => atsMutation.mutate()}
                  className="w-full sm:w-auto font-semibold shadow-lg hover:shadow-xl transition-all"
                >
                  <Search className="mr-2 h-5 w-5" />
                  {atsMutation.isPending || atsMutation.isSuccess && !comprehensiveAnalysis ? "Analyzing..." : "Analyze ATS Score"}
                </Button>

                {atsMutation.isPending && (
                  <div className="flex flex-col items-center space-y-2 text-primary animate-pulse mt-4">
                    <p className="font-medium">{loadingMessages[loadingStateIndex]}</p>
                    <Progress value={(loadingStateIndex + 1) * 20} className="w-64 h-2" />
                  </div>
                )}
                {atsMutation.isError && (
                  <p className="text-sm text-destructive mt-2 flex items-center gap-1">
                    <AlertTriangle className="h-4 w-4" /> Resume analysis could not be completed right now. Please try again.
                  </p>
                )}
              </div>
            )}

            {activeResume.parse_status === "failed" && (
              <div className="flex flex-col items-center justify-center p-6 border border-destructive/20 rounded-lg bg-destructive/5 space-y-4 text-center">
                <AlertTriangle className="h-10 w-10 text-destructive mb-2" />
                <h3 className="text-xl font-semibold text-destructive">Resume Parsing Failed</h3>
                <p className="text-sm text-muted-foreground max-w-md">
                  We encountered an error while trying to process this resume. This can happen if the file is corrupted, encrypted, or if the AI services are temporarily unavailable.
                </p>
                <Button variant="outline" onClick={() => document.querySelector('input[type="file"]')?.dispatchEvent(new MouseEvent('click'))}>
                  Upload a New Resume
                </Button>
              </div>
            )}

            {activeResume.parse_status === "pending" || activeResume.parse_status === "processing" ? (
              <div className="flex flex-col items-center justify-center p-8 border rounded-lg bg-muted/10 space-y-4 text-center">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mb-2"></div>
                <h3 className="text-xl font-semibold">Processing Resume...</h3>
                <p className="text-sm text-muted-foreground max-w-md">
                  We are securely extracting text and analyzing your resume structure. This usually takes just a few seconds.
                </p>
              </div>
            ) : null}
          </CardContent>
        </Card>
      )}

      {comprehensiveAnalysis && !atsMutation.isPending && (
        <motion.div 
          className="space-y-8 relative z-10"
          variants={containerVars}
          initial="hidden"
          animate="show"
        >
          
          {/* ATS Score and Breakdown */}
          <div className="grid md:grid-cols-2 gap-6">
            <motion.div variants={itemVars}>
              <Card className="flex flex-col items-center justify-center p-8 border-t-4 border-t-primary h-full glass glass-hover">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" /> ATS Score
                </h2>
              <div className="relative flex items-center justify-center">
                <svg className="w-40 h-40 transform -rotate-90">
                  <circle cx="80" cy="80" r="70" fill="transparent" stroke="currentColor" strokeWidth="10" className="text-muted" />
                  <circle 
                    cx="80" cy="80" r="70" fill="transparent" stroke="currentColor" strokeWidth="10" 
                    strokeDasharray={440} strokeDashoffset={440 - (440 * comprehensiveAnalysis.overall_score) / 100}
                    className="text-primary transition-all duration-1000 ease-out" 
                  />
                </svg>
                <div className="absolute flex flex-col items-center justify-center">
                  <span className="text-4xl font-extrabold">{comprehensiveAnalysis.overall_score}</span>
                  <span className="text-sm text-muted-foreground font-medium">/ 100</span>
                </div>
              </div>
              <p className="mt-6 font-medium text-lg">
                {comprehensiveAnalysis.overall_score >= 80 ? "Excellent" : comprehensiveAnalysis.overall_score >= 60 ? "Good" : "Needs Work"}
              </p>
              </Card>
            </motion.div>

            <motion.div variants={itemVars}>
              <Card className="h-full glass glass-hover">
                <CardHeader>
                  <CardTitle>Score Breakdown</CardTitle>
                </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { label: "Resume Structure", score: comprehensiveAnalysis.category_scores.structure },
                  { label: "Keywords", score: comprehensiveAnalysis.category_scores.keywords },
                  { label: "Skills", score: comprehensiveAnalysis.category_scores.skills },
                  { label: "Experience", score: comprehensiveAnalysis.category_scores.experience },
                  { label: "Projects", score: comprehensiveAnalysis.category_scores.projects },
                  { label: "Education", score: comprehensiveAnalysis.category_scores.education },
                  { label: "ATS Compatibility", score: comprehensiveAnalysis.category_scores.ats_compatibility },
                  { label: "Contact Information", score: comprehensiveAnalysis.category_scores.contact_info },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{item.label}</span>
                    <div className="flex items-center gap-3 w-1/2">
                      <Progress value={item.score} className="h-2 flex-1" />
                      <span className="font-semibold w-8 text-right">{item.score}%</span>
                    </div>
                  </div>
                ))}
              </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* AI Resume Summary */}
          <motion.div variants={itemVars}>
            <Card className="glass glass-hover">
              <CardHeader className="bg-primary/5 border-b border-primary/10">
                <CardTitle className="text-lg flex items-center gap-2 text-primary">
                  <FileText className="h-5 w-5" />
                  AI Resume Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6 text-sm leading-relaxed italic border-l-4 border-primary ml-4 mb-4 mt-4">
                "{comprehensiveAnalysis.resume_summary}"
              </CardContent>
            </Card>
          </motion.div>

          {/* Strengths & Weaknesses */}
          <div className="grid md:grid-cols-2 gap-6">
            <motion.div variants={itemVars}>
              <Card className="border-l-4 border-l-green-500 h-full glass glass-hover hover:-translate-y-1">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                  Resume Strengths
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {comprehensiveAnalysis.strengths.map((str, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <div className="h-1.5 w-1.5 rounded-full bg-green-500 mt-1.5 shrink-0" />
                      <span>{str}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={itemVars}>
              <Card className="border-l-4 border-l-orange-500 h-full glass glass-hover hover:-translate-y-1">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-orange-500" />
                  Areas to Improve
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {comprehensiveAnalysis.areas_to_improve.map((area, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <div className="h-1.5 w-1.5 rounded-full bg-orange-500 mt-1.5 shrink-0" />
                      <span>{area}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Missing Keywords */}
          <motion.div variants={itemVars}>
            <Card className="glass glass-hover">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                <Search className="h-5 w-5 text-primary" />
                Missing Keywords for Tech Roles
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {comprehensiveAnalysis.missing_keywords.map((kw, i) => (
                  <Badge key={i} variant="outline" className="border-primary/50 text-primary bg-primary/5 px-3 py-1">
                    {kw}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
          </motion.div>

          {/* Recommended Roles */}
          <motion.div variants={itemVars} className="space-y-4 pt-4">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <ArrowRight className="h-6 w-6 text-primary" />
              Recommended Career Roles
            </h2>
            <div className="grid md:grid-cols-3 gap-6">
              {comprehensiveAnalysis.recommended_roles.map((role, i) => (
                <motion.div 
                  key={i} 
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1 }}
                >
                  <Card className="h-full flex flex-col relative overflow-hidden group glass glass-hover hover:-translate-y-2">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <div className="absolute top-0 right-0 bg-gradient-to-l from-primary to-blue-500 text-primary-foreground px-4 py-1.5 text-xs font-bold rounded-bl-xl shadow-md">
                    {role.match_percentage}% MATCH
                  </div>
                  <CardHeader className="pb-3 pt-6">
                    <CardTitle className="text-lg pr-12">{role.role_name}</CardTitle>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col gap-4 text-sm z-10">
                    <div className="space-y-1">
                      <p className="font-semibold text-xs uppercase text-muted-foreground tracking-wider">Why it matches</p>
                      <ul className="space-y-1">
                        {role.why_matches.map((w, j) => (
                          <li key={j} className="flex items-start gap-1.5">
                            <CheckCircle2 className="h-3.5 w-3.5 text-green-500 mt-0.5 shrink-0" />
                            <span className="leading-snug">{w}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    {role.missing_skills.length > 0 && (
                      <div className="space-y-1 mt-auto pt-4 border-t">
                        <p className="font-semibold text-xs uppercase text-muted-foreground tracking-wider">Skills to add</p>
                        <p className="text-muted-foreground text-xs leading-relaxed">
                          {role.missing_skills.join(", ")}
                        </p>
                      </div>
                    )}
                    <Button 
                      className="w-full mt-4" 
                      onClick={() => {
                        import('@/lib/api/resumeModules').then(({ updateMe }) => {
                          updateMe({ target_role: role.role_name }).then(() => {
                            window.location.href = '/skills';
                          });
                        });
                      }}
                    >
                      Select as Target Role
                    </Button>
                  </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Actionable Improvements */}
          <motion.div variants={itemVars}>
            <Card className="glass glass-hover overflow-hidden relative">
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-primary to-blue-500"></div>
              <CardHeader className="bg-primary/5">
                <CardTitle className="text-lg text-primary flex items-center gap-2">
                🚀 How to Improve Your Resume
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <ol className="list-decimal list-inside space-y-3 text-sm">
                {comprehensiveAnalysis.actionable_improvements.map((imp, i) => (
                  <li key={i} className="pl-2 leading-relaxed">{imp}</li>
                ))}
              </ol>
            </CardContent>
          </Card>
          </motion.div>

          {/* Suggested Changes */}
          {comprehensiveAnalysis.suggested_changes && comprehensiveAnalysis.suggested_changes.length > 0 && (
            <motion.div variants={itemVars}>
              <Card className="glass glass-hover">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-primary" /> Suggested Improvements
                  </CardTitle>
                </CardHeader>
              <CardContent className="space-y-4">
                {comprehensiveAnalysis.suggested_changes.map((change, i) => (
                  <div key={i} className="grid sm:grid-cols-2 gap-4 text-sm border rounded-lg overflow-hidden">
                    <div className="p-4 bg-muted/30 border-r border-b sm:border-b-0">
                      <span className="text-xs font-bold uppercase text-red-500 block mb-2">Current</span>
                      <p className="italic text-muted-foreground">"{change.current}"</p>
                    </div>
                    <div className="p-4 bg-green-500/5">
                      <span className="text-xs font-bold uppercase text-green-600 block mb-2">Suggested</span>
                      <p className="font-medium text-green-900 dark:text-green-100">"{change.suggested}"</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
            </motion.div>
          )}

        </motion.div>
      )}
    </motion.div>
  );
}
