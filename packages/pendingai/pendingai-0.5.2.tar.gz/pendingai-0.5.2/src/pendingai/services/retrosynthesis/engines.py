#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from datetime import datetime
from typing import Any, Dict, Optional

from requests import Response

from pendingai.api_resources.interfaces import ListResourceInterface
from pendingai.api_resources.object import ListObject, Object
from pendingai.api_resources.parser import cast
from pendingai.exceptions import UnexpectedResponseError


class Engine(Object):
    """Engine object."""

    id: str
    """Resource id."""
    object: str = "engine"
    """Resource object type."""
    name: str
    """Engine name."""
    last_alive: datetime
    """Engine timestamp for last usage."""
    suspended: bool = False
    """Engine suspension status."""


class EngineInterface(ListResourceInterface[Engine]):
    """Engine resource interface."""

    def list(
        self,
        page: int = 1,
        after: Optional[str] = None,
        before: Optional[str] = None,
        limit: int = 25,
    ) -> ListObject[Engine]:
        """List `Engine` resources. Resources are sorted in reverse
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
            ListObject[Engine]: List of `Engine` resources.
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
        r: Response = self._requestor.get("/retro/v2/engines", params=params)
        if r.status_code == 200:
            return cast(ListObject[Engine], r.json())
        elif r.status_code == 400:
            error: str = r.json().get("error", {}).get("message", "Unknown error.")
            raise ValueError(f"Invalid request: {error}")
        raise UnexpectedResponseError("GET", "list_engine")
