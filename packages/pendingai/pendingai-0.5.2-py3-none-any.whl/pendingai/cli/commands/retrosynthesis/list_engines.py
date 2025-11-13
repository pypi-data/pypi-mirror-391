#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typer import Exit, Typer

from pendingai.cli.console import Console
from pendingai.cli.context import PendingAiContext
from pendingai.cli.renderables.retrosynthesis import RetrosynthesisEngineTable

console = Console()
app = Typer()


@app.command()
def list_engines(ctx: PendingAiContext):
    """
    Retrieve a list of selectable Engines.
    """
    with console.status("Fetching retrosynthesis Engines..."):
        data = ctx.obj["client"].retrosynthesis.engines.list(limit=100)

    if len(data.data) == 0:
        console.print("[yellow]! No results found.")
        raise Exit(0)

    tdata = [
        RetrosynthesisEngineTable.EngineData(
            id=entry.id,
            name=entry.name,
            last_alive=entry.last_alive,
            suspended=entry.suspended,
        )
        for entry in data.data
    ]
    table = RetrosynthesisEngineTable(tdata)
    console.print(table, new_line_start=True)
