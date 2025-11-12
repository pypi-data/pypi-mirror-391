"""OpenSearch integration utilities and client wrapper.

Provides OpenSearch client configuration, connection management,
and health monitoring capabilities for search and analytics workloads.
"""

from ..core.require_extra import require_extra

__all__ = (
    "OpenSearchConfig",
    "OpenSearchClient",
    "is_opensearch_connected",
)

require_extra("opensearch", "opensearch")

from .client import OpenSearchClient
from .config import OpenSearchConfig
from .health import is_opensearch_connected
