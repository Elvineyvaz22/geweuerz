from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from cleaning import parse_engagement_rate, parse_followers
from discovery import detect_platform, extract_username, is_profile_url
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
