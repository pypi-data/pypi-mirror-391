#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from enum import Enum
from pathlib import Path
from typing import Annotated

from typer import Option


class Format(str, Enum):
    """Supported export formats."""

    JSON = "json"
    CSV = "csv"
    YAML = "yaml"


FormatOption = Annotated[
    Format,
    Option(
        "--format",
        help="The format any results should be exported in.",
        case_sensitive=False,
    ),
]
ForceOption = Annotated[
    bool,
    Option(
        "--force",
        "-f",
        help="Force the command to run, skip confirmation prompts.",
        is_flag=True,
    ),
]
RenderJson = Annotated[
    bool,
    Option(
        "--json",
        help="Render any text output as JSON.",
        is_flag=True,
    ),
]
FileAppendOption = Annotated[
    bool,
    Option(
        "--append",
        help="Append to the output file without prompting.",
        is_flag=True,
    ),
]


# Command options ======================================================

# Error handling strategy options for commands that may encounter errors
# during runtime that could be skipped, raised, or warned.


class ErrorStrategy(str, Enum):
    """Error handling strategies for commands."""

    RAISE = "raise"
    SKIP = "skip"
    WARN = "warn"


ErrorStrategyOption = Annotated[
    ErrorStrategy,
    Option(
        "--on-error",
        help="An optional error handling strategy to use.",
        case_sensitive=False,
    ),
]
SkipErrorsOption = Annotated[
    bool,
    Option(
        "--skip-errors",
        help="Skip any errors encountered during command execution.",
        is_flag=True,
    ),
]

# Output path options for commands are given with generic help text to
# make them applicable across multiple commands.

OutputFilepathOption = Annotated[
    Path,
    Option(
        "--output",
        "-o",
        help="A filepath to save any command results to.",
        show_default=False,
        resolve_path=True,
        file_okay=True,
        dir_okay=False,
        writable=True,
    ),
]
OutputDirectoryOption = Annotated[
    Path,
    Option(
        "--output",
        "-o",
        help="A directory to save any command results to.",
        resolve_path=True,
        file_okay=False,
        dir_okay=True,
    ),
]
