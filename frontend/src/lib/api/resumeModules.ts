import { apiClient, unwrap } from "@/lib/api/client";
import type {
  ATSReport,
  Resume,
  ResumeSummary,
  Roadmap,
  Role,
  SkillGapReport,
  User,
} from "@/types";

// --- Users ---
export const getMe = () => unwrap<User>(apiClient.get("/users/me"));
export const updateMe = (payload: Partial<User> & Record<string, unknown>) =>
  unwrap<User>(apiClient.put("/users/me", payload));

// --- Resumes ---
export const uploadResume = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return unwrap<Resume>(
    apiClient.post("/resumes", form, { headers: { "Content-Type": "multipart/form-data" } })
  );
};
export const listResumes = () => unwrap<ResumeSummary[]>(apiClient.get("/resumes"));
export const getResume = (id: string) => unwrap<Resume>(apiClient.get(`/resumes/${id}`));
export const getResumeStatus = (id: string) =>
  unwrap<{ id: string; parse_status: string }>(apiClient.get(`/resumes/${id}/status`));

// --- ATS ---
export const analyzeATS = (resumeId: string, targetRoleId: number) =>
  unwrap<ATSReport>(apiClient.post("/ats/analyze", { resume_id: resumeId, target_role_id: targetRoleId }));
export const getLatestATSReport = (resumeId: string) =>
  unwrap<ATSReport>(apiClient.get(`/ats/reports/${resumeId}`));
export const getATSHistory = (resumeId: string) =>
  unwrap<ATSReport[]>(apiClient.get(`/ats/reports/${resumeId}/history`));

// --- Skills / Skill Gap ---
export const listRoles = () => unwrap<Role[]>(apiClient.get("/skills/roles"));
export const analyzeSkillGap = (resumeId: string, roleId: number) =>
  unwrap<SkillGapReport>(apiClient.post("/skills/gap-analysis", { resume_id: resumeId, role_id: roleId }));

// --- Roadmap ---
export const generateRoadmap = (skillGapReportId: string, weeks = 8) =>
  unwrap<Roadmap>(apiClient.post("/roadmap/generate", { skill_gap_report_id: skillGapReportId, weeks }));
export const getRoadmap = (id: string) => unwrap<Roadmap>(apiClient.get(`/roadmap/${id}`));
export const updateRoadmapProgress = (id: string, week: number, taskIndex: number, completed: boolean) =>
  unwrap<Roadmap>(apiClient.patch(`/roadmap/${id}/progress`, { week, task_index: taskIndex, completed }));
