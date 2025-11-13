#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import webbrowser
from pathlib import Path
from typing import List

import yaml
from typer import Typer

from pendingai.cli.console import Console
from pendingai.cli.constants import HELP_PANEL_RETROSYNTHESIS_COMMANDS
from pendingai.cli.context import PendingAiContext
from pendingai.cli.parameters import OutputDirectoryOption
from pendingai.cli.parameters.retrosynthesis import (
    DepictOption,
    ExportFormat,
    ExportFormatOption,
    JobIdsArgument,
)
from pendingai.cli.utils.generate_html import generate_html_report

console = Console()
app = Typer()


@app.command(rich_help_panel=HELP_PANEL_RETROSYNTHESIS_COMMANDS)
def export(
    ctx: PendingAiContext,
    job_ids: JobIdsArgument,
    output_directory: OutputDirectoryOption = Path.cwd() / "out",
    format: ExportFormatOption = ExportFormat.JSON,
    depict: DepictOption = False,
) -> None:
    """
    Export results for one or more retrosynthesis Jobs to file.
    """
    output_directory.mkdir(parents=True, exist_ok=True)

    viewable_job_ids: List[str] = job_ids.copy()
    for job_id in job_ids:
        export_basename: str = f"job_{job_id}.{format.value}"
        export_filepath: Path = output_directory / export_basename
        has_html_saved: bool = export_filepath.with_suffix("").exists()
        if export_filepath.exists() or (format == ExportFormat.HTML and has_html_saved):
            continue

        # Retrieve the results for the job; check that the job is done
        # before saving the results in the required export format.
        with console.status("Fetching retrosynthesis Job results..."):
            job = ctx.obj["client"].retrosynthesis.jobs.retrieve(job_id)

        if job.status not in ["completed", "failed"]:
            console.print(f"[yellow]Skip '{job_id}' as job is not completed.")
            continue

        if format == ExportFormat.JSON:
            content = json.dumps(dict(job), indent=2)
            export_filepath.write_text(content)

        elif format == ExportFormat.YAML:
            content = yaml.safe_dump(dict(job), indent=2)
            export_filepath.write_text(content)

        elif format == ExportFormat.HTML:
            export_filepath = export_filepath.with_suffix("")
            if len(job.routes) == 0:
                console.print(f"[yellow]Skip '{job_id}' as job contains no results.")
                viewable_job_ids.remove(job_id)
                continue
            generate_html_report(output_directory, dict(job), index=False)

        console.print(f"[green]Save '{job_id}' to '{export_filepath}'.")

    # When exporting to HTML, open each job result in the web browser.
    if format == ExportFormat.HTML and depict:
        for job_id in viewable_job_ids:
            html_filepath: Path = output_directory / f"job_{job_id}" / "index.html"
            webbrowser.open_new_tab(f"file://{html_filepath}")
