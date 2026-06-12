from __future__ import annotations

from collections import Counter

from keywords import CONTACT_KEYWORDS, EU_COUNTRIES, GEO_FIT_COUNTRIES, NEGATIVE_KEYWORDS, POSITIVE_KEYWORDS
from models import Influencer, ScoredInfluencer, Summary


def contains_any(text: str, keywords: list[str]) -> list[str]:
    lower_text = text.lower()
    return [keyword for keyword in keywords if keyword in lower_text]


def score_niche(bio: str) -> tuple[int, list[str], list[str]]:
    positives = contains_any(bio, POSITIVE_KEYWORDS)
    negatives = contains_any(bio, NEGATIVE_KEYWORDS)
    score = min(30, len(positives) * 4)
    score = max(0, score - len(negatives) * 10)
    return score, positives, negatives


def score_audience(followers: int) -> int:
    if 5_000 <= followers <= 150_000:
        return 20
    if 150_001 <= followers <= 500_000:
        return 14
    if 500_001 <= followers <= 1_000_000:
        return 8
    if followers > 1_000_000:
        return 4
    if 1_000 <= followers <= 4_999:
        return 8
    return 2


def score_engagement(engagement_rate: float) -> int:
    if engagement_rate >= 5:
        return 20
    if engagement_rate >= 3:
        return 16
    if engagement_rate >= 1.5:
        return 10
    if engagement_rate >= 0.5:
        return 5
    return 1


def score_contactability(email: str, bio: str) -> tuple[int, list[str]]:
    if email and email.lower() != "no email":
        return 10, ["email available"]
    contact_matches = contains_any(bio, CONTACT_KEYWORDS)
    if contact_matches:
        return 6, [f"contact keyword: {', '.join(contact_matches)}"]
    return 0, []


def score_geography(country: str) -> int:
    normalized = country.strip().lower()
    if not normalized:
        return 4
    if normalized in GEO_FIT_COUNTRIES or normalized in EU_COUNTRIES:
        return 10
    return 4


def score_view_efficiency(avg_views: int | None, followers: int) -> tuple[int, str | None]:
    if avg_views is None or followers <= 0:
        return 3, "avg_views missing"
    ratio = avg_views / followers
    if ratio > 0.5:
        return 10, None
    if ratio >= 0.2:
        return 7, None
    if ratio >= 0.1:
        return 4, None
    return 1, "low view efficiency"


def calculate_grade(score: int) -> str:
    if score >= 75:
        return "A - priority partner"
    if score >= 60:
        return "B - good candidate"
    if score >= 45:
        return "C - maybe test"
    return "D - skip"


def score_influencer(influencer: Influencer) -> ScoredInfluencer:
    reasons: list[str] = []
    warnings: list[str] = []

    niche_score, positives, negatives = score_niche(influencer.bio)
    if positives:
        reasons.append(f"niche: {', '.join(positives[:6])}")
    if negatives:
        warnings.append(f"negative keywords: {', '.join(negatives)}")

    audience_score = score_audience(influencer.followers)
    reasons.append(f"audience score {audience_score}")

    engagement_score = score_engagement(influencer.engagement_rate)
    reasons.append(f"engagement score {engagement_score}")

    contact_score, contact_reasons = score_contactability(influencer.email, influencer.bio)
    reasons.extend(contact_reasons)
    if contact_score == 0:
        warnings.append("no direct contact signal")

    geo_score = score_geography(influencer.country)
    if geo_score == 10:
        reasons.append(f"geo fit: {influencer.country}")

    view_score, view_warning = score_view_efficiency(influencer.avg_views, influencer.followers)
    if view_warning:
        warnings.append(view_warning)

    total = niche_score + audience_score + engagement_score + contact_score + geo_score + view_score
    return ScoredInfluencer(
        **influencer.model_dump(),
        score=int(total),
        grade=calculate_grade(int(total)),
        match_reasons="; ".join(reasons),
        warnings="; ".join(warnings),
    )


def score_influencers(influencers: list[Influencer]) -> list[ScoredInfluencer]:
    scored = [score_influencer(influencer) for influencer in influencers]
    return sorted(scored, key=lambda item: (item.score, item.grade), reverse=True)


def build_summary(scored: list[ScoredInfluencer], total_imported: int, total_after_dedupe: int) -> Summary:
    grade_counts = Counter(item.grade[0] for item in scored)
    countries = Counter(item.country or "Unknown" for item in scored)
    platforms = Counter(item.platform or "unknown" for item in scored)
    average_score = round(sum(item.score for item in scored) / len(scored), 2) if scored else 0.0

    return Summary(
        total_imported=total_imported,
        total_after_dedupe=total_after_dedupe,
        a_count=grade_counts.get("A", 0),
        b_count=grade_counts.get("B", 0),
        c_count=grade_counts.get("C", 0),
        d_count=grade_counts.get("D", 0),
        average_score=average_score,
        top_countries=", ".join(f"{name}: {count}" for name, count in countries.most_common(5)),
        top_platforms=", ".join(f"{name}: {count}" for name, count in platforms.most_common(5)),
    )

