#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from datetime import datetime
from typing import Any, List, Optional, TypedDict

from rich.table import Column, Table

from pendingai.constants import local_tz


def _convert_datetime_to_delta_str(dt: datetime) -> str:
    """Convert a datetime to a human-readable delta string."""
    secs: int = int((datetime.now(local_tz) - dt.astimezone(local_tz)).total_seconds())
    if secs < 60:
        return f"{secs} secs ago"
    elif secs < (3600 * 2):
        return f"{secs // 60} mins ago"
    elif secs < (86400 * 2):
        return f"{secs // 3600} hrs ago"
    elif secs < (604800 * 2):
        return f"{secs // 86400} days ago"
    return f"{secs // 604800} weeks ago"


def _convert_datetime_to_str(dt: datetime) -> str:
    """Convert a datetime to a human-readable string."""
    return dt.astimezone(local_tz).strftime("%a %b %d %H:%M:%S %Y")


class RetrosynthesisJobTable(Table):
    """Table containing retrosynthesis Job entries.

    Usage:

        tdata = [RetrosynthesisJobTable.JobData(...) for ...]
        table = RetrosynthesisJobTable(tdata)
        console.print(table)
    """

    columns: List[Column] = [
        Column("CREATED", style="", no_wrap=True),
        Column("ID", style="cyan", width=25),
        Column("SMILES", max_width=32, style="yellow", no_wrap=True),
        Column("RESULT", no_wrap=True),
    ]

    class JobData(TypedDict):
        """Input data for a Job."""

        id: str
        query: Optional[str]
        created: datetime
        status: Optional[str]
        routes: Optional[List[Any]]

    @staticmethod
    def _colour_result(status: str, number_of_routes: int) -> str:
        """Convert a status and result count into synthesizable flag."""
        if status not in {"completed", "failed"}:
            return "[dim i yellow]processing"
        elif number_of_routes == 0:
            return "[red]not producible"
        return "[green]producible"

    def add_row(self, entry: JobData):
        super().add_row(
            _convert_datetime_to_str(entry["created"]),
            entry["id"],
            entry["query"] or "[i dim]unknown",
            self._colour_result(entry["status"] or "failed", len(entry["routes"] or [])),
        )

    def __init__(self, entries: List[JobData]):
        super().__init__(*type(self).columns, box=None)
        [self.add_row(x) for x in entries]


class RetrosynthesisBatchTable(Table):
    """Table containing retrosynthesis Batch entries.

    Usage:

        tdata = [RetrosynthesisBatchTable.BatchData(...) for ...]
        table = RetrosynthesisBatchTable(tdata)
        console.print(table)
    """

    columns: List[Column] = [
        Column("CREATED", style="", no_wrap=True),
        Column("ID", style="cyan"),
        Column("Name", style="yellow"),
        Column("Size", justify="right"),
        Column("Status", justify="right"),
        Column("Filename", style="blue"),
    ]

    class BatchData(TypedDict):
        """Input data for a Batch."""

        id: str
        name: Optional[str]
        created: datetime
        number_of_jobs: int
        completed_jobs: int
        filename: Optional[str]

    @staticmethod
    def _colour_number_of_jobs(value: int) -> str:
        """Convert number of jobs to a bin colour string."""
        if value >= 10_000:
            return f"[not b dark_orange]{value}[/]"
        elif value >= 1_000:
            return f"[not b sandy_brown]{value}[/]"
        return f"[not b pink1]{value}[/]"

    @staticmethod
    def _colour_status(completed_jobs: int, number_of_jobs: int) -> str:
        """Convert batch status to a bin colour string."""
        status: float = (completed_jobs / number_of_jobs) * 100
        if status >= 100.0:
            return f"[not b dark_sea_green4]{status:.2f}%[/]"
        elif status >= 75.0:
            return f"[not b yellow]{status:.2f}%[/]"
        elif status >= 50.0:
            return f"[not b sandy_brown]{status:.2f}%[/]"
        elif status >= 25.0:
            return f"[not b red]{status:.2f}%[/]"
        return f"[not b dark_red]{status:.2f}%[/]"

    def add_row(self, entry: BatchData):
        # Colouring is apply in binned ranges for some fields which is
        # handled by static methods to keep this method more readable.
        super().add_row(
            _convert_datetime_to_str(entry["created"]),
            entry["id"],
            entry["name"] or "[i dim]null",
            self._colour_number_of_jobs(entry["number_of_jobs"]),
            self._colour_status(entry["completed_jobs"], entry["number_of_jobs"]),
            entry["filename"] or "[i dim]unknown",
        )

    def __init__(self, entries: List[BatchData]):
        super().__init__(*type(self).columns, box=None)
        [self.add_row(x) for x in entries]


class RetrosynthesisLibraryTable(Table):
    """Table containing retrosynthesis Library entries.

    Usage:

        tdata = [RetrosynthesisLibraryTable.LibraryData(...) for ...]
        table = RetrosynthesisLibraryTable(tdata)
        console.print(table)
    """

    columns: List[Column] = [
        Column("NAME", max_width=20, no_wrap=True),
        Column("ID", style="cyan"),
        Column("VERSION"),
        Column("LAST UPDATED", justify="right"),
    ]

    class LibraryData(TypedDict):
        """Input data for an Library."""

        id: str
        name: Optional[str]
        version: Optional[str]
        available_from: datetime

    def add_row(self, entry: LibraryData):
        super().add_row(
            entry["name"] or "[dim i]unknown",
            entry["id"],
            entry["version"] or "latest",
            _convert_datetime_to_delta_str(entry["available_from"]),
        )

    def __init__(self, entries: List[LibraryData]):
        super().__init__(*type(self).columns, box=None)
        entries.sort(key=lambda x: x["available_from"], reverse=True)
        [self.add_row(x) for x in entries]


class RetrosynthesisEngineTable(Table):
    """Table containing retrosynthesis Engine entries.

    Usage:

        tdata = [RetrosynthesisEngineTable.EngineData(...) for ...]
        table = RetrosynthesisEngineTable(tdata)
        console.print(table)
    """

    columns: List[Column] = [
        Column("NAME", max_width=20, no_wrap=True),
        Column("ID", style="cyan"),
        Column("STATUS"),
        Column("LAST ACTIVE", justify="right"),
    ]

    class EngineData(TypedDict):
        """Input data for an Engine."""

        id: str
        name: Optional[str]
        last_alive: datetime
        suspended: bool

    def add_row(self, entry: EngineData):
        # Provide either a red or green colour based on the status of
        # the engine to help with readability for inactive engines.
        colour: str = "[red]" if entry["suspended"] else "[green]"
        super().add_row(
            entry["name"],
            entry["id"],
            f"{colour}offline" if entry["suspended"] else f"{colour}active",
            colour + _convert_datetime_to_delta_str(entry["last_alive"]),
        )

    def __init__(self, entries: List[EngineData]):
        super().__init__(*type(self).columns, box=None)
        entries.sort(key=lambda x: (not x["suspended"], x["last_alive"]), reverse=True)
        [self.add_row(x) for x in entries]


class RetrosynthesisBatchSummary(Table):
    """Summary table for a retrosynthesis Batch."""

    def __init__(
        self,
        batch_id: str,
        name: Optional[str],
        number_of_jobs: int,
        created: datetime,
        updated: datetime,
        filename: Optional[str],
    ):
        super().__init__(
            Column(style="reset"),
            Column(style="reset"),
            Column(style="reset"),
            title="RETROSYNTHESIS BATCH",
            title_justify="left",
            title_style="bold",
            show_header=False,
            box=None,
        )

        self.add_row("ID", "=", batch_id)
        self.add_row("Name", "=", name or "[dim]null")
        self.add_row("Size", "=", str(number_of_jobs))
        self.add_row("Created", "=", _convert_datetime_to_str(created))
        self.add_row("Updated", "=", _convert_datetime_to_str(updated))
        self.add_row("Filename", "=", filename or "[dim]null")


class RetrosynthesisJobSummary(Table):
    """Summary table for a retrosynthesis Job."""

    def __init__(
        self,
        job_id: str,
        query: str,
        created: datetime,
        updated: datetime,
        status: str,
    ):
        super().__init__(
            Column(style="reset"),
            Column(style="reset"),
            Column(style="reset"),
            title="RETROSYNTHESIS JOB",
            title_justify="left",
            title_style="bold",
            show_header=False,
            box=None,
        )

        self.add_row("ID", "=", job_id)
        self.add_row("Molecule", "=", query)
        self.add_row("Created", "=", _convert_datetime_to_str(created))
        self.add_row("Updated", "=", _convert_datetime_to_str(updated))
        self.add_row("Status", "=", status.title())


class RetrosynthesisParameterSummary(Table):
    """Summary table for retrosynthesis parameters."""

    def __init__(
        self,
        retrosynthesis_engine: str,
        building_block_libraries: List[str],
        number_of_routes: int,
        processing_time: int,
        reaction_limit: int,
        building_block_limit: int,
    ):
        super().__init__(
            Column(style="reset"),
            Column(style="reset"),
            Column(style="reset"),
            title="RETROSYNTHESIS PARAMETERS",
            title_justify="left",
            title_style="bold",
            show_header=False,
            box=None,
        )
        self.add_row("Engine", "=", retrosynthesis_engine)
        self.add_row("Libraries", "=", ", ".join(building_block_libraries))
        self.add_row("Max Routes", "=", str(number_of_routes))
        self.add_row("Max Seconds", "=", str(processing_time))
        self.add_row("Reaction Limit", "=", str(reaction_limit))
        self.add_row("Molecule Limit", "=", str(building_block_limit))


class RetrosynthesisBatchQueue(Table):
    """Table containing retrosynthesis Batch queue entries."""

    def __init__(
        self,
        queued: int,
        completed: int,
        failed: int,
        accessible: int,
    ):
        super().__init__(
            Column("Batch Group", style=""),
            Column("Queued", style=""),
            Column("Complete", style=""),
            Column("Failed", style=""),
            Column("Synthesizable", style=""),
            header_style="",
            title="SUMMARY",
            title_style="b",
            title_justify="left",
            pad_edge=True,
            box=None,
        )
        self.add_row(
            "total",
            str(queued),
            str(completed),
            str(failed),
            str(accessible),
        )
