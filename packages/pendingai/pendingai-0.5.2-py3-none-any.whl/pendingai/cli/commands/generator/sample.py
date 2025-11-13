#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from pathlib import Path
from typing import Set

from rich.progress import Progress, TaskID
from rich.prompt import Confirm
from typer import Exit, Typer

from pendingai.cli.console import Console
from pendingai.cli.context import PendingAiContext
from pendingai.cli.parameters import FileAppendOption, ForceOption, OutputFilepathOption
from pendingai.cli.parameters.generator import ModelIdOption, NumberOfSamplesOption

console = Console()
app = Typer()


@app.command()
def sample(
    ctx: PendingAiContext,
    output_file: OutputFilepathOption = Path.cwd() / "sample.smi",
    number_of_samples: NumberOfSamplesOption = 500,
    model_id: ModelIdOption = None,
    file_append: FileAppendOption = False,
    force: ForceOption = False,
) -> None:
    """
    Sample molecules from a generator model and save as SMILES to file.
    """
    file_flag: str = "a" if file_append else "w"
    if output_file.exists() and not force and not file_append:
        prompt: str = f"[dim]? Overwrite [blue u]{output_file}[/blue u]"
        if not Confirm.ask(prompt, console=console, default=False):
            raise Exit(0)

    # Check that if a model is specified and exists, that it is ready
    # for sampling and online, otherwise exit with an error message.
    if model_id:
        with console.status("Checking model status..."):
            status: str = ctx.obj["client"].generator.models.status(model_id).status
        if status != "online":
            console.print(f"[fail]! Model is not available for sampling: '{model_id}'")
            raise Exit(1)

    # Iterate over mini-batch sampling requests until requested sample
    # size is met and write intermediates to file.
    samples: Set[str] = set()
    with open(output_file, file_flag) as f:
        with Progress(transient=True) as progress:
            task: TaskID = progress.add_task("Sampling...", total=number_of_samples)
            while not progress.finished:
                smiles = ctx.obj["client"].generator.samples.create(model_id, 500).smiles
                f.writelines([x + "\n" for x in set(smiles) - samples])
                samples.update(smiles)
                progress.update(task, completed=len(samples))

    console.print(f"[success]Sampled {len(samples)} molecules: '{output_file}'.")
