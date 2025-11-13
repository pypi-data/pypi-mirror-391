#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List, Optional, TypedDict

from rich.table import Column, Table


class GeneratorModelsTable(Table):
    """Table containing generator Model entries.

    Usage:

        tdata = [GeneratorModelsTable.ModelData(...) for ...]
        table = GeneratorModelsTable(tdata)
        console.print(table)
    """

    columns: List[Column] = [
        Column("NAME", style="", max_width=32, no_wrap=True),
        Column("ID", style="cyan", width=32),
        Column("VERSION", max_width=8, style="", no_wrap=True),
        Column("STATUS"),
    ]

    class ModelData(TypedDict):
        """Input data for a Job."""

        id: str
        name: Optional[str]
        version: Optional[str]
        status: bool

    def add_row(self, entry: ModelData):
        super().add_row(
            entry["name"] or "[i dim]null",
            entry["id"],
            entry["version"] or "[i dim]null",
            "[green]online" if entry["status"] else "[red]offline",
        )

    def __init__(self, entries: List[ModelData]):
        super().__init__(*type(self).columns, box=None)
        entries.sort(key=lambda x: x["status"])
        [self.add_row(x) for x in entries]
