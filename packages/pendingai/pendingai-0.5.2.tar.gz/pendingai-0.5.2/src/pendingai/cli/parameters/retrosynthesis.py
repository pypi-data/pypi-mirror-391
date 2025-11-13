#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from enum import Enum
from pathlib import Path
from typing import Annotated, List, Optional, Set

from typer import Argument, BadParameter, Option

from pendingai.cli.console import Console
from pendingai.cli.context import PendingAiContext
from pendingai.constants import smiles_regex

console = Console()


# Command argument callbacks ===========================================


def callback_smiles(smiles: str) -> str:
    """Validate that the provided SMILES string is allowed."""
    smiles = smiles.strip()
    if not smiles:
        raise BadParameter("SMILES molecule cannot be empty.")
    if not smiles_regex.match(smiles):
        raise BadParameter("Invalid characters in SMILES molecule.")
    return smiles


def callback_smiles_file(smiles_file: Path) -> Path:
    """Validate that the provided SMILES file exists and is readable."""
    try:
        smiles_lines: List[str] = smiles_file.read_text().splitlines()
        smiles: Set[str] = set([x for x in smiles_lines if x.strip()])
    except Exception:
        raise BadParameter("Unable to read contents of SMILES file.")
    if len(smiles) == 0:
        raise BadParameter("At least one valid SMILES entry is required.")
    return smiles_file


def callback_job_id(ctx: PendingAiContext, job_id: str) -> str:
    """Callback for validating a retrosynthesis Job ID."""
    try:
        with console.status("Checking Job ID exists..."):
            ctx.obj["client"].retrosynthesis.jobs.retrieve(job_id)
    except Exception:
        raise BadParameter(f"Job ID does not exist: '{job_id}'.")
    return job_id


def callback_job_ids(ctx: PendingAiContext, job_ids: List[str]) -> List[str]:
    """Callback for validating a list of retrosynthesis Job IDs."""
    with console.status("Checking Job IDs exist..."):
        for job_id in job_ids:
            try:
                ctx.obj["client"].retrosynthesis.jobs.retrieve(job_id)
            except Exception:
                raise BadParameter(f"Job ID does not exist: '{job_id}'.")
    return job_ids


def callback_batch_id(ctx: PendingAiContext, batch_id: str) -> str:
    """Callback for validating a retrosynthesis Batch ID."""
    try:
        with console.status("Checking Batch ID exists..."):
            ctx.obj["client"].retrosynthesis.batches.retrieve(batch_id)
    except Exception:
        raise BadParameter(f"Batch ID does not exist: '{batch_id}'.")
    return batch_id


# Command arguments ====================================================

# Retrosynthesis Job and Batch creation commands require input SMILES
# molecules; these can be provided either as a single SMILES string or
# as a filepath to a file containing line-delimited SMILES strings.

SmilesArgument = Annotated[
    str,
    Argument(
        help="A SMILES molecule to perform retrosynthesis on.",
        callback=callback_smiles,
        metavar="SMILES",
        show_default=False,
    ),
]
SmilesFileArgument = Annotated[
    Path,
    Argument(
        help="A filepath containing line-delimited SMILES molecules.",
        callback=callback_smiles_file,
        metavar="SMILES_FILE",
        resolve_path=True,
        show_default=False,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
]

# Retrosynthesis Job and Batch operations such as exporting or resource
# deletion require one or more ID arguments for performing operations.

JobIdArgument = Annotated[
    str,
    Argument(
        help="A retrosynthesis Job ID.",
        callback=callback_job_id,
        metavar="JOB_ID",
        show_default=False,
    ),
]
JobIdsArgument = Annotated[
    List[str],
    Argument(
        help="One or more retrosynthesis Job IDs.",
        callback=callback_job_ids,
        metavar="JOB_IDS",
        show_default=False,
    ),
]
BatchIdArgument = Annotated[
    str,
    Argument(
        help="A retrosynthesis Batch ID.",
        callback=callback_batch_id,
        metavar="BATCH_ID",
        show_default=False,
    ),
]


# Command option callbacks =============================================


def callback_batch_name(name: Optional[str]) -> Optional[str]:
    """Callback for checking Batch name validity."""
    if name is not None:
        name = name.strip()
        if not name:
            return None
        if len(name) > 512:
            raise BadParameter("Exceeds maximum length of 512 characters.")
    return name


def callback_batch_description(description: Optional[str]) -> Optional[str]:
    """Callback for checking Batch description validity."""
    if description is not None:
        description = description.strip()
        if not description:
            return None
        if len(description) > 2048:
            raise BadParameter("Exceeds maximum length of 2048 characters.")
    return description


# Command options ======================================================


class ExportFormat(str, Enum):
    """Enumeration of supported retrosynthesis export formats."""

    JSON = "json"
    YAML = "yaml"
    HTML = "html"


ExportFormatOption = Annotated[
    ExportFormat,
    Option(
        "--format",
        help="Result format to use for exporting retrosynthesis results.",
        case_sensitive=False,
    ),
]


class ExportBatchFormat(str, Enum):
    """Enumeration of supported batch export formats."""

    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    TSV = "tsv"


ExportBatchFormatOption = Annotated[
    ExportBatchFormat,
    Option(
        "--format",
        help="Result format to use for exporting retrosynthesis batch results.",
        case_sensitive=False,
    ),
]

DepictOption = Annotated[
    bool,
    Option(
        "--depict",
        help="Whether to open route depictions in HTML reports in the webbrowser.",
        is_flag=True,
    ),
]

# Additional optional parameters for retrosynthesis Batches; used to
# create or identify a retrosynthesis Batch.

BatchNameOption = Annotated[
    Optional[str],
    Option(
        "--name",
        "-n",
        help="An optional name for a retrosynthesis Batch.",
        callback=callback_batch_name,
        show_default=False,
    ),
]
BatchDescriptionOption = Annotated[
    Optional[str],
    Option(
        "--description",
        "-d",
        help="An optional description for a retrosynthesis Batch.",
        callback=callback_batch_description,
        show_default=False,
    ),
]

# Retrosynthesis parameters are used when submitting a retrosynthesis
# Job or Batch so they are shared across multiple commands.


class RetrosynthesisOptions:
    """Namespace for grouping retrosynthesis parameter options."""

    HELP_PANEL_NAMESPACE = "Retrosynthesis Parameters"
    """Grouped help panel name for retrosynthesis options."""

    class Defaults:
        """Default retrosynthesis option values."""

        NUMBER_OF_ROUTES_MIN: int = 1
        NUMBER_OF_ROUTES_MAX: int = 50
        PROCESSING_TIME_MIN: int = 60
        PROCESSING_TIME_MAX: int = 600
        REACTION_LIMIT_MIN: int = 1
        REACTION_LIMIT_MAX: int = 25
        BUILDING_BLOCK_LIMIT_MIN: int = 1
        BUILDING_BLOCK_LIMIT_MAX: int = 25

    @staticmethod
    def callback_retrosynthesis_engine(
        ctx: PendingAiContext, value: Optional[str]
    ) -> Optional[str]:
        """Callback for validating retrosynthesis engine option."""
        if value:
            with console.status("Checking Engine ID exists..."):
                engines = ctx.obj["client"].retrosynthesis.engines.list(limit=100)
            if value not in [engine.id for engine in engines.data]:
                raise BadParameter(f"Engine ID does not exist: '{value}'.")
        return value

    @staticmethod
    def callback_building_block_libraries(
        ctx: PendingAiContext, value: Optional[List[str]]
    ) -> Optional[List[str]]:
        """Callback for validating building block libraries option."""
        if value:
            with console.status("Checking Library IDs exist..."):
                libraries = ctx.obj["client"].retrosynthesis.libraries.list(limit=100)
            for library in value:
                if library not in [lib.id for lib in libraries.data]:
                    raise BadParameter(f"Library ID does not exist: '{library}'.")
            return list(set(value))
        return []

    RetrosynthesisEngine = Annotated[
        Optional[str],
        Option(
            "--engine",
            "-e",
            help="An Engine ID to use for retrosynthesis.",
            callback=callback_retrosynthesis_engine,
            rich_help_panel=HELP_PANEL_NAMESPACE,
            show_default=False,
        ),
    ]
    BuildingBlockLibraries = Annotated[
        Optional[List[str]],
        Option(
            "--library",
            "-l",
            help="One or more Library IDs to use for retrosynthesis.",
            callback=callback_building_block_libraries,
            rich_help_panel=HELP_PANEL_NAMESPACE,
            show_default=False,
            metavar="LIST",
        ),
    ]
    NumberOfRoutes = Annotated[
        int,
        Option(
            "--num-routes",
            help="Max number of retrosynthesis routes to generate.",
            rich_help_panel=HELP_PANEL_NAMESPACE,
            min=Defaults.NUMBER_OF_ROUTES_MIN,
            max=Defaults.NUMBER_OF_ROUTES_MAX,
        ),
    ]
    ProcessingTime = Annotated[
        int,
        Option(
            "--time-limit",
            help="Max allowed time in seconds for a retrosynthesis Job.",
            rich_help_panel=HELP_PANEL_NAMESPACE,
            min=Defaults.PROCESSING_TIME_MIN,
            max=Defaults.PROCESSING_TIME_MAX,
        ),
    ]
    ReactionLimit = Annotated[
        int,
        Option(
            "--reaction-limit",
            help="Max times a reaction can be used in retrosynthesis routes.",
            rich_help_panel=HELP_PANEL_NAMESPACE,
            min=Defaults.REACTION_LIMIT_MIN,
            max=Defaults.REACTION_LIMIT_MAX,
        ),
    ]
    BuildingBlockLimit = Annotated[
        int,
        Option(
            "--block-limit",
            help="Max times a building block can be used in retrosynthesis routes.",
            rich_help_panel=HELP_PANEL_NAMESPACE,
            min=Defaults.BUILDING_BLOCK_LIMIT_MIN,
            max=Defaults.BUILDING_BLOCK_LIMIT_MAX,
        ),
    ]


# Pagination parameters are used for listing resources in a paginated
# format; these are shared across multiple resource listing commands.


class PaginationOptions:
    """Namespace for grouping pagination search options."""

    HELP_PANEL_NAMESPACE = "Pagination Options"
    """Grouped help panel name for pagination options."""

    class Defaults:
        """Default pagination option values."""

        PAGE_MIN: int = 1
        PAGE_MAX: int = 1_000_000
        LIMIT_MIN: int = 1
        LIMIT_MAX: int = 100

    Page = Annotated[
        int,
        Option(
            "--page",
            "-p",
            help="Page number being fetched.",
            rich_help_panel=HELP_PANEL_NAMESPACE,
            show_default=True,
            clamp=True,
            min=Defaults.PAGE_MIN,
            max=Defaults.PAGE_MAX,
        ),
    ]
    Limit = Annotated[
        int,
        Option(
            "--limit",
            "-l",
            help="Number of results per page.",
            rich_help_panel=HELP_PANEL_NAMESPACE,
            show_default=True,
            clamp=True,
            min=Defaults.LIMIT_MIN,
            max=Defaults.LIMIT_MAX,
        ),
    ]
    After = Annotated[
        Optional[str],
        Option(
            "--after",
            help="Cursor for results after a specific resource ID.",
            rich_help_panel=HELP_PANEL_NAMESPACE,
            show_default=False,
        ),
    ]
    Before = Annotated[
        Optional[str],
        Option(
            "--before",
            help="Cursor for results before a specific resource ID.",
            rich_help_panel=HELP_PANEL_NAMESPACE,
            show_default=False,
        ),
    ]
