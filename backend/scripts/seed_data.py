"""
Seeds baseline reference data required for the platform to function:
departments, roles, skill taxonomy (skills_master + role_skills), an
aptitude question bank, and a handful of sample job postings.

Run:
    PYTHONPATH=. python scripts/seed_data.py
"""
import asyncio
import uuid

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.modules.aptitude.models import AptitudeQuestion
from app.modules.jobs.models import Company, Job
from app.modules.skills.models import Role, RoleSkill, SkillMaster
from app.modules.users.models import Department

ROLES = ["Data Scientist", "Data Analyst", "ML Engineer", "Software Engineer", "AI Engineer"]

DEPARTMENTS = ["CSE", "AI & DS", "ECE", "IT", "MECH"]

SKILLS = [
    ("Python", "language"), ("Java", "language"), ("C++", "language"), ("SQL", "language"),
    ("R", "language"), ("JavaScript", "language"), ("TypeScript", "language"),
    ("Machine Learning", "domain"), ("Deep Learning", "domain"), ("NLP", "domain"),
    ("Computer Vision", "domain"), ("Statistics", "domain"), ("A/B Testing", "domain"),
    ("TensorFlow", "framework"), ("PyTorch", "framework"), ("Scikit-learn", "framework"),
    ("XGBoost", "framework"), ("Pandas", "framework"), ("NumPy", "framework"),
    ("React", "framework"), ("Node.js", "framework"), ("FastAPI", "framework"), ("Django", "framework"),
    ("Docker", "tool"), ("Kubernetes", "tool"), ("Git", "tool"), ("AWS", "tool"), ("GCP", "tool"),
    ("PostgreSQL", "tool"), ("MongoDB", "tool"), ("Tableau", "tool"), ("Power BI", "tool"),
    ("REST API", "tool"), ("System Design", "domain"), ("Data Structures", "domain"), ("Algorithms", "domain"),
    ("Communication", "soft-skill"), ("Problem Solving", "soft-skill"),
]

# role_name -> [(skill_name, importance 1-5), ...]
ROLE_SKILLS = {
    "Data Scientist": [
        ("Python", 5), ("SQL", 5), ("Machine Learning", 5), ("Statistics", 5),
        ("Pandas", 4), ("Scikit-learn", 4), ("Deep Learning", 3), ("A/B Testing", 3),
        ("Tableau", 2), ("Communication", 3),
    ],
    "Data Analyst": [
        ("SQL", 5), ("Python", 4), ("Statistics", 4), ("Tableau", 4), ("Power BI", 3),
        ("Pandas", 4), ("Communication", 4), ("Problem Solving", 3),
    ],
    "ML Engineer": [
        ("Python", 5), ("Machine Learning", 5), ("Deep Learning", 4), ("TensorFlow", 4),
        ("PyTorch", 4), ("Docker", 4), ("System Design", 3), ("AWS", 3), ("SQL", 3),
    ],
    "Software Engineer": [
        ("Java", 4), ("Python", 4), ("Data Structures", 5), ("Algorithms", 5),
        ("System Design", 4), ("Git", 4), ("REST API", 4), ("SQL", 3), ("Docker", 3),
    ],
    "AI Engineer": [
        ("Python", 5), ("Deep Learning", 5), ("NLP", 4), ("Computer Vision", 3),
        ("PyTorch", 4), ("TensorFlow", 3), ("System Design", 3), ("Docker", 3), ("AWS", 3),
    ],
}

APTITUDE_QUESTIONS = [
    # (category, question, options, correct_index, difficulty)
    ("quantitative", "If a train travels 300 km in 5 hours, what is its speed?", ["50 km/h", "60 km/h", "70 km/h", "65 km/h"], 1, "easy"),
    ("quantitative", "What is 15% of 240?", ["30", "36", "40", "24"], 1, "easy"),
    ("quantitative", "A shop sells an item at a 20% profit. If cost price is 500, what is the selling price?", ["550", "600", "620", "580"], 1, "medium"),
    ("quantitative", "The average of 5 numbers is 20. If one number is removed, the average becomes 18. What was removed?", ["24", "28", "26", "30"], 1, "medium"),
    ("quantitative", "Simple interest on 1000 at 10% per annum for 2 years is:", ["100", "200", "150", "210"], 1, "easy"),
    ("logical", "Find the next number: 2, 6, 12, 20, 30, ?", ["36", "40", "42", "38"], 1, "medium"),
    ("logical", "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies?", ["Yes", "No", "Cannot be determined", "Only sometimes"], 0, "easy"),
    ("logical", "Which one does not belong: Apple, Banana, Carrot, Mango?", ["Apple", "Banana", "Carrot", "Mango"], 2, "easy"),
    ("logical", "A is taller than B. C is shorter than B. Who is the shortest?", ["A", "B", "C", "Cannot be determined"], 2, "medium"),
    ("logical", "Complete the pattern: AZ, BY, CX, ?", ["DW", "DV", "EW", "DX"], 0, "hard"),
    ("verbal", "Choose the correct synonym for 'Ambiguous':", ["Clear", "Vague", "Precise", "Direct"], 1, "easy"),
    ("verbal", "Choose the correct antonym for 'Benevolent':", ["Kind", "Generous", "Malevolent", "Charitable"], 2, "easy"),
    ("verbal", "Fill in the blank: She is _____ to her friends.", ["loyalty", "loyal", "loyally", "loyalness"], 1, "easy"),
    ("verbal", "Identify the grammatically correct sentence:", [
        "Neither of the boys were present.", "Neither of the boys was present.",
        "Neither of the boys is being present.", "Neither of the boy was present.",
    ], 1, "medium"),
    ("verbal", "Choose the correctly spelled word:", ["Recieve", "Receive", "Receeve", "Receve"], 1, "easy"),
]

SAMPLE_JOBS = [
    ("TechNova", "Data Scientist", "Data Scientist – New Grad", ["Python", "SQL", "Machine Learning", "Statistics"], 0, 1, "Bengaluru", "full_time"),
    ("Insight Analytics", "Data Analyst", "Junior Data Analyst", ["SQL", "Tableau", "Python"], 0, 2, "Hyderabad", "full_time"),
    ("NeuralWorks AI", "ML Engineer", "ML Engineer Intern", ["Python", "TensorFlow", "Docker"], 0, 0, "Remote", "internship"),
    ("CodeForge", "Software Engineer", "Software Engineer I", ["Java", "Data Structures", "Algorithms", "REST API"], 0, 2, "Pune", "full_time"),
    ("VisionAI Labs", "AI Engineer", "AI Engineer – Computer Vision", ["Python", "PyTorch", "Computer Vision"], 1, 3, "Chennai", "full_time"),
]


async def seed():
    async with AsyncSessionLocal() as session:
        # Departments
        dept_map = {}
        for name in DEPARTMENTS:
            existing = (await session.execute(select(Department).where(Department.name == name))).scalar_one_or_none()
            if not existing:
                existing = Department(name=name)
                session.add(existing)
                await session.flush()
            dept_map[name] = existing
        await session.commit()

        # Roles
        role_map = {}
        for name in ROLES:
            existing = (await session.execute(select(Role).where(Role.name == name))).scalar_one_or_none()
            if not existing:
                existing = Role(name=name)
                session.add(existing)
                await session.flush()
            role_map[name] = existing
        await session.commit()

        # Skills master
        skill_map = {}
        for name, category in SKILLS:
            existing = (await session.execute(select(SkillMaster).where(SkillMaster.name == name))).scalar_one_or_none()
            if not existing:
                existing = SkillMaster(name=name, category=category)
                session.add(existing)
                await session.flush()
            skill_map[name] = existing
        await session.commit()

        # Role <-> Skill taxonomy
        for role_name, skills in ROLE_SKILLS.items():
            role = role_map[role_name]
            for skill_name, importance in skills:
                skill = skill_map[skill_name]
                existing = (
                    await session.execute(
                        select(RoleSkill).where(RoleSkill.role_id == role.id, RoleSkill.skill_id == skill.id)
                    )
                ).scalar_one_or_none()
                if not existing:
                    session.add(RoleSkill(role_id=role.id, skill_id=skill.id, importance=importance))
        await session.commit()

        # Aptitude questions
        existing_count = (await session.execute(select(AptitudeQuestion))).scalars().all()
        if not existing_count:
            for category, question, options, correct, difficulty in APTITUDE_QUESTIONS:
                session.add(AptitudeQuestion(
                    id=uuid.uuid4(), category=category, question=question,
                    options=options, correct_option=correct, difficulty=difficulty,
                ))
            await session.commit()

        # Sample jobs (with embeddings indexed via JobsService for consistency)
        from app.modules.jobs.repository import JobsRepository
        from app.modules.jobs.schemas import JobCreateIn
        from app.modules.jobs.service import JobsService

        existing_jobs = (await session.execute(select(Job))).scalars().all()
        if not existing_jobs:
            jobs_service = JobsService(session)
            for company, role_name, title, skills, exp_min, exp_max, location, job_type in SAMPLE_JOBS:
                payload = JobCreateIn(
                    title=title, company_name=company, role_id=role_map[role_name].id,
                    description=f"{title} at {company}, focused on {role_name} responsibilities.",
                    required_skills=skills, experience_min=exp_min, experience_max=exp_max,
                    location=location, job_type=job_type,
                )
                await jobs_service.create(payload)

        print("Seed complete: departments, roles, skills, role_skills, aptitude questions, sample jobs.")


if __name__ == "__main__":
    asyncio.run(seed())
