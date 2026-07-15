"""
Module 15: cross-cohort analytics. Aggregates skill demand from active job
postings and placement-probability trends over time from stored predictions.
"""
from collections import Counter
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.jobs.models import Job
from app.modules.placement.models import PlacementPrediction


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def skill_demand(self, top_n: int = 20) -> list[dict]:
        stmt = select(Job.required_skills).where(Job.is_active.is_(True))
        result = await self.session.execute(stmt)
        counter: Counter = Counter()
        for (skills,) in result.all():
            if not skills:
                continue
            for skill in skills:
                counter[skill] += 1

        return [{"skill": skill, "demand_count": count} for skill, count in counter.most_common(top_n)]

    async def placement_trends(self) -> list[dict]:
        stmt = select(PlacementPrediction.probability, PlacementPrediction.created_at)
        result = await self.session.execute(stmt)
        rows = result.all()

        monthly: dict[str, list[float]] = {}
        for probability, created_at in rows:
            key = created_at.strftime("%Y-%m") if isinstance(created_at, datetime) else str(created_at)[:7]
            monthly.setdefault(key, []).append(float(probability))

        trends = [
            {"month": month, "avg_predicted_probability": round(sum(vals) / len(vals) * 100, 2), "sample_size": len(vals)}
            for month, vals in sorted(monthly.items())
        ]
        return trends
