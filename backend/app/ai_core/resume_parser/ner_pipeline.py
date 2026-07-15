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
    def parse(self, text: str, known_skills: list[str] | None = None) -> ParsedResume:
        known_skills = known_skills or _DEFAULT_SKILL_GAZETTEER
        sections = _split_sections(text)

        return ParsedResume(
            raw_text=text,
            emails=list(dict.fromkeys(_EMAIL_RE.findall(text))),
            phones=list(dict.fromkeys(_PHONE_RE.findall(text)))[:3],
            skills=_extract_skills(sections.get("skills", "") or text, known_skills),
            education=_extract_education(sections.get("education", "")),
            projects=_extract_projects(sections.get("projects", "")),
            certifications=_extract_certifications(sections.get("certifications", "")),
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
