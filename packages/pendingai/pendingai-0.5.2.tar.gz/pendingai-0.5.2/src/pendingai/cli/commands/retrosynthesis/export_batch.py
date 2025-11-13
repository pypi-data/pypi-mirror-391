#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
from pathlib import Path

import yaml
from rich.prompt import Confirm
from typer import BadParameter, Exit, Typer

from pendingai.cli.console import Console
from pendingai.cli.constants import HELP_PANEL_BATCH_OPERATIONS
from pendingai.cli.context import PendingAiContext
from pendingai.cli.parameters import (
    ForceOption,
    OutputFilepathOption,
)
from pendingai.cli.parameters.retrosynthesis import (
    BatchIdArgument,
    ExportBatchFormat,
    ExportBatchFormatOption,
)
from pendingai.cli.renderables.retrosynthesis import (
    RetrosynthesisBatchQueue,
    RetrosynthesisBatchSummary,
)

console = Console()
app = Typer()


@app.command(rich_help_panel=HELP_PANEL_BATCH_OPERATIONS)
def export_batch(
    ctx: PendingAiContext,
    batch_id: BatchIdArgument,
    output_file: OutputFilepathOption = Path.cwd() / "results.json",
    format: ExportBatchFormatOption = ExportBatchFormat.JSON,
    force: ForceOption = False,
) -> None:
    """
    Export results from a retrosynthesis Batch to file.
    """
    # Handle output file naming based on the format; if the default name
    # is used then the suffix needs to be updated to match the format.
    if output_file == Path.cwd() / "results.json":
        output_file = output_file.with_suffix(f".{format}")

    if output_file.exists() and not force:
        prompt: str = f"[dim]? Overwrite [blue u]{output_file}[/blue u]"
        if not Confirm.ask(prompt, console=console, default=False):
            raise Exit(0)

    with console.status("Retrieving retrosynthesis Batch results..."):
        batch = ctx.obj["client"].retrosynthesis.batches.retrieve(batch_id)
        results = ctx.obj["client"].retrosynthesis.batches.result(batch_id)

    if len(results) == 0:
        raise BadParameter(
            f"Batch ID has no results: '{batch_id}'.", param_hint="BATCH_ID"
        )

    console.print(
        RetrosynthesisBatchSummary(
            batch_id=batch.id,
            name=batch.name,
            number_of_jobs=batch.number_of_jobs,
            created=batch.created,
            updated=batch.updated,
            filename=batch.filename,
        ),
        new_line_start=True,
    )
    console.print(
        RetrosynthesisBatchQueue(
            sum(1 for r in results if not r.completed),
            sum(1 for r in results if r.completed),
            0,
            sum(1 for r in results if (r.synthesizable and r.completed)),
        ),
        new_line_start=True,
    )

    if format == ExportBatchFormat.JSON:
        content = json.dumps([dict(r) for r in results], indent=2)
    elif format == ExportBatchFormat.YAML:
        content = yaml.safe_dump([dict(r) for r in results], indent=2)
    elif format == ExportBatchFormat.CSV:
        lines = [",".join([str(v) for v in dict(r).values()]) for r in results]
        content = "\n".join(lines)
    elif format == ExportBatchFormat.TSV:
        lines = ["\t".join([str(v) for v in dict(r).values()]) for r in results]
        content = "\n".join(lines)
    output_file.write_text(content)

    console.print(f"\n[green]✓ Saved results to file: '{output_file}'.")
