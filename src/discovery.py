from __future__ import annotations

import re
import time
from dataclasses import dataclass
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup


DEFAULT_KEYWORDS = [
    "travel",
    "travel creator",
    "travel blogger",
    "travel influencer",
    "reiseblogger",
    "travel hacks",
    "budget travel",
    "digital nomad",
    "nomad life",
    "airport tips",
    "cheap flights",
    "europe travel",
    "turkey travel",
    "istanbul travel",
    "solo travel",
    "family travel",
    "student travel",
    "expat travel",
    "auswandern",
    "leben in deutschland",
    "esim travel",
    "roaming",
    "internet abroad travel",
]

DEFAULT_COUNTRIES = [
    "Germany",
    "Turkey",
    "Azerbaijan",
    "United Kingdom",
    "France",
    "Italy",
    "Spain",
    "Netherlands",
    "Poland",
    "Georgia",
    "UAE",
    "USA",
]

PLATFORM_DOMAINS = {
    "instagram": ("instagram.com",),
    "tiktok": ("tiktok.com",),
    "youtube": ("youtube.com", "youtu.be"),
}

DISCOVERY_COLUMNS = [
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


@dataclass(frozen=True)
class SearchLead:
    name: str
    username: str
    platform: str
    country: str
    bio: str
    email: str
    followers: str
    profile_url: str


def build_queries(
    keywords: list[str],
    countries: list[str],
    platforms: list[str],
    max_queries: int,
    relaxed: bool = True,
) -> list[str]:
    queries: list[str] = []
    for platform in platforms:
        domain = PLATFORM_DOMAINS[platform][0]
        for country in countries:
            for keyword in keywords:
                query_variants = [
                    f"site:{domain} {keyword} {country}",
                    f"{domain} {keyword} {country} creator",
                ]
                if relaxed:
                    query_variants.extend(
                        [
                            f"{platform} {keyword} {country}",
                            f"{keyword} {country} {platform} followers",
                        ]
                    )
                for query in query_variants:
                    queries.append(query)
                    if len(queries) >= max_queries:
                        return queries
    return queries


def unwrap_duckduckgo_url(url: str) -> str:
    parsed = urlparse(url)
    if "duckduckgo.com" not in parsed.netloc:
        return url
    target = parse_qs(parsed.query).get("uddg", [""])[0]
    return unquote(target) if target else url


def unwrap_bing_url(url: str) -> str:
    parsed = urlparse(url)
    if "bing.com" not in parsed.netloc:
        return url
    target = parse_qs(parsed.query).get("u", [""])[0]
    return unquote(target) if target else url


def detect_platform(url: str) -> str | None:
    netloc = urlparse(url).netloc.lower()
    for platform, domains in PLATFORM_DOMAINS.items():
        if any(domain in netloc for domain in domains):
            return platform
    return None


def extract_username(url: str, platform: str) -> str:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return ""

    if platform == "youtube" and parts[0] in {"channel", "c", "user"} and len(parts) > 1:
        return parts[1]
    if platform == "youtube" and parts[0].startswith("@"):
        return parts[0]
    return parts[0]


def clean_profile_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme or 'https'}://{parsed.netloc}{parsed.path}".rstrip("/")


def is_profile_url(url: str, platform: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return False
    blocked_parts = {
        "p",
        "reel",
        "reels",
        "tv",
        "explore",
        "stories",
        "accounts",
        "privacy",
        "about",
        "tag",
        "tags",
        "music",
        "video",
        "shorts",
        "watch",
        "share",
        "photo",
        "status",
    }
    parts = [part.lower() for part in path.split("/") if part]
    if any(part in blocked_parts for part in parts):
        return False
    first = parts[0]
    if platform == "youtube":
        return (first.startswith("@") and len(parts) == 1) or (first in {"channel", "c", "user"} and len(parts) == 2)
    if platform in {"instagram", "tiktok"}:
        return len(parts) == 1
    return True


def search_duckduckgo(query: str, limit: int, timeout: int = 20) -> list[tuple[str, str, str]]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 EyDostInfluencerResearch/1.0"},
        timeout=timeout,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results: list[tuple[str, str, str]] = []
    for result in soup.select(".result"):
        link = result.select_one(".result__a")
        snippet = result.select_one(".result__snippet")
        if not link or not link.get("href"):
            continue
        title = re.sub(r"\s+", " ", link.get_text(" ", strip=True))
        description = re.sub(r"\s+", " ", snippet.get_text(" ", strip=True)) if snippet else ""
        results.append((title, unwrap_duckduckgo_url(link["href"]), description))
        if len(results) >= limit:
            break
    return results


def search_bing(query: str, limit: int, timeout: int = 20) -> list[tuple[str, str, str]]:
    url = f"https://www.bing.com/search?q={quote_plus(query)}"
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 EyDostInfluencerResearch/1.0"},
        timeout=timeout,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results: list[tuple[str, str, str]] = []
    for result in soup.select("li.b_algo"):
        link = result.select_one("h2 a")
        snippet = result.select_one(".b_caption p") or result.select_one("p")
        if not link or not link.get("href"):
            continue
        title = re.sub(r"\s+", " ", link.get_text(" ", strip=True))
        description = re.sub(r"\s+", " ", snippet.get_text(" ", strip=True)) if snippet else ""
        results.append((title, unwrap_bing_url(link["href"]), description))
        if len(results) >= limit:
            break
    return results


def extract_email(text: str) -> str:
    match = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text)
    return match.group(0) if match else "no email"


def extract_followers(text: str) -> str:
    patterns = [
        r"([\d.,]+\s*[kKmM]?)\s+Followers",
        r"([\d.,]+\s*[kKmM]?)\s+followers",
        r"Followers[:\s]+([\d.,]+\s*[kKmM]?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).replace(" ", "")
    return ""


def search_all_sources(query: str, limit: int, source: str) -> list[tuple[str, str, str]]:
    searchers = []
    if source in {"duckduckgo", "all"}:
        searchers.append(search_duckduckgo)
    if source in {"bing", "all"}:
        searchers.append(search_bing)

    results: list[tuple[str, str, str]] = []
    seen_urls: set[str] = set()
    for searcher in searchers:
        try:
            source_results = searcher(query, limit)
        except requests.RequestException:
            continue
        for title, url, snippet in source_results:
            clean_url = clean_profile_url(url)
            if clean_url in seen_urls:
                continue
            seen_urls.add(clean_url)
            results.append((title, url, snippet))
            if len(results) >= limit:
                return results
    return results


def discover_leads(
    keywords: list[str],
    countries: list[str],
    platforms: list[str],
    per_query: int,
    max_queries: int,
    delay_seconds: float,
    source: str = "all",
    relaxed: bool = True,
) -> list[SearchLead]:
    queries = build_queries(keywords, countries, platforms, max_queries, relaxed=relaxed)
    leads_by_key: dict[tuple[str, str], SearchLead] = {}

    for query in queries:
        country = next((country for country in countries if country.lower() in query.lower()), "")
        results = search_all_sources(query, per_query, source)

        for title, url, snippet in results:
            platform = detect_platform(url)
            if not platform:
                continue
            clean_url = clean_profile_url(url)
            if not is_profile_url(clean_url, platform):
                continue
            username = extract_username(clean_url, platform)
            if not username:
                continue
            key = (platform, username.lower())
            leads_by_key.setdefault(
                key,
                SearchLead(
                    name=title,
                    username=username,
                    platform=platform,
                    country=country,
                    bio=snippet,
                    email=extract_email(f"{title} {snippet}"),
                    followers=extract_followers(f"{title} {snippet}"),
                    profile_url=clean_url,
                ),
            )

        if delay_seconds > 0:
            time.sleep(delay_seconds)

    return list(leads_by_key.values())


def leads_to_dataframe(leads: list[SearchLead]) -> pd.DataFrame:
    rows = []
    for lead in leads:
        rows.append(
            {
                "name": lead.name,
                "username": lead.username,
                "platform": lead.platform,
                "followers": lead.followers,
                "engagement_rate": "",
                "country": lead.country,
                "bio": lead.bio,
                "email": lead.email,
                "avg_views": "",
                "posts": "",
                "profile_url": lead.profile_url,
            }
        )
    return pd.DataFrame(rows, columns=DISCOVERY_COLUMNS)
