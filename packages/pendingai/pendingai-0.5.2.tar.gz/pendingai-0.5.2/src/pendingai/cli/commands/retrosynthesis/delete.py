#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typer import Typer

from pendingai.cli.console import Console
from pendingai.cli.constants import HELP_PANEL_RETROSYNTHESIS_COMMANDS
from pendingai.cli.context import PendingAiContext
from pendingai.cli.parameters.retrosynthesis import JobIdArgument

console = Console()
app = Typer()


@app.command(rich_help_panel=HELP_PANEL_RETROSYNTHESIS_COMMANDS)
def delete(ctx: PendingAiContext, job_id: JobIdArgument) -> None:
    """
    Delete a retrosynthesis Job and any calculated results.
    """
    with console.status("Deleting retrosynthesis Job..."):
        ctx.obj["client"].retrosynthesis.jobs.delete(job_id)
