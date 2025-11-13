#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typer import Exit, Typer

from pendingai.cli.console import Console
from pendingai.cli.constants import HELP_PANEL_BATCH_OPERATIONS
from pendingai.cli.context import PendingAiContext
from pendingai.cli.parameters.retrosynthesis import PaginationOptions
from pendingai.cli.renderables.retrosynthesis import RetrosynthesisBatchTable

console = Console()
app = Typer()


@app.command(rich_help_panel=HELP_PANEL_BATCH_OPERATIONS)
def list_batches(
    ctx: PendingAiContext,
    page: PaginationOptions.Page = 1,
    limit: PaginationOptions.Limit = 10,
    after: PaginationOptions.After = None,
    before: PaginationOptions.Before = None,
) -> None:
    """
    Retrieve a list of retrosynthesis Batches.
    """
    with console.status("Fetching retrosynthesis Batches..."):
        data = ctx.obj["client"].retrosynthesis.batches.list(page, after, before, limit)

    if len(data.data) == 0:
        console.print("[yellow]! No results found.")
        raise Exit(0)

    tdata = [
        RetrosynthesisBatchTable.BatchData(
            id=entry.id,
            name=entry.name,
            created=entry.created,
            number_of_jobs=entry.number_of_jobs,
            completed_jobs=entry.completed_jobs,
            filename=entry.filename,
        )
        for entry in data.data
    ]
    table = RetrosynthesisBatchTable(tdata)
    console.print(table, new_line_start=True)
    if data.metadata["has_next"]:
        console.print(f"\n[dim]Tip: Use '--after {data.data[-1].id}' for more results.")
