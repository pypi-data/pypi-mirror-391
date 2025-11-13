#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List

from typer import BadParameter, Typer

from pendingai.cli.console import Console
from pendingai.cli.constants import HELP_PANEL_BATCH_OPERATIONS
from pendingai.cli.context import PendingAiContext
from pendingai.cli.parameters import SkipErrorsOption
from pendingai.cli.parameters.retrosynthesis import (
    BatchDescriptionOption,
    BatchNameOption,
    RetrosynthesisOptions,
    SmilesFileArgument,
)
from pendingai.cli.renderables.retrosynthesis import (
    RetrosynthesisBatchSummary,
    RetrosynthesisParameterSummary,
)
from pendingai.constants import smiles_regex

console = Console()
app = Typer()


@app.command(rich_help_panel=HELP_PANEL_BATCH_OPERATIONS)
def create_batch(
    ctx: PendingAiContext,
    smiles_file: SmilesFileArgument,
    name: BatchNameOption = None,
    description: BatchDescriptionOption = None,
    retrosynthesis_engine: RetrosynthesisOptions.RetrosynthesisEngine = None,
    building_block_libraries: RetrosynthesisOptions.BuildingBlockLibraries = [],
    number_of_routes: RetrosynthesisOptions.NumberOfRoutes = 1,
    processing_time: RetrosynthesisOptions.ProcessingTime = 60,
    reaction_limit: RetrosynthesisOptions.ReactionLimit = 10,
    building_block_limit: RetrosynthesisOptions.BuildingBlockLimit = 10,
    skip_errors: SkipErrorsOption = False,
) -> None:
    """
    Create a retrosynthesis Batch.
    """
    # Collect the SMILES from the input file and validate each line,
    # collect as a unique list for batch submission and report any
    # errors encountered.
    lines: List[str] = smiles_file.read_text().splitlines()
    smiles: List[str] = list(set([x.strip() for x in lines if x.strip()]))
    for s in smiles:
        if not smiles_regex.match(s):
            if not skip_errors:
                raise BadParameter(f"Invalid SMILES: '{s}'.", param_hint="SMILES_FILE")
            smiles.remove(s)

    if len(smiles) == 0:
        raise BadParameter("No valid SMILES molecules found.", param_hint="SMILES_FILE")

    with console.status("Creating retrosynthesis Batch..."):
        batch = ctx.obj["client"].retrosynthesis.batches.create(
            smiles,
            name=name,
            description=description,
            filename=smiles_file.name,
            retrosynthesis_engine=retrosynthesis_engine,
            building_block_libraries=building_block_libraries,
            number_of_routes=number_of_routes,
            processing_time=processing_time,
            reaction_limit=reaction_limit,
            building_block_limit=building_block_limit,
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
        RetrosynthesisParameterSummary(
            batch.parameters["retrosynthesis_engine"],
            batch.parameters["building_block_libraries"],
            batch.parameters["number_of_routes"],
            batch.parameters["processing_time"],
            batch.parameters["reaction_limit"],
            batch.parameters["building_block_limit"],
        ),
        new_line_start=True,
    )
