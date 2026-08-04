import { apiClient, unwrap } from "@/lib/api/client";
import type {
  AptitudeAttempt,
  AptitudeQuestion,
  AptitudeResult,
  CodingAttempt,
  CodingProblem,
  DashboardData,
  InterviewSession,
  Job,
  JobMatch,
  PlacementFeatures,
  PlacementPrediction,
  ReadinessScore,
} from "@/types";

// --- Readiness ---
export const getMyReadiness = () => unwrap<ReadinessScore>(apiClient.get("/readiness/me"));
export const recomputeReadiness = () => unwrap<ReadinessScore>(apiClient.post("/readiness/recompute"));
export const getReadinessHistory = () => unwrap<ReadinessScore[]>(apiClient.get("/readiness/me/history"));

// --- Placement Prediction ---
export const predictPlacement = (features: PlacementFeatures) =>
  unwrap<PlacementPrediction>(apiClient.post("/placement/predict", features));
export const getPlacementHistory = () =>
  unwrap<PlacementPrediction[]>(apiClient.get("/placement/predict/history"));

// --- Job Matching & Recommendations ---
export const computeJobMatches = (resumeId: string) =>
  unwrap<JobMatch[]>(apiClient.post("/matching/compute", { resume_id: resumeId }));
export const getJobMatches = (resumeId: string) => unwrap<JobMatch[]>(apiClient.get(`/matching/${resumeId}`));
export const listJobs = (params?: Record<string, string | number>) =>
  unwrap<Job[]>(apiClient.get("/jobs", { params }));
export const getRecommendedJobs = () => unwrap<JobMatch[]>(apiClient.get("/jobs/recommended"));

// --- Interview Simulator ---
export const startInterview = (mode: "hr" | "technical", roleId?: number) =>
  unwrap<{ session: InterviewSession; first_question: string }>(
    apiClient.post("/interview/sessions", { mode, role_id: roleId })
  );
export const submitInterviewAnswer = (sessionId: string, answer: string) =>
  unwrap<{ feedback: Record<string, unknown>; next_question: string | null; session_status: string }>(
    apiClient.post(`/interview/sessions/${sessionId}/answer`, { answer })
  );
export const completeInterview = (sessionId: string) =>
  unwrap<InterviewSession>(apiClient.post(`/interview/sessions/${sessionId}/complete`));
export const listInterviewSessions = () => unwrap<InterviewSession[]>(apiClient.get("/interview/sessions"));

// --- Coding Assessment ---
export const generateCodingProblem = (roleId: number | undefined, difficulty: string) =>
  unwrap<CodingProblem>(apiClient.post("/coding/generate", { role_id: roleId, difficulty }));
export const submitCode = (problemId: string, code: string, language = "python") =>
  unwrap<CodingAttempt>(apiClient.post(`/coding/${problemId}/submit`, { code, language }));
export const listCodingAttempts = () => unwrap<CodingAttempt[]>(apiClient.get("/coding/attempts"));

// --- Aptitude Assessment ---
export const getAptitudeTest = () => unwrap<AptitudeQuestion[]>(apiClient.get("/aptitude/test"));
export const submitAptitudeTest = (answers: { question_id: string; selected_option: number }[]) =>
  unwrap<AptitudeResult>(apiClient.post("/aptitude/submit", { answers }));
export const listAptitudeAttempts = () => unwrap<AptitudeAttempt[]>(apiClient.get("/aptitude/attempts"));

// --- Student Dashboard ---
export const getStudentDashboard = () => unwrap<DashboardData>(apiClient.get("/dashboard/student"));
