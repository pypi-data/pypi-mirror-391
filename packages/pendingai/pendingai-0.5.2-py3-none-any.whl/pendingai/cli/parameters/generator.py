#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import Annotated, Optional

from typer import BadParameter, Option

from pendingai.cli.console import Console
from pendingai.cli.context import PendingAiContext

console = Console()


# Command option callbacks =============================================


def callback_model_id(ctx: PendingAiContext, model_id: Optional[str]) -> Optional[str]:
    """Callback for validating a generator model."""
    if model_id:
        with console.status("Checking generator model exists..."):
            data = ctx.obj["client"].generator.models.list(limit=100)
        if model_id not in [model.id for model in data.data]:
            raise BadParameter(f"Model ID does not exist: '{model_id}'.")
    return model_id


# Command options ======================================================


NumberOfSamplesOption = Annotated[
    int,
    Option(
        "-n",
        "--num-samples",
        help="Number of molecules to sample.",
        min=1,
        clamp=True,
    ),
]


ModelIdOption = Annotated[
    Optional[str],
    Option(
        "--model",
        "-m",
        help="Model ID to use for molecule sampling.",
        callback=callback_model_id,
        show_default=False,
    ),
]
