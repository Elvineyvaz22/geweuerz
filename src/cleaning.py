from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

from models import Influencer


COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "name": ("name", "full_name", "creator_name"),
    "username": ("username", "handle", "profile"),
    "platform": ("platform", "social_network", "channel"),
    "followers": ("followers", "followers_count", "audience_size"),
    "engagement_rate": ("engagement_rate", "engagement", "er"),
    "country": ("country", "location", "audience_country"),
    "bio": ("bio", "description", "about"),
    "email": ("email", "contact_email", "business_email"),
    "avg_views": ("avg_views", "views", "average_views"),
    "posts": ("posts", "post_count"),
    "profile_url": ("url", "profile_url", "link"),
}


COUNTRY_ALIASES = {
    "az": "Azerbaijan",
    "azerbaycan": "Azerbaijan",
    "azerbaijan": "Azerbaijan",
    "de": "Germany",
    "germany": "Germany",
    "deutschland": "Germany",
    "tr": "Turkey",
    "turkey": "Turkey",
    "turkiye": "Turkey",
    "türkiye": "Turkey",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "gb": "United Kingdom",
    "usa": "United States",
    "us": "United States",
    "united states": "United States",
    "uae": "United Arab Emirates",
    "united arab emirates": "United Arab Emirates",
}


def normalize_column_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def build_column_map(columns: list[str]) -> dict[str, str]:
    normalized = {normalize_column_name(column): column for column in columns}
    mapping: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            key = normalize_column_name(alias)
            if key in normalized:
                mapping[canonical] = normalized[key]
                break
    return mapping


def parse_number(value: Any) -> float:
    if value is None or pd.isna(value):
        return 0.0
    text = str(value).strip().replace(" ", "")
    if not text:
        return 0.0

    multiplier = 1.0
    if text[-1:].lower() == "k":
        multiplier = 1_000.0
        text = text[:-1]
    elif text[-1:].lower() == "m":
        multiplier = 1_000_000.0
        text = text[:-1]

    if "," in text and "." not in text:
        comma_parts = text.split(",")
        text = ".".join(comma_parts) if len(comma_parts[-1]) <= 2 else "".join(comma_parts)
    else:
        text = text.replace(",", "")

    cleaned = re.sub(r"[^0-9.]", "", text)
    if not cleaned:
        return 0.0
    return float(cleaned) * multiplier


def parse_followers(value: Any) -> int:
    return int(round(parse_number(value)))


def parse_optional_int(value: Any) -> int | None:
    if value is None or pd.isna(value) or str(value).strip() == "":
        return None
    return int(round(parse_number(value)))


def parse_engagement_rate(value: Any) -> float:
    if value is None or pd.isna(value):
        return 0.0
    original = str(value).strip()
    if not original:
        return 0.0
    has_percent = "%" in original
    normalized = original.replace("%", "").replace(",", ".").strip()
    number = parse_number(normalized)
    if has_percent:
        return round(number, 4)
    if 0 < number <= 1:
        return round(number * 100, 4)
    return round(number, 4)


def normalize_country(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    key = text.lower()
    return COUNTRY_ALIASES.get(key, text.title())


def normalize_platform(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip().lower()


def load_and_clean_csv(input_path: Path) -> tuple[list[Influencer], int, int]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)
    if df.empty:
        raise ValueError("Input CSV is empty.")

    total_imported = len(df)
    column_map = build_column_map(list(df.columns))
    cleaned_rows: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        data: dict[str, Any] = {}
        for canonical in COLUMN_ALIASES:
            source = column_map.get(canonical)
            data[canonical] = row[source] if source else ""

        data["followers"] = parse_followers(data["followers"])
        data["engagement_rate"] = parse_engagement_rate(data["engagement_rate"])
        data["avg_views"] = parse_optional_int(data["avg_views"])
        data["posts"] = parse_optional_int(data["posts"])
        data["platform"] = normalize_platform(data["platform"])
        data["country"] = normalize_country(data["country"])
        data["email"] = str(data["email"]).strip() if str(data["email"]).strip() else "no email"
        cleaned_rows.append(data)

    clean_df = pd.DataFrame(cleaned_rows)
    clean_df["dedupe_key"] = clean_df["username"].fillna("").str.lower().str.strip()
    clean_df.loc[clean_df["dedupe_key"] == "", "dedupe_key"] = clean_df.index.astype(str)
    clean_df = clean_df.drop_duplicates(subset=["dedupe_key"], keep="first").drop(columns=["dedupe_key"])

    influencers = [Influencer.model_validate(record) for record in clean_df.to_dict(orient="records")]
    return influencers, total_imported, len(influencers)
