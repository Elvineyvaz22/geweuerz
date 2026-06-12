from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from cleaning import load_and_clean_csv
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


if __name__ == "__main__":
    app()

