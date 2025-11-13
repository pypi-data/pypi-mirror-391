"""Utility functions for aixtools compliance."""

from fastmcp.server.dependencies import get_context

from aixtools.compliance.private_data import PrivateData
from aixtools.logging.logging_config import get_logger

logger = get_logger(__name__)


def mark_current_workspace_private() -> PrivateData:
    """
    Mark the current workspace as containing private data.

    This function automatically retrieves the FastMCP context from thread-local storage
    and marks the workspace as containing private data. This is idempotent - calling it
    multiple times is safe and will only set the flag once.
    """

    ctx = get_context()
    private_data = PrivateData(ctx)

    if not private_data.has_private_data:
        private_data.has_private_data = True
        logger.info("Marked workspace as containing CP Portal private data")
    else:
        logger.debug("Workspace already marked as containing private data")

    return private_data
