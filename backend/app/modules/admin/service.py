"""
Admin/placement-officer facing aggregation (Module 14): per-department
placement analytics and CSV export. Access to these endpoints is gated by
`require_role(["admin", "placement_officer"])` at the router level.
"""
import csv
import io

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.placement.models import PlacementPrediction
from app.modules.readiness.models import ReadinessScore
from app.modules.users.models import Department, StudentProfile, User


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def department_analytics(self) -> list[dict]:
        stmt = (
            select(
                Department.id,
                Department.name,
                func.count(StudentProfile.id).label("student_count"),
                func.avg(StudentProfile.cgpa).label("avg_cgpa"),
                func.avg(StudentProfile.internships).label("avg_internships"),
            )
            .join(StudentProfile, StudentProfile.department_id == Department.id, isouter=True)
            .group_by(Department.id, Department.name)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        analytics = []
        for row in rows:
            avg_readiness = await self._avg_readiness_for_department(row.id)
            avg_placement_prob = await self._avg_placement_probability_for_department(row.id)
            analytics.append({
                "department_id": row.id,
                "department_name": row.name,
                "student_count": row.student_count or 0,
                "avg_cgpa": round(float(row.avg_cgpa), 2) if row.avg_cgpa else None,
                "avg_internships": round(float(row.avg_internships), 2) if row.avg_internships else None,
                "avg_readiness_score": avg_readiness,
                "avg_placement_probability": avg_placement_prob,
            })
        return analytics

    async def _avg_readiness_for_department(self, department_id: int) -> float | None:
        stmt = (
            select(func.avg(ReadinessScore.overall_score))
            .join(User, User.id == ReadinessScore.user_id)
            .join(StudentProfile, StudentProfile.user_id == User.id)
            .where(StudentProfile.department_id == department_id)
        )
        value = (await self.session.execute(stmt)).scalar()
        return round(float(value), 2) if value else None

    async def _avg_placement_probability_for_department(self, department_id: int) -> float | None:
        stmt = (
            select(func.avg(PlacementPrediction.probability))
            .join(User, User.id == PlacementPrediction.user_id)
            .join(StudentProfile, StudentProfile.user_id == User.id)
            .where(StudentProfile.department_id == department_id)
        )
        value = (await self.session.execute(stmt)).scalar()
        return round(float(value) * 100, 2) if value else None

    async def export_department_analytics_csv(self) -> str:
        rows = await self.department_analytics()
        buffer = io.StringIO()
        if rows:
            writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return buffer.getvalue()
