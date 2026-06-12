from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Influencer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = ""
    username: str = ""
    platform: str = ""
    followers: int = 0
    engagement_rate: float = 0.0
    country: str = ""
    bio: str = ""
    email: str = "no email"
    avg_views: int | None = None
    posts: int | None = None
    profile_url: str = ""

    @field_validator("name", "username", "platform", "country", "bio", "email", "profile_url", mode="before")
    @classmethod
    def stringify(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @field_validator("followers", mode="before")
    @classmethod
    def validate_followers(cls, value: object) -> int:
        if value in (None, ""):
            return 0
        return int(value)

    @field_validator("engagement_rate", mode="before")
    @classmethod
    def validate_engagement(cls, value: object) -> float:
        if value in (None, ""):
            return 0.0
        return float(value)

    @field_validator("avg_views", "posts", mode="before")
    @classmethod
    def optional_int(cls, value: object) -> int | None:
        if value in (None, ""):
            return None
        return int(value)

    @field_validator("email")
    @classmethod
    def default_email(cls, value: str) -> str:
        return value if value else "no email"


class ScoredInfluencer(Influencer):
    score: int = 0
    grade: str = ""
    match_reasons: str = ""
    warnings: str = ""


class Summary(BaseModel):
    total_imported: int
    total_after_dedupe: int
    a_count: int
    b_count: int
    c_count: int
    d_count: int
    average_score: float
    top_countries: str
    top_platforms: str


TEMPLATE_COLUMNS = [
    "name",
    "username",
    "platform",
    "followers",
    "engagement_rate",
    "country",
    "bio",
    "email",
    "avg_views",
    "posts",
    "profile_url",
]

