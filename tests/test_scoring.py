from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from cleaning import parse_engagement_rate, parse_followers
from collabstr import country_from_location, platform_from_alt, strip_rating
from discovery import build_queries, detect_platform, extract_email, extract_followers, extract_username, is_profile_url
from scoring import calculate_grade, score_niche


def test_parse_followers_k() -> None:
    assert parse_followers("10K") == 10000


def test_parse_followers_m() -> None:
    assert parse_followers("1.2M") == 1200000


def test_parse_engagement_percent() -> None:
    assert parse_engagement_rate("3.5%") == 3.5


def test_parse_engagement_decimal_rate() -> None:
    assert parse_engagement_rate("0.035") == 3.5


def test_parse_engagement_comma_percent() -> None:
    assert parse_engagement_rate("3,5%") == 3.5


def test_niche_keyword_score() -> None:
    score, positives, negatives = score_niche("Digital nomad sharing travel, airport and esim tips")
    assert score > 0
    assert "digital nomad" in positives
    assert not negatives


def test_final_grade_calculation() -> None:
    assert calculate_grade(75).startswith("A")
    assert calculate_grade(60).startswith("B")
    assert calculate_grade(45).startswith("C")
    assert calculate_grade(44).startswith("D")


def test_detect_platform_and_username() -> None:
    url = "https://www.instagram.com/travelcreator/"
    assert detect_platform(url) == "instagram"
    assert extract_username(url, "instagram") == "travelcreator"


def test_reject_post_url() -> None:
    assert not is_profile_url("https://www.instagram.com/p/abc123", "instagram")
    assert not is_profile_url("https://www.tiktok.com/@creator/video/123", "tiktok")


def test_extract_followers_and_email_from_snippet() -> None:
    text = "12K Followers, Travel tips and collabs: creator@example.com"
    assert extract_followers(text) == "12K"
    assert extract_email(text) == "creator@example.com"


def test_build_relaxed_queries() -> None:
    queries = build_queries(["travel"], ["Germany"], ["instagram"], max_queries=4, relaxed=True)
    assert len(queries) == 4
    assert any("instagram travel Germany" in query for query in queries)


def test_collabstr_helpers() -> None:
    assert strip_rating("Gemma & Nitish 5.0") == "Gemma & Nitish"
    assert platform_from_alt("instagram creator") == "instagram"
    assert country_from_location("Dubai, DU, AE") == "United Arab Emirates"
