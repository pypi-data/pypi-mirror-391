#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typer import Typer

from pendingai.cli.console import Console
from pendingai.cli.constants import HELP_PANEL_RETROSYNTHESIS_COMMANDS
from pendingai.cli.context import PendingAiContext
from pendingai.cli.parameters.retrosynthesis import JobIdArgument
from pendingai.cli.renderables.retrosynthesis import RetrosynthesisJobSummary

console = Console()
app = Typer()


@app.command(rich_help_panel=HELP_PANEL_RETROSYNTHESIS_COMMANDS)
def status(ctx: PendingAiContext, job_id: JobIdArgument) -> None:
    """
    Retrieve status information for a retrosynthesis Job.
    """
    with console.status("Fetching retrosynthesis Job..."):
        job = ctx.obj["client"].retrosynthesis.jobs.retrieve(job_id)

    console.print(
        RetrosynthesisJobSummary(
            job.id,
            job.query,
            job.created,
            job.updated,
            job.status,
        ),
        new_line_start=True,
    )
