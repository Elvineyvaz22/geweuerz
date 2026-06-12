from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup

from discovery import DISCOVERY_COLUMNS


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def strip_rating(name: str) -> str:
    return re.sub(r"\s+\d+(?:\.\d+)?$", "", name).strip()


def platform_from_alt(value: str) -> str:
    text = value.lower()
    if "instagram" in text:
        return "instagram"
    if "tiktok" in text:
        return "tiktok"
    if "youtube" in text:
        return "youtube"
    if "ugc" in text:
        return "ugc"
    if "amazon" in text:
        return "amazon"
    return text.replace(" creator", "").strip()


def username_from_url(url: str) -> str:
    parts = [part for part in urlparse(url).path.split("/") if part]
    return parts[0] if parts else ""


def country_from_location(location: str) -> str:
    if not location:
        return ""
    last = location.split(",")[-1].strip()
    code_map = {
        "US": "United States",
        "AE": "United Arab Emirates",
        "GB": "United Kingdom",
        "FR": "France",
        "PL": "Poland",
        "CA": "Canada",
        "AU": "Australia",
    }
    return code_map.get(last.upper(), last)


def parse_collabstr_html(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    soup = BeautifulSoup(input_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    rows: list[dict[str, str]] = []

    for card in soup.select(".profile-listing-holder"):
        link = card.select_one("a[href*='collabstr.com/']")
        name = card.select_one(".profile-listing-owner-name")
        title = card.select_one(".profile-listing-title")
        price = card.select_one(".profile-listing-price")
        location = card.select_one(".profile-listing-category")
        followers = card.select_one(".profile-listing-followers")
        platform_img = card.select_one(".profile-listing-platform-img")

        profile_url = link.get("href", "").strip() if link else ""
        raw_followers = clean_text(followers.get_text(" ", strip=True)) if followers else ""
        follower_value = "" if raw_followers.upper() == "UGC" else raw_followers
        platform = platform_from_alt(platform_img.get("alt", "")) if platform_img else ""
        title_text = clean_text(title.get_text(" ", strip=True)) if title else ""
        price_text = clean_text(price.get_text(" ", strip=True)) if price else ""
        location_text = clean_text(location.get_text(" ", strip=True)) if location else ""

        if not profile_url:
            continue

        rows.append(
            {
                "name": strip_rating(clean_text(name.get_text(" ", strip=True))) if name else "",
                "username": username_from_url(profile_url),
                "platform": platform,
                "followers": follower_value,
                "engagement_rate": "",
                "country": country_from_location(location_text),
                "bio": f"{title_text}. Collabstr price: {price_text}. Location: {location_text}.",
                "email": "no email",
                "avg_views": "",
                "posts": "",
                "profile_url": profile_url,
            }
        )

    return pd.DataFrame(rows, columns=DISCOVERY_COLUMNS).drop_duplicates(subset=["profile_url"], keep="first")

