from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from cleaning import load_and_clean_csv
from collabstr import parse_collabstr_html
from discovery import DEFAULT_COUNTRIES, DEFAULT_KEYWORDS, discover_leads, leads_to_dataframe
from exporter import export_to_excel
from models import TEMPLATE_COLUMNS
from scoring import build_summary, score_influencers

app = typer.Typer(help="EyDost eSIM influencer CSV scoring tool.")


@app.command()
def filter(
    input: Path = typer.Option(..., "--input", "-i", help="Input influencer CSV file."),
    output: Path = typer.Option(..., "--output", "-o", help="Output Excel file path."),
) -> None:
    """Clean, score and export influencer candidates."""
    try:
        influencers, total_imported, total_after_dedupe = load_and_clean_csv(input)
        if not influencers:
            raise ValueError("No valid influencer rows found after cleaning.")
        scored = score_influencers(influencers)
        summary = build_summary(scored, total_imported, total_after_dedupe)
        export_to_excel(scored, summary, output)
    except Exception as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"Exported {len(scored)} scored influencers to {output}")


@app.command()
def template(
    output: Path = typer.Option(..., "--output", "-o", help="Output CSV template path."),
) -> None:
    """Create an empty CSV template with supported columns."""
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=TEMPLATE_COLUMNS).to_csv(output, index=False)
    typer.echo(f"Template written to {output}")


@app.command()
def discover(
    output: Path = typer.Option(..., "--output", "-o", help="Output discovered leads CSV path."),
    keywords: list[str] | None = typer.Option(None, "--keyword", "-k", help="Keyword to search. Can be repeated."),
    countries: list[str] | None = typer.Option(None, "--country", "-c", help="Country/audience market. Can be repeated."),
    platforms: list[str] | None = typer.Option(None, "--platform", "-p", help="instagram, tiktok, youtube. Can be repeated."),
    per_query: int = typer.Option(5, "--per-query", help="Max search results to inspect per query."),
    max_queries: int = typer.Option(40, "--max-queries", help="Max search queries to run."),
    delay_seconds: float = typer.Option(1.0, "--delay", help="Delay between search requests."),
    source: str = typer.Option("all", "--source", help="Search source: all, duckduckgo, or bing."),
    relaxed: bool = typer.Option(True, "--relaxed/--strict", help="Use broader query variants."),
) -> None:
    """Discover public social profile leads from web search and save them as CSV."""
    selected_platforms = [platform.lower() for platform in (platforms or ["instagram", "tiktok", "youtube"])]
    invalid_platforms = sorted(set(selected_platforms) - {"instagram", "tiktok", "youtube"})
    if invalid_platforms:
        raise typer.BadParameter(f"Unsupported platform(s): {', '.join(invalid_platforms)}")
    selected_source = source.lower()
    if selected_source not in {"all", "duckduckgo", "bing"}:
        raise typer.BadParameter("Unsupported source. Use all, duckduckgo, or bing.")

    try:
        leads = discover_leads(
            keywords=keywords or DEFAULT_KEYWORDS,
            countries=countries or DEFAULT_COUNTRIES,
            platforms=selected_platforms,
            per_query=per_query,
            max_queries=max_queries,
            delay_seconds=delay_seconds,
            source=selected_source,
            relaxed=relaxed,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        leads_to_dataframe(leads).to_csv(output, index=False)
    except Exception as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"Discovered {len(leads)} unique leads and wrote them to {output}")


@app.command("import-collabstr")
def import_collabstr(
    input: Path = typer.Option(..., "--input", "-i", help="Saved Collabstr HTML file."),
    output: Path = typer.Option(..., "--output", "-o", help="Output CSV path."),
) -> None:
    """Parse a saved Collabstr influencer listing HTML file into CSV."""
    try:
        df = parse_collabstr_html(input)
        if df.empty:
            raise ValueError("No Collabstr influencer cards found in HTML.")
        output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output, index=False)
    except Exception as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"Imported {len(df)} Collabstr influencers to {output}")


if __name__ == "__main__":
    app()
