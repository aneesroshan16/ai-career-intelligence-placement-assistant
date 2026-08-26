export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "student" | "admin" | "placement_officer";
  avatar_url?: string | null;
  profile?: StudentProfile | null;
}

export interface StudentProfile {
  id: string;
  roll_number?: string | null;
  department_id?: number | null;
  graduation_year?: number | null;
  cgpa?: number | null;
  internships: number;
  active_backlogs: number;
  phone?: string | null;
  location?: string | null;
  target_role?: string | null;
}

export interface Role {
  id: number;
  name: string;
  match_percentage?: number;
  reasoning?: string;
  matched_skills?: string[];
  developing_skills?: string[];
  missing_skills?: string[];
  next_steps?: string[];
}

export interface ResumeSummary {
  id: string;
  file_type: string;
  original_filename: string;
  parse_status: "pending" | "processing" | "completed" | "failed";
  is_active: boolean;
}

export interface Resume extends ResumeSummary {
  skills: { id: number; raw_text: string; proficiency: string | null }[];
  education: {
    id: number;
    institution: string | null;
    degree: string | null;
    field_of_study: string | null;
    start_year: number | null;
    end_year: number | null;
  }[];
  projects: { id: number; title: string; description: string | null; tech_stack: string[] | null }[];
  certifications: { id: number; title: string; issuer: string | null }[];
}

export interface ATSCategoryScores {
  structure: number;
  keywords: number;
  skills: number;
  experience: number;
  projects: number;
  education: number;
  ats_compatibility: number;
  contact_info: number;
}

export interface RecommendedRole {
  role_name: string;
  match_percentage: number;
  why_matches: string[];
  missing_skills: string[];
}

export interface ResumeImprovement {
  current: string;
  suggested: string;
}

export interface ComprehensiveATSAnalysis {
  overall_score: number;
  category_scores: ATSCategoryScores;
  strengths: string[];
  areas_to_improve: string[];
  missing_keywords: string[];
  resume_summary: string;
  recommended_roles: RecommendedRole[];
  actionable_improvements: string[];
  suggested_changes: ResumeImprovement[];
}

export interface ATSReport {
  id: string;
  resume_id: string;
  overall_score: number;
  keyword_score: number | null;
  formatting_score: number | null;
  section_score: number | null;
  missing_sections: string[] | null;
  suggestions: ComprehensiveATSAnalysis[] | { issue: string; recommendation: string; severity: string }[] | null;
  recommended_roles?: RecommendedRole[] | null;
  target_role_id: number | null;
}

export interface SkillGapReport {
  id: string;
  resume_id: string;
  role_id: number;
  matched_skills: { skill: string; importance: number }[];
  missing_skills: { skill: string; importance: number }[];
  match_percentage: number;
}

export interface Roadmap {
  id: string;
  skill_gap_report_id: string;
  total_weeks: number;
  plan: {
    week: number;
    focus_skills: string[];
    tasks: string[];
    est_hours: number;
    tasks_completed?: boolean[];
  }[];
  milestones: { month: number; goal: string; deliverable: string }[];
  generated_by: string;
}

export interface ReadinessScore {
  id: string;
  technical_score: number | null;
  aptitude_score: number | null;
  communication_score: number | null;
  interview_score: number | null;
  overall_score: number;
}

export interface PlacementFeatures {
  cgpa: number;
  internships: number;
  projects_count: number;
  certifications_count: number;
  skills_count: number;
  coding_score: number;
  aptitude_score: number;
  ats_score: number;
  interview_score: number;
}

export interface PlacementPrediction {
  probability: number;
  predicted_label: boolean;
  model_version: string;
}

export interface Job {
  id: string;
  title: string;
  company_name?: string | null;
  role_id: number | null;
  description: string | null;
  required_skills: string[] | null;
  experience_min: number;
  experience_max: number | null;
  location: string | null;
  job_type: "internship" | "full_time" | "contract";
  is_active: boolean;
}

export interface JobMatch {
  job_id: string;
  title: string;
  company_name: string | null;
  location: string | null;
  job_type: string;
  similarity_score: number;
}

export interface InterviewSession {
  id: string;
  mode: "hr" | "technical";
  role_id: number | null;
  status: "in_progress" | "completed" | "abandoned";
  overall_feedback: Record<string, unknown> | null;
  score: number | null;
}

export interface InterviewSessionDetail extends InterviewSession {
  turns: {
    id: string;
    turn_number: number;
    question: string;
    answer: string | null;
    feedback: Record<string, unknown> | null;
  }[];
}

export interface CodingProblem {
  id: string;
  title: string;
  difficulty: string;
  statement: string;
  starter_code: Record<string, string> | null;
  visible_test_cases: { input: string; expected_output: string }[];
}

export interface CodingAttempt {
  id: string;
  problem_id: string;
  language: string;
  passed_cases: number;
  total_cases: number;
  score: number | null;
  execution_log?: { case?: number; passed?: boolean; hidden?: boolean; stdout?: string; stderr?: string; error?: string }[] | null;
}

export interface AptitudeQuestion {
  id: string;
  category: "quantitative" | "logical" | "verbal";
  question: string;
  options: string[];
  difficulty: string | null;
}

export interface AptitudeResult {
  overall_score: number;
  category_scores: Record<string, number>;
  total_questions: number;
  correct_answers: number;
}

export interface AptitudeAttempt {
  id: string;
  overall_score: number;
  category_scores: Record<string, number>;
  total_questions: number;
  correct_answers: number;
}

export interface DashboardData {
  active_resume_id: string | null;
  ats_score_trend: { date: string; score: number }[];
  readiness_trend: { date: string; overall_score: number }[];
  skill_progress: { total_skills: number; matched_skill_names: string[] };
  interview_history: { id: string; mode: string; status: string; score: number | null; started_at: string }[];
}
