#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typer import Typer

from pendingai.cli.console import Console
from pendingai.cli.context import PendingAiContext
from pendingai.cli.renderables.generator import GeneratorModelsTable

console = Console()
app = Typer()


@app.command()
def list_models(ctx: PendingAiContext) -> None:
    """
    List molecule generator models.
    """

    with console.status("Fetching generator models..."):
        data = ctx.obj["client"].generator.models.list(limit=100)
        statuses = [
            ctx.obj["client"].generator.models.status(model.id).status
            for model in data.data
        ]

    tdata = [
        GeneratorModelsTable.ModelData(
            id=model.id,
            name=model.name,
            version=model.version,
            status=status == "online",
        )
        for model, status in zip(data.data, statuses)
    ]
    console.print(GeneratorModelsTable(tdata), new_line_start=True)
