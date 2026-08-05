import asyncio
import sys
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.modules.resumes.models import Resume
from app.modules.skills.models import Role
from app.modules.ats.service import ATSService
from app.modules.skills.service import SkillsService
from app.modules.roadmap.service import RoadmapService

async def main():
    async with AsyncSessionLocal() as session:
        # Get first resume
        result = await session.execute(select(Resume).limit(1))
        resume = result.scalar_one_or_none()
        if not resume:
            print("No resumes found in the database. Please upload one first.")
            return

        # Get first role
        result = await session.execute(select(Role).limit(1))
        role = result.scalar_one_or_none()
        if not role:
            print("No roles found.")
            return

        print(f"Testing analysis for Resume ID: {resume.id} (File: {resume.original_filename}) against Role: {role.name}\n")

        print("--- 1. Recommended Roles ---")
        skills_service = SkillsService(session)
        recommended = await skills_service.recommend_roles(str(resume.id))
        print("Top 5 recommended roles for this resume:")
        for r in recommended[:5]:
            print(f"  - {r.name}: {r.match_percentage}%")
            
        print("\n--- 2. Skill Gap Analysis ---")
        gap_report = await skills_service.analyze_gap(str(resume.id), role.id)
        print(f"Match for {role.name}: {gap_report.match_percentage}%")
        print(f"Matched Skills: {[s['skill'] for s in gap_report.matched_skills]}")
        print(f"Missing Skills: {[s['skill'] for s in gap_report.missing_skills]}\n")

        print("--- 3. ATS Analysis (using full resume text) ---")
        ats_service = ATSService(session)
        ats_report = await ats_service.analyze(str(resume.id), role.id)
        print(f"Overall Score: {ats_report.overall_score}")
        print(f"Suggestions generated specifically for this resume:\n")
        for i, sugg in enumerate(ats_report.suggestions):
            print(f"  {i+1}. [{sugg.get('severity')}] {sugg.get('issue')}\n     -> {sugg.get('recommendation')}")
        
        print("\n--- 4. Roadmap Generation (using contextualized prompt & smarter mock) ---")
        roadmap_service = RoadmapService(session)
        roadmap = await roadmap_service.generate(str(gap_report.id), weeks=4)
        print(f"Roadmap generated successfully for {roadmap.total_weeks} weeks!")
        for week in roadmap.plan[:2]:
            print(f"  Week {week.get('week')}: Focus -> {', '.join(week.get('focus_skills', []))}")

if __name__ == "__main__":
    asyncio.run(main())
