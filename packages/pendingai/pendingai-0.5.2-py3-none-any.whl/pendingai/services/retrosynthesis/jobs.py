#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from requests import Response

from pendingai.api_resources.interfaces import (
    CreateResourceInterface,
    DeleteResourceInterface,
    ListResourceInterface,
    RetrieveResourceInterface,
)
from pendingai.api_resources.object import DeleteObject, ListObject, Object
from pendingai.api_resources.parser import cast
from pendingai.exceptions import NotFoundError, UnexpectedResponseError


class Job(Object):
    """
    Job object.
    """

    class Parameters(Object):
        """
        Job object parameters.
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
        ai_disclaimer: str
        """
        AI-generated content disclaimer.
        """

    class Route(Object):
        """
        Job object synthetic routes.
        """

        class Step(Object):
            """
            Job object synthetic route steps.
            """

            reaction_smiles: str
            """
            Single-step reaction SMILES.
            """
            order: int
            """
            Post-order position of the synthetic route step.
            """

        summary: str
        """
        SMILES representation of a synthetic route.
        """
        building_blocks: list[dict]
        """
        Building blocks used in the synthetic route.
        """
        steps: list[dict]  # FIXME: Requires object namespace validation.
        """
        Single-step reaction stages of the synthetic route.
        """

    id: str
    """Resource id."""
    object: str = "job"
    """Resource object type."""
    query: str
    """Query SMILES structure being processed."""
    status: str
    """Most recent job status."""
    parameters: dict  # FIXME: Requires object namespace validation.
    """Job parameters."""
    created: datetime
    """Timestamp for when the job was created."""
    updated: datetime
    """Timestamp for when the job was last updated."""
    routes: list[dict]  # FIXME: Requires object namespace validation.
    """Collection of found synthetic routes."""


class JobInterface(
    ListResourceInterface[Job],
    CreateResourceInterface[Job],
    RetrieveResourceInterface[Job],
    DeleteResourceInterface[Job],
):
    """Jobs resource interface."""

    def list(
        self,
        page: int = 1,
        after: Optional[str] = None,
        before: Optional[str] = None,
        limit: int = 10,
    ) -> ListObject[Job]:
        """List `Job` resources. Resources are sorted in reverse
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
            ListObject[Job]: List of `Job` resources.
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
        r: Response = self._requestor.get(
            "/retro/v2/jobs", params=params, headers={"accept-encoding": "gzip"}
        )
        if r.status_code == 200:
            return cast(ListObject[Job], r.json())
        elif r.status_code == 400:
            error: str = r.json().get("error", {}).get("message", "Unknown error.")
            raise ValueError(f"Invalid request: {error}")
        raise UnexpectedResponseError("GET", "list_job")

    def create(
        self,
        smiles: str,
        retrosynthesis_engine: Optional[str] = None,
        building_block_libraries: Optional[List[str]] = None,
        number_of_routes: int = 1,
        processing_time: int = 60,
        reaction_limit: int = 10,
        building_block_limit: int = 10,
    ) -> Job:
        """Create a `Job` resource to perform retrosynthesis on a
        target molecule defined by its SMILES structure. The
        retrosynthesis process is performed asynchronously and the
        status can be polled.

        Args:
            smiles (str): SMILES structure of the target molecule.
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
            Job: The created `Job` resource.
        """
        # Validation of the job request parameters to ensure they fall
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
            "query": smiles,
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

        # Make the request to create the Job resource and capture the
        # 400 and 402 responses to parse any relevant error content.
        r: Response = self._requestor.post(
            "/retro/v2/jobs", json=body, headers={"accept-encoding": "gzip"}
        )
        if r.status_code == 200:
            return cast(Job, r.json())
        elif r.status_code == 400:
            error: str = r.json().get("error", {}).get("message", "Unknown error.")
            raise ValueError(f"Invalid request: {error}")
        elif r.status_code == 402:  # FIXME
            pass
        raise UnexpectedResponseError("POST", "create_job")

    def retrieve(self, id: str) -> Job:
        """Retrieve a `Job` resource by its `id`. The job contains its
        current status and, if available, the results of the job.

        Args:
            id (str): The `id` of the `Job` resource to retrieve.

        Returns:
            Job: The requested `Job` resource.
        """
        r: Response = self._requestor.get(
            f"/retro/v2/jobs/{id}", headers={"accept-encoding": "gzip"}
        )
        if r.status_code == 200:
            return cast(Job, r.json())
        elif r.status_code in [404, 422]:
            raise NotFoundError(id, "Job")
        raise UnexpectedResponseError("GET", "retrieve_job")

    def delete(self, id: str) -> DeleteObject:
        """Delete a `Job` resource by its `id`. The job will no longer
        be processed if it is still queued and any results will be
        removed if they exist. The customer metered usage is updated to
        reflect an incomplete job.

        Note that the operation is **non-reversible** and all resources
        are no longer accessible after deletion.

        Args:
            id (str): The `id` of the `Job` resource to delete.

        Returns:
            DeleteObject: Deletion confirmation.
        """
        r: Response = self._requestor.delete(f"/retro/v2/jobs/{id}")
        if r.status_code == 200:
            return cast(DeleteObject, r.json())
        elif r.status_code == 402:  # FIXME
            pass
        elif r.status_code == 409:  # FIXME
            raise ValueError(f"Job {id} cannot be deleted while processing.")
        elif r.status_code in [404, 422]:
            raise NotFoundError(id, "Job")
        raise UnexpectedResponseError("DELETE", "delete_job")
