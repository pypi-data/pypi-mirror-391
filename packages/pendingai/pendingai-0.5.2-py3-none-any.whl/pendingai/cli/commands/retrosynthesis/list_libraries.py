#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typer import Exit, Typer

from pendingai.cli.console import Console
from pendingai.cli.context import PendingAiContext
from pendingai.cli.renderables.retrosynthesis import RetrosynthesisLibraryTable

console = Console()
app = Typer()


@app.command()
def list_libraries(ctx: PendingAiContext):
    """
    Retrieve a list of selectable Libraries.
    """
    with console.status("Fetching building block Libraries..."):
        data = ctx.obj["client"].retrosynthesis.libraries.list(limit=100)

    if len(data.data) == 0:
        console.print("[yellow]! No results found.")
        raise Exit(0)

    tdata = [
        RetrosynthesisLibraryTable.LibraryData(
            id=entry.id,
            name=entry.name,
            version=entry.version,
            available_from=entry.available_from,
        )
        for entry in data.data
    ]
    table = RetrosynthesisLibraryTable(tdata)
    console.print(table, new_line_start=True)
