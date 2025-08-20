import re
from dataclasses import dataclass

@dataclass
class Job:
    company: str
    company_desc: str | None
    employees_num: str | None
    company_url: str | None
    desc: str
    is_remote: bool
    level_desc: str | None
    url: str
    location: str
    title: str
    rating: int

    def __init__(self, company: str, company_desc: str | None, employees_num: str | None,
                 company_url: str | None, desc: str, is_remote: bool,
                 level_desc: str | None, url: str, location: str, title: str,
                 linkedin_url: str, linkedin_company: str):
        self.company = company
        self.company_desc = company_desc
        self.employees_num = employees_num
        self.company_url = company_url or linkedin_company
        self.desc = desc
        self.is_remote = is_remote
        self.level_desc = level_desc
        self.url = url or linkedin_url
        self.location = location
        self.title = title
        self.rating = self.calculate_job_rating()

    # -------------------------
    # Config
    # -------------------------
    KEYWORDS_CONFIG = {
        "python": 50,   # must-have
        "flask": 40,
        "redis": 35,
        "aws": 45,
        "microservices": 45,
        "backend": 40,
        "ci/cd": 35,
        "circleci": 25,
        "mysql": 25,
        "sql": 30,
        "cloud": 30,
        "heroku": 15,
        "serverless": 15,
        "lambda": 15,
        "react": 25,
        "typescript": 20,
        "javascript": 15,
        "ember": 10,
        "fullstack": 15,
        "api": 10,
        "postgresql": 15,
        "rest": 10,
        # negatives
        "node": -10,
        "go": -50,
        "java": -50,
        "c#": -50,
        "vue": -50,
        "kubernetes": -200,
        # strong avoid
        "angular": -1000,
        "php": -1000,
        "wordpress": -1000,
        "drupal": -1000,
    }

    MUST_HAVE = {"python"}

    SECTION_HEADERS = {
        "requirements": ["requirements", "qualifications", "must have", "what we’re looking for"],
        "responsibilities": ["responsibilities", "what you’ll do", "your role"],
        "about": ["about", "our company", "who we are", "tech stack"],
    }

    SECTION_WEIGHTS = {
        "requirements": 1.0,       # full weight
        "responsibilities": 0.7,   # medium importance
        "about": 0.3,              # low importance
    }

    # -------------------------
    # Helpers
    # -------------------------
    def split_sections(self, desc: str) -> dict:
        """Split job description into sections by detecting headers."""
        sections = {"requirements": "", "responsibilities": "", "about": desc.lower()}
        desc_lower = desc.lower()

        for section, keywords in self.SECTION_HEADERS.items():
            for kw in keywords:
                match = re.split(rf"\b{kw}\b", desc_lower)
                if len(match) > 1:
                    sections[section] = match[-1]
                    break
        return sections

    # -------------------------
    # Main Scoring
    # -------------------------
    def calculate_job_rating(self) -> int:
        sections = self.split_sections(self.desc)

        # Must-have filter (only in requirements section!)
        req_words = set(re.findall(r"\b[a-zA-Z0-9#+/]+\b", sections["requirements"]))
        if not self.MUST_HAVE.issubset(req_words):
            return -999  # reject: missing must-have

        rating = 0
        used_keywords = set()

        for section, text in sections.items():
            words = re.findall(r"\b[a-zA-Z0-9#+/]+\b", text)
            multiplier = self.SECTION_WEIGHTS.get(section, 1.0)

            for word in words:
                if word in used_keywords:
                    continue

                found_rating = self.KEYWORDS_CONFIG.get(word)
                if found_rating is None:
                    continue

                # strong avoid → immediate reject
                if found_rating <= -1000:
                    return -1000

                rating += int(found_rating * multiplier)
                used_keywords.add(word)

        return rating
