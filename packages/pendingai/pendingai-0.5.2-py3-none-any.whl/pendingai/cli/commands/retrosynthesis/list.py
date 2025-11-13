#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typer import Exit, Typer

from pendingai.cli.console import Console
from pendingai.cli.constants import HELP_PANEL_RETROSYNTHESIS_COMMANDS
from pendingai.cli.context import PendingAiContext
from pendingai.cli.parameters.retrosynthesis import PaginationOptions
from pendingai.cli.renderables.retrosynthesis import RetrosynthesisJobTable

console = Console()
app = Typer()


@app.command(rich_help_panel=HELP_PANEL_RETROSYNTHESIS_COMMANDS)
def list(
    ctx: PendingAiContext,
    page: PaginationOptions.Page = 1,
    limit: PaginationOptions.Limit = 10,
    after: PaginationOptions.After = None,
    before: PaginationOptions.Before = None,
) -> None:
    """
    Retrieve a list of retrosynthesis Jobs.
    """
    with console.status("Fetching retrosynthesis Jobs..."):
        data = ctx.obj["client"].retrosynthesis.jobs.list(page, after, before, limit)

    if len(data.data) == 0:
        console.print("[yellow]! No results found.")
        raise Exit(0)

    tdata = [
        RetrosynthesisJobTable.JobData(
            id=entry.id,
            query=entry.query,
            created=entry.created,
            status=entry.status,
            routes=entry.routes,
        )
        for entry in data.data
    ]
    table = RetrosynthesisJobTable(tdata)
    console.print(table, new_line_start=True)
    if data.metadata["has_next"]:
        console.print(f"\n[dim]Tip: Use '--after {data.data[-1].id}' for more results.")
