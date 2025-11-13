#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typer import Typer

from .list_models import app as list_models_app
from .sample import app as sample_app

app = Typer(
    name="generator",
    help=(
        "Powerful and efficient solution for creating novel, diverse, drug-like "
        "molecules. For more information refer to the documentation with "
        "<pendingai docs>."
    ),
    short_help="Generative solution for molecules.",
    no_args_is_help=True,
)

app.add_typer(list_models_app)

# Generator Operations =================================================

app.add_typer(sample_app)
