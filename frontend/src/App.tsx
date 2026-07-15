import { Navigate, Route, Routes } from "react-router-dom";
import { Shell } from "@/components/layout/Shell";
import { AdminRoute, ProtectedRoute } from "@/components/shared/ProtectedRoute";
import { useAuthListener } from "@/hooks/useAuthListener";
import AdminDashboardPage from "@/pages/admin/AdminDashboard";
import AnalyticsPage from "@/pages/analytics/AnalyticsPage";
import LoginPage from "@/pages/auth/Login";
import SignupPage from "@/pages/auth/Signup";
import AssessmentsPage from "@/pages/student/Assessments";
import DashboardPage from "@/pages/student/Dashboard";
import InterviewPage from "@/pages/student/Interview";
import JobsPage from "@/pages/student/Jobs";
import PlacementPage from "@/pages/student/Placement";
import ResumeUploadPage from "@/pages/student/ResumeUpload";
import RoadmapPage from "@/pages/student/Roadmap";
import SkillGapPage from "@/pages/student/SkillGap";

export default function App() {
  useAuthListener();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Shell />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/resume" element={<ResumeUploadPage />} />
          <Route path="/skills" element={<SkillGapPage />} />
          <Route path="/roadmap" element={<RoadmapPage />} />
          <Route path="/placement" element={<PlacementPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/interview" element={<InterviewPage />} />
          <Route path="/assessments" element={<AssessmentsPage />} />

          <Route element={<AdminRoute />}>
            <Route path="/admin" element={<AdminDashboardPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
