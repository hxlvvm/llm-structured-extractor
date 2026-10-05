from datetime import date
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator


class Seniority(str, Enum):
    intern = "intern"
    junior = "junior"
    mid = "mid"
    senior = "senior"
    unknown = "unknown"


class JobPosting(BaseModel):
    """The structured record we want the LLM to produce from a free-text job ad."""
    title: str = Field(description="Job title, e.g. 'Python Developer'")
    company: str | None = Field(default=None, description="Hiring company")
    location: str | None = None
    remote: bool = Field(default=False, description="True if the role can be done fully remotely")
    seniority: Seniority = Seniority.unknown
    min_years_experience: float | None = Field(default=None, ge=0, le=40)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    contact_email: EmailStr | None = None
    deadline: date | None = None

    @field_validator("required_skills", "preferred_skills")
    @classmethod
    def _clean(cls, v: list[str]) -> list[str]:
        seen, out = set(), []
        for s in (x.strip() for x in v):
            if s and s.lower() not in seen:
                seen.add(s.lower()); out.append(s)
        return out


class ExtractRequest(BaseModel):
    text: str = Field(min_length=20, max_length=20_000)
