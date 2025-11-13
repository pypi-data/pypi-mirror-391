#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typer import Typer

from pendingai.cli.console import Console
from pendingai.cli.constants import HELP_PANEL_RETROSYNTHESIS_COMMANDS
from pendingai.cli.context import PendingAiContext
from pendingai.cli.parameters.retrosynthesis import RetrosynthesisOptions, SmilesArgument
from pendingai.cli.renderables.retrosynthesis import (
    RetrosynthesisJobSummary,
    RetrosynthesisParameterSummary,
)

console = Console()
app = Typer()


@app.command(rich_help_panel=HELP_PANEL_RETROSYNTHESIS_COMMANDS)
def create(
    ctx: PendingAiContext,
    smiles: SmilesArgument,
    retrosynthesis_engine: RetrosynthesisOptions.RetrosynthesisEngine = None,
    building_block_libraries: RetrosynthesisOptions.BuildingBlockLibraries = [],
    number_of_routes: RetrosynthesisOptions.NumberOfRoutes = 1,
    processing_time: RetrosynthesisOptions.ProcessingTime = 60,
    reaction_limit: RetrosynthesisOptions.ReactionLimit = 10,
    building_block_limit: RetrosynthesisOptions.BuildingBlockLimit = 10,
) -> None:
    """
    Create a retrosynthesis Job for a query SMILES structure.
    """

    with console.status("Creating retrosynthesis Job..."):
        job = ctx.obj["client"].retrosynthesis.jobs.create(
            smiles,
            retrosynthesis_engine,
            building_block_libraries,
            number_of_routes=number_of_routes,
            processing_time=processing_time,
            reaction_limit=reaction_limit,
            building_block_limit=building_block_limit,
        )

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
    console.print(
        RetrosynthesisParameterSummary(
            job.parameters["retrosynthesis_engine"],
            job.parameters["building_block_libraries"],
            job.parameters["number_of_routes"],
            job.parameters["processing_time"],
            job.parameters["reaction_limit"],
            job.parameters["building_block_limit"],
        ),
        new_line_start=True,
    )
