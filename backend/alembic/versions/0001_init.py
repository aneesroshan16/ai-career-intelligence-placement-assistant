"""initial schema

Revision ID: 0001_init
Revises:
Create Date: 2026-07-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')  # for gen_random_uuid()

    op.create_table(
        "departments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("full_name", sa.String, nullable=False, server_default=""),
        sa.Column("role", sa.String, nullable=False, server_default="student"),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "student_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True),
        sa.Column("roll_number", sa.String, unique=True, nullable=True),
        sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("graduation_year", sa.Integer, nullable=True),
        sa.Column("cgpa", sa.Numeric(4, 2), nullable=True),
        sa.Column("internships", sa.Integer, server_default="0"),
        sa.Column("active_backlogs", sa.Integer, server_default="0"),
        sa.Column("phone", sa.String, nullable=True),
        sa.Column("location", sa.String, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
    )

    op.create_table(
        "skills_master",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("category", sa.String, nullable=True),
    )

    op.create_table(
        "role_skills",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer, sa.ForeignKey("skills_master.id", ondelete="CASCADE"), nullable=False),
        sa.Column("importance", sa.SmallInteger, server_default="3"),
        sa.UniqueConstraint("role_id", "skill_id"),
    )

    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_url", sa.Text, nullable=False),
        sa.Column("file_type", sa.String, nullable=False),
        sa.Column("original_filename", sa.String, nullable=False),
        sa.Column("parse_status", sa.String, server_default="pending"),
        sa.Column("raw_text", sa.Text, nullable=True),
        sa.Column("embedding_id", sa.String, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_resumes_user", "resumes", ["user_id"])

    op.create_table(
        "resume_skills",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer, sa.ForeignKey("skills_master.id"), nullable=True),
        sa.Column("raw_text", sa.String, nullable=False),
        sa.Column("proficiency", sa.String, nullable=True),
    )
    op.create_index("idx_resume_skills_resume", "resume_skills", ["resume_id"])

    op.create_table(
        "resume_education",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("institution", sa.String, nullable=True),
        sa.Column("degree", sa.String, nullable=True),
        sa.Column("field_of_study", sa.String, nullable=True),
        sa.Column("start_year", sa.Integer, nullable=True),
        sa.Column("end_year", sa.Integer, nullable=True),
        sa.Column("gpa", sa.Numeric(4, 2), nullable=True),
    )

    op.create_table(
        "resume_projects",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tech_stack", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("project_url", sa.String, nullable=True),
    )

    op.create_table(
        "resume_certifications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("issuer", sa.String, nullable=True),
        sa.Column("issue_date", sa.Date, nullable=True),
        sa.Column("credential_url", sa.String, nullable=True),
    )

    op.create_table(
        "ats_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("keyword_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("formatting_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("section_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("missing_sections", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("suggestions", postgresql.JSONB, nullable=True),
        sa.Column("target_role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_ats_reports_resume", "ats_reports", ["resume_id"])

    op.create_table(
        "skill_gap_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("matched_skills", postgresql.JSONB, nullable=False),
        sa.Column("missing_skills", postgresql.JSONB, nullable=False),
        sa.Column("match_percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_skill_gap_resume_role", "skill_gap_reports", ["resume_id", "role_id"])

    op.create_table(
        "roadmaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("skill_gap_report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skill_gap_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("total_weeks", sa.Integer, nullable=False),
        sa.Column("plan", postgresql.JSONB, nullable=False),
        sa.Column("milestones", postgresql.JSONB, nullable=False),
        sa.Column("generated_by", sa.String, server_default="mock"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "readiness_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("technical_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("aptitude_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("communication_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("interview_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("computed_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "placement_predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_version", sa.String, nullable=False),
        sa.Column("input_features", postgresql.JSONB, nullable=False),
        sa.Column("probability", sa.Numeric(5, 4), nullable=False),
        sa.Column("predicted_label", sa.Boolean, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_placement_pred_user", "placement_predictions", ["user_id"])

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("logo_url", sa.String, nullable=True),
    )

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("required_skills", postgresql.JSONB, nullable=True),
        sa.Column("experience_min", sa.Numeric(3, 1), server_default="0"),
        sa.Column("experience_max", sa.Numeric(3, 1), nullable=True),
        sa.Column("location", sa.String, nullable=True),
        sa.Column("job_type", sa.String, nullable=False),
        sa.Column("embedding_id", sa.String, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("posted_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_jobs_role", "jobs", ["role_id"])

    op.create_table(
        "job_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("similarity_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("resume_id", "job_id"),
    )
    op.create_index("idx_job_matches_resume", "job_matches", ["resume_id"])

    op.create_table(
        "interview_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode", sa.String, nullable=False),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=True),
        sa.Column("status", sa.String, server_default="in_progress"),
        sa.Column("overall_feedback", postgresql.JSONB, nullable=True),
        sa.Column("score", sa.Numeric(5, 2), nullable=True),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("idx_interview_sessions_user", "interview_sessions", ["user_id"])

    op.create_table(
        "interview_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("turn_number", sa.Integer, nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=True),
        sa.Column("feedback", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "coding_problems",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("difficulty", sa.String, nullable=False),
        sa.Column("statement", sa.Text, nullable=False),
        sa.Column("starter_code", postgresql.JSONB, nullable=True),
        sa.Column("test_cases", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "coding_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("coding_problems.id"), nullable=False),
        sa.Column("submitted_code", sa.Text, nullable=False),
        sa.Column("language", sa.String, nullable=False),
        sa.Column("passed_cases", sa.Integer, server_default="0"),
        sa.Column("total_cases", sa.Integer, server_default="0"),
        sa.Column("score", sa.Numeric(5, 2), nullable=True),
        sa.Column("execution_log", postgresql.JSONB, nullable=True),
        sa.Column("submitted_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_coding_attempts_user", "coding_attempts", ["user_id"])

    op.create_table(
        "aptitude_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("category", sa.String, nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("options", postgresql.JSONB, nullable=False),
        sa.Column("correct_option", sa.SmallInteger, nullable=False),
        sa.Column("difficulty", sa.String, nullable=True),
    )

    op.create_table(
        "aptitude_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_scores", postgresql.JSONB, nullable=False),
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("total_questions", sa.Integer, nullable=False),
        sa.Column("correct_answers", sa.Integer, nullable=False),
        sa.Column("submitted_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    op.create_index("idx_student_profiles_dept", "student_profiles", ["department_id"])


def downgrade() -> None:
    for table in [
        "aptitude_attempts", "aptitude_questions", "coding_attempts", "coding_problems",
        "interview_turns", "interview_sessions", "job_matches", "jobs", "companies",
        "placement_predictions", "readiness_scores", "roadmaps", "skill_gap_reports",
        "ats_reports", "resume_certifications", "resume_projects", "resume_education",
        "resume_skills", "resumes", "role_skills", "skills_master", "roles",
        "student_profiles", "users", "departments",
    ]:
        op.drop_table(table)
