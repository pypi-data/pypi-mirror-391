#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typer import Typer

from pendingai.cli.console import Console
from pendingai.cli.constants import HELP_PANEL_BATCH_OPERATIONS
from pendingai.cli.context import PendingAiContext
from pendingai.cli.parameters.retrosynthesis import BatchIdArgument

console = Console()
app = Typer()


@app.command(rich_help_panel=HELP_PANEL_BATCH_OPERATIONS)
def delete_batch(ctx: PendingAiContext, batch_id: BatchIdArgument) -> None:
    """
    Delete a retrosynthesis Batch.
    """
    with console.status("Deleting retrosynthesis Batch..."):
        ctx.obj["client"].retrosynthesis.batches.delete(batch_id)
