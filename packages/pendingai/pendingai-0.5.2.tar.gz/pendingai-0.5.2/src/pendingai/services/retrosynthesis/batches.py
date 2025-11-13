#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from requests import Response

from pendingai.api_resources.interfaces import (
    CreateResourceInterface,
    DeleteResourceInterface,
    ListResourceInterface,
    RetrieveResourceInterface,
    UpdateResourceInterface,
)
from pendingai.api_resources.object import DeleteObject, ListObject, Object
from pendingai.api_resources.parser import cast
from pendingai.exceptions import NotFoundError, UnexpectedResponseError


class Batch(Object):
    """
    Batch object.
    """

    class Parameters(Object):
        """
        Batch object parameters.
        """

        retrosynthesis_engine: str
        """
        Engine resource id.
        """
        building_block_libraries: list[str]
        """
        Library resource ids.
        """
        number_of_routes: int
        """
        Maximum number of routes generated from retrosynthesis.
        """
        processing_time: int
        """
        Maximum allowable time for retrosynthesis.
        """
        reaction_limit: int
        """
        Maximum number of times a reaction can appear in a route.
        """
        building_block_limit: int
        """
        Maximum number of times a building block can appear in a route.
        """

    id: str
    """
    Resource id.
    """
    object: str = "batch"
    """
    Resource object type.
    """
    name: str | None
    """
    Optional name of the batch.
    """
    description: str | None
    """
    Optional description of the batch.
    """
    filename: str | None
    """
    Optional filename source of the batch.
    """
    created: datetime
    """
    Time the batch was created.
    """
    updated: datetime
    """
    Time the batch was last updated.
    """
    number_of_jobs: int
    """
    Number of jobs stored in the batch.
    """
    completed_jobs: int = 0
    """
    Number of completed jobs in the batch.
    """
    parameters: dict  # FIXME: Requires object namespace validation.
    """
    Shared batch job parameters.
    """


class BatchStatus(Object):
    """Status information for a `Batch`. Batches require routine polling
    to determine when all jobs have been completed. A batch will be
    completed once the `status` transitions to `completed` and the
    `number_of_jobs` matches `completed_jobs`."""

    status: Literal["submitted", "processing", "completed"]
    """A flag used to annotate the current status of a
    `Batch`. The value may change during retrosynthesis."""
    number_of_jobs: int
    """Number of retrosynthesis `Job` resources that belong to a
    `Batch`. The value can change over time as new jobs are added."""
    completed_jobs: int
    """Total number of retrosynthesis `Job` resources that have
    completed in the `Batch`."""


class BatchResult(Object):
    """An individual retrosynthesis result for a `Job` resource that
    belongs to a `Batch`. Provides a summary of the job status and if
    any retrosynthesis results were found."""

    job_id: str
    """The `id` of the `Job` resource for the containing
    `Batch`. Use this value to retrieve individual retrosynthesis
    results from the dedicated API endpoint."""
    smiles: str
    """The `Job` resource SMILES structure."""
    completed: bool
    """A flag to indicate if the `Job` is completed.
    Retrieving results before a `Batch` status has transitioned to
    completed may contain incomplete jobs."""
    synthesizable: bool
    """A flag to indicate if the SMILES structure was
    found to be synthesizable. The value will be `true` if there is
    at least one retrosynthesis route found."""


class BatchInterface(
    ListResourceInterface[Batch],
    CreateResourceInterface[Batch],
    RetrieveResourceInterface[Batch],
    UpdateResourceInterface[Batch],
    DeleteResourceInterface[Batch],
):
    """Batch resource interface."""

    def list(
        self,
        page: int = 1,
        after: Optional[str] = None,
        before: Optional[str] = None,
        limit: int = 10,
    ) -> ListObject[Batch]:
        """List `Batch` resources. Resources are sorted in reverse
        chronological order based on when they were created. Use the
        `after` and `before` cursor parameters to navigate through
        pages, i.e., the `after` cursor retrieves the next page of
        results, while `before` retrieves the previous page of results.

        Args:
            page (int, optional): Page number to retrieve.
            after (str, optional): An `id` to get the next page.
            before (str, optional): An `id` to get the previous page.
            limit (int, optional): Maximum results to return per page.

        Returns:
            ListObject[Batch]: List of `Batch` resources.
        """
        # Validation of pagination parameters to ensure they fall within
        # correct value bounds before making the API request.
        if not 1 <= page <= 1_000_000:
            raise ValueError("Page number must be between 1 and 1,000,000.")
        if not 1 <= limit <= 100:
            raise ValueError("Page limit must be between 1 and 100.")
        if after and before:
            raise ValueError("Cannot specify both 'after' and 'before' cursors.")

        # Build query parameters for the pagination request. Conditional
        # inclusion of cursor keys is required for the request.
        params: Dict[str, Any] = {"page": page, "limit": limit}
        params.update({"after": after} if after else {})
        params.update({"before": before} if before else {})

        # Make the API request and capture the 400 response to parse any
        # validation errors with the cursor parameters.
        r: Response = self._requestor.get("/retro/v2/batches", params=params)
        if r.status_code == 200:
            return cast(ListObject[Batch], r.json())
        elif r.status_code == 400:
            error: str = r.json().get("error", {}).get("message", "Unknown error.")
            raise ValueError(f"Invalid request: {error}")
        raise UnexpectedResponseError("GET", "list_batch")

    def create(
        self,
        smiles: List[str],
        name: Optional[str] = None,
        description: Optional[str] = None,
        filename: Optional[str] = None,
        retrosynthesis_engine: Optional[str] = None,
        building_block_libraries: Optional[List[str]] = None,
        number_of_routes: int = 1,
        processing_time: int = 60,
        reaction_limit: int = 10,
        building_block_limit: int = 10,
    ) -> Batch:
        """Create a new `Batch` resource to manage a collection
        of retrosynthesis `Job` resources. Individual jobs are provided
        as the list of SMILES structures. All jobs in the batch share
        a common set of provided parameters.

        Args:
            smiles (List[str]): SMILES structures of target molecules.
            name (str, optional): Optional name.
            description (str, optional): Optional description.
            filename (str, optional): Optional filename source.
            retrosynthesis_engine (str, optional): Engine resource id.
                Selects the most recently active by default.
            building_block_libraries (List[str], optional): List of
                library resource ids. Selects all by default.
            number_of_routes (int, optional): Maximum number of routes
                generated from retrosynthesis.
            processing_time (int, optional): Maximum allowable time for
                retrosynthesis in seconds.
            reaction_limit (int, optional): Maximum number of times a
                reaction can appear in a route.
            building_block_limit (int, optional): Maximum number of
                times a building block can appear in a route.

        Returns:
            Batch: The created `Batch` resource.
        """
        # Validation of the request parameters to ensure they fall
        # within correct value bounds before making the API request.
        if not 1 <= number_of_routes <= 50:
            raise ValueError("Number of routes must be between 1 and 50.")
        if not 60 <= processing_time <= 720:
            raise ValueError("Processing time must be between 60 and 720 seconds.")
        if not 1 <= reaction_limit <= 25:
            raise ValueError("Reaction limit must be between 1 and 25.")
        if not 1 <= building_block_limit <= 25:
            raise ValueError("Building block limit must be between 1 and 25.")

        # Build the request payload, ignore conditional paramters that
        # are undefined to use the request defaults.
        body: Dict[str, Any] = {
            "smiles": smiles,
            "name": name,
            "description": description,
            "filename": filename,
            "parameters": {
                "number_of_routes": number_of_routes,
                "processing_time": processing_time,
                "reaction_limit": reaction_limit,
                "building_block_limit": building_block_limit,
            },
        }
        if retrosynthesis_engine:
            body["parameters"]["retrosynthesis_engine"] = retrosynthesis_engine
        if building_block_libraries and len(building_block_libraries) > 0:
            body["parameters"]["building_block_libraries"] = building_block_libraries

        # Make the request to create the Batch resource and capture the
        # 400 and 402 responses to parse any relevant error content.
        r: Response = self._requestor.post("/retro/v2/batches", json=body)
        if r.status_code == 200:
            return cast(Batch, r.json())
        elif r.status_code == 400:
            error: str = r.json().get("error", {}).get("message", "Unknown error.")
            raise ValueError(f"Invalid request: {error}")
        elif r.status_code == 402:  # FIXME
            pass
        raise UnexpectedResponseError("POST", "create_batch")

    def retrieve(self, id: str) -> Batch:
        """Retrieve a `Batch` resource by its `id`. The retrieved
        resource contains metadata about the batch and its parameters,
        but does not include any `Job` results.

        Args:
            id (str): The `id` of the `Batch` resource to retrieve.

        Returns:
            Batch: The requested `Batch` resource.
        """
        r: Response = self._requestor.get(f"/retro/v2/batches/{id}")
        if r.status_code == 200:
            return cast(Batch, r.json())
        elif r.status_code in [404, 422]:
            raise NotFoundError(id, "Batch")
        raise UnexpectedResponseError("GET", "retrieve_batch")

    def status(self, id: str) -> BatchStatus:
        """Retrieve the status of a `Batch` resource by its `id`. The
        status includes information about the number of jobs in the
        batch and how many have been completed.

        Args:
            id (str): The `id` of the `Batch` resource to check status.

        Returns:
            BatchStatus: The status of the requested `Batch` resource.
        """
        r: Response = self._requestor.get(f"/retro/v2/batches/{id}/status")
        if r.status_code == 200:
            return cast(BatchStatus, r.json())
        elif r.status_code in [404, 422]:
            raise NotFoundError(id, "Batch")
        raise UnexpectedResponseError("GET", "status_batch")

    def result(self, id: str) -> List[BatchResult]:
        """Retrieve the collection of results from all `Job` resources
        for the `Batch`. The list contains each job `id` to use for
        retrieving synthetic routes and whether a query molecule was
        synthesizable. Incomplete jobs are marked as such.

        Args:
            id (str): The `id` of the `Batch` resource to get results.

        Returns:
            List[BatchResult]: List of results for each `Job`.
        """
        r: Response = self._requestor.get(
            f"/retro/v2/batches/{id}/result", headers={"accept-encoding": "gzip"}
        )
        if r.status_code == 200:
            return cast(list[BatchResult], r.json())
        elif r.status_code in [404, 422]:
            raise NotFoundError(id, "Batch")
        raise UnexpectedResponseError("GET", "result_batch")

    def update(self, id: str, smiles: List[str]) -> Batch:
        """Update a `Batch` and submit additional retrosynthesis `Job`
        resources. The number of jobs must not exceed the batch size
        limit. SMILES structures are not checked for duplicates against
        existing jobs in the batch, so care must be taken to avoid
        adding the same molecule multiple times.

        Args:
            id (str): The `id` of the `Batch` resource to update.
            smiles (List[str]): List of SMILES structures to add as new
                `Job` resources in the batch.

        Returns:
            Batch: The updated `Batch` resource.
        """
        body: Dict[str, Any] = {"smiles": smiles}
        r: Response = self._requestor.put(f"/retro/v2/batches/{id}", json=body)
        if r.status_code == 200:
            return cast(Batch, r.json())
        elif r.status_code == 400:
            error: str = r.json().get("error", {}).get("message", "Unknown error.")
            raise ValueError(f"Invalid request: {error}")
        elif r.status_code == 402:  # FIXME
            pass
        elif r.status_code == 404:
            raise NotFoundError(id, "Batch")
        elif r.status_code == 413:
            raise ValueError("Number of SMILES exceeds batch limit.")
        raise UnexpectedResponseError("PUT", "update_batch")

    def delete(self, id: str) -> DeleteObject:
        """Delete a `Batch` resource by its `id`. The batch will stop
        being processed if it is still queued and any results will be
        removed if they exist. The customer metered usage is updated to
        reflect any incomplete jobs. All attached `Job` resources are
        also deleted.

        Note that the operation is **non-reversible** and all resources
        are no longer accessible after deletion.

        Args:
            id (str): The `id` of the `Batch` resource to delete.

        Returns:
            DeleteObject: Deletion confirmation.
        """
        r: Response = self._requestor.delete(f"/retro/v2/batches/{id}")
        if r.status_code == 200:
            return cast(DeleteObject, r.json())
        elif r.status_code == 402:  # FIXME
            pass
        elif r.status_code in [404, 422]:
            raise NotFoundError(id, "Batch")
        raise UnexpectedResponseError("DELETE", "delete_batch")
