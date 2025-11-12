"""OpenSearch health check utilities.

This module provides functions to verify OpenSearch cluster connectivity and
availability by performing ping operations and returning diagnostic information.
Useful for health check endpoints and monitoring OpenSearch cluster status.
"""

from .client import OpenSearchClient

__all__ = ("is_opensearch_connected",)


def is_opensearch_connected(
    client: OpenSearchClient,
) -> tuple[bool, Exception | None]:
    """Check if OpenSearch cluster connection is functional by sending a ping command.

    Attempts to ping the OpenSearch cluster to verify connectivity and cluster availability.
    Returns both a boolean status and any exception encountered during the check,
    making it useful for health check endpoints and monitoring dashboards.

    Args:
        client: OpenSearchClient instance to test connectivity for. The client should be
            properly configured with valid cluster endpoints and authentication parameters.

    Returns:
        Tuple[bool, Optional[Exception]]: A tuple containing:
            - bool: True if ping successful and OpenSearch cluster is reachable, False otherwise.
            - Optional[Exception]: The exception object if connection failed (for
              debugging/logging purposes), None if successful.

    Example:
        >>> from dtpyfw.opensearch import OpenSearchConfig, OpenSearchClient
        >>> config = OpenSearchConfig().set_url("https://localhost:9200")
        >>> client = OpenSearchClient(config)
        >>> is_connected, error = is_opensearch_connected(client)
        >>> if is_connected:
        ...     print("OpenSearch cluster is healthy")
        ... else:
        ...     print(f"OpenSearch connection failed: {error}")

    Note:
        This function uses the OpenSearchClient's built-in health check capability.
        The ping operation is lightweight and checks basic cluster connectivity.
        For comprehensive health monitoring, consider checking cluster status endpoints
        using client.get_cluster_info().
    """
    try:
        # Use the client's built-in health check method
        is_healthy = client.is_healthy()
        return is_healthy, None
    except Exception as e:
        return False, e
