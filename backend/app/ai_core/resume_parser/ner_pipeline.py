"""
Structured extraction: raw resume text -> ParsedResume.

Hybrid approach (no LLM dependency, so this works fully offline):
  - Regex for contact info (email, phone) and section detection.
  - A curated skills gazetteer (matched case-insensitively against known
    skill names, typically the `skills_master` table) for skill extraction.
  - Lightweight heuristics for splitting Education/Projects/Certifications
    sections based on common resume header keywords.

Designed so a future LLM-based extractor can be swapped in behind the same
`ResumeParser.parse(text, known_skills) -> ParsedResume` signature — e.g.
`ai_core.llm.complete_json(prompt, ParsedResume)` — without touching callers.
"""
from __future__ import annotations

import re

from app.ai_core.resume_parser.schema import (
    ParsedCertification,
    ParsedEducation,
    ParsedProject,
    ParsedResume,
    ParsedSkill,
)

_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}")
_YEAR_RE = re.compile(r"(19|20)\d{2}")

_SECTION_HEADERS = {
    "education": ["education", "academic background", "academics"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses & certifications"],
    "skills": ["skills", "technical skills", "core competencies"],
}


def _split_sections(text: str) -> dict[str, str]:
    """Splits raw text into section->body using common resume header keywords."""
    lines = text.split("\n")
    sections: dict[str, list[str]] = {}
    current = "header"
    sections[current] = []

    for line in lines:
        stripped = line.strip().lower()
        matched_section = None
        for section_name, keywords in _SECTION_HEADERS.items():
            if any(stripped == kw or stripped.startswith(kw) for kw in keywords) and len(stripped) < 40:
                matched_section = section_name
                break
        if matched_section:
            current = matched_section
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def _extract_skills(text: str, known_skills: list[str]) -> list[ParsedSkill]:
    found: list[ParsedSkill] = []
    seen = set()
    lower_text = text.lower()
    for skill in known_skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, lower_text) and skill.lower() not in seen:
            seen.add(skill.lower())
            found.append(ParsedSkill(raw_text=skill, normalized_name=skill))
    return found


def _extract_education(section_text: str) -> list[ParsedEducation]:
    if not section_text:
        return []
    entries = []
    for block in re.split(r"\n{1,2}", section_text):
        block = block.strip()
        if not block:
            continue
        full_years = [int(m) for m in re.findall(r"(?:19|20)\d{2}", block)]
        entries.append(
            ParsedEducation(
                institution=block.split("\n")[0][:200],
                start_year=full_years[0] if full_years else None,
                end_year=full_years[-1] if len(full_years) > 1 else None,
            )
        )
    return entries[:5]


def _extract_projects(section_text: str) -> list[ParsedProject]:
    if not section_text:
        return []
    projects = []
    for block in re.split(r"\n{2,}", section_text):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        title = lines[0][:200]
        description = " ".join(lines[1:])[:1000] if len(lines) > 1 else None
        projects.append(ParsedProject(title=title, description=description))
    return projects[:10]


def _extract_certifications(section_text: str) -> list[ParsedCertification]:
    if not section_text:
        return []
    certs = []
    for line in section_text.split("\n"):
        line = line.strip("-•* \t")
        if line:
            certs.append(ParsedCertification(title=line[:200]))
    return certs[:10]


class ResumeParser:
    async def parse(self, text: str, known_skills: list[str] | None = None) -> ParsedResume:
        # Avoid the mock LLM completely and implement a deterministic, logic-based pipeline.
        # This guarantees dynamic output that precisely matches the uploaded resume text.
        sections = _split_sections(text)
        
        # 1. Contact info extraction
        email_match = _EMAIL_RE.search(text)
        phone_match = _PHONE_RE.search(text)
        email = email_match.group(0) if email_match else None
        phone = phone_match.group(0) if phone_match else None
        
        # 2. Extract sections using the deterministic functions
        skills_text = sections.get("skills", text) # fallback to full text if no explicit skills section
        extracted_skills = _extract_skills(skills_text, known_skills or _DEFAULT_SKILL_GAZETTEER)
        
        # If we didn't find many skills in the skills section, search the whole resume
        if len(extracted_skills) < 3:
            extracted_skills = _extract_skills(text, known_skills or _DEFAULT_SKILL_GAZETTEER)

        education = _extract_education(sections.get("education", ""))
        projects = _extract_projects(sections.get("projects", ""))
        certifications = _extract_certifications(sections.get("certifications", ""))
        
        # Simple name heuristic (first line)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        name = lines[0] if lines else None
        if name and (len(name) > 40 or "@" in name or any(char.isdigit() for char in name)):
            name = "Applicant"

        return ParsedResume(
            name=name,
            email=email,
            phone=phone,
            skills=extracted_skills,
            education=education,
            projects=projects,
            certifications=certifications,
            experience=[],
            raw_text=text
        )


# Fallback gazetteer used when the DB skills_master table isn't available
# (e.g. isolated unit tests). Production calls pass the live DB list instead.
_DEFAULT_SKILL_GAZETTEER = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "SQL", "R",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Scikit-learn", "XGBoost", "Pandas", "NumPy",
    "React", "Node.js", "FastAPI", "Django", "Flask", "REST API",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Git", "CI/CD",
    "PostgreSQL", "MongoDB", "Redis", "Data Analysis", "Data Visualization",
    "Tableau", "Power BI", "Excel", "Statistics", "A/B Testing",
]
