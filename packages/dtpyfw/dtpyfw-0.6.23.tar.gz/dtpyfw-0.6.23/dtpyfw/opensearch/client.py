"""OpenSearch client module.

This module provides a client wrapper for OpenSearch connections with
configuration management, connection testing, and health monitoring.
"""

from typing import Any

from opensearchpy import OpenSearch, RequestsHttpConnection

from ..core.exception import exception_to_dict
from ..log import footprint
from .config import OpenSearchConfig


class OpenSearchClient:
    """OpenSearch client wrapper with configuration-based initialization.

    Provides a managed OpenSearch client with automatic connection testing,
    health monitoring, and comprehensive configuration support including
    authentication, SSL, and cluster management.

    Example:
        >>> from dtpyfw.opensearch import OpenSearchConfig, OpenSearchClient
        >>> config = (
        ...     OpenSearchConfig()
        ...     .set_url("https://localhost:9200")
        ...     .set_username("admin")
        ...     .set_password("admin")
        ...     .set_verify_certs(False)
        ... )
        >>> client = OpenSearchClient(config)
        >>> info = client.get_cluster_info()
    """

    def __init__(self, config: OpenSearchConfig) -> None:
        """Initialize OpenSearch client with provided configuration.

        Args:
            config: OpenSearchConfig instance containing connection parameters,
                authentication, SSL settings, and other client options.

        Raises:
            ConnectionError: If OpenSearch connection cannot be established.
            ValueError: If required configuration parameters are missing.

        Example:
            >>> config = OpenSearchConfig().set_url("https://localhost:9200")
            >>> client = OpenSearchClient(config)
        """
        self.config = config
        self._client: OpenSearch | None = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize OpenSearch client from configuration."""
        controller = f"{__name__}.OpenSearchClient._initialize_client"

        try:
            # Get configuration values using the builder pattern
            hosts = self.config.get("hosts")
            url = self.config.get("url")
            username = self.config.get("username")
            password = self.config.get("password")
            use_ssl = self.config.get("use_ssl", True)
            verify_certs = self.config.get("verify_certs", True)
            timeout = self.config.get("timeout", 30)
            max_retries = self.config.get("max_retries", 3)
            retry_on_timeout = self.config.get("retry_on_timeout", True)
            ca_certs = self.config.get("ca_certs")
            client_cert = self.config.get("client_cert")
            client_key = self.config.get("client_key")

            # Determine hosts configuration
            if hosts:
                # Use multiple hosts if provided
                opensearch_hosts = hosts
            elif url:
                # Use single URL if provided
                opensearch_hosts = [url]
            else:
                raise ValueError(
                    "Either 'hosts' or 'url' must be provided in configuration"
                )

            # Configure authentication
            auth = None
            if username and password:
                auth = (username, password)

            # Create client configuration
            client_config = {
                "hosts": opensearch_hosts,
                "connection_class": RequestsHttpConnection,
                "use_ssl": use_ssl,
                "verify_certs": verify_certs,
                "timeout": timeout,
                "max_retries": max_retries,
                "retry_on_timeout": retry_on_timeout,
            }

            # Add authentication if configured
            if auth:
                client_config["http_auth"] = auth

            # Add SSL certificate configuration if provided
            if ca_certs:
                client_config["ca_certs"] = ca_certs

            if client_cert and client_key:
                client_config["client_cert"] = client_cert
                client_config["client_key"] = client_key

            # Create and test client
            self._client = OpenSearch(**client_config)

            # Test connection
            self._test_connection()

            footprint.leave(
                log_type="info",
                controller=controller,
                subject="Open Search Client initialized",
                message=f"OpenSearch client initialized successfully: {opensearch_hosts}",
                payload={"hosts": opensearch_hosts, "use_ssl": use_ssl},
            )

        except Exception as e:
            footprint.leave(
                log_type="error",
                controller=controller,
                subject="Open Search Client initialization failed",
                message=f"Failed to initialize OpenSearch client: {str(e)}",
                payload={"error": exception_to_dict(e)},
            )
            raise ConnectionError(f"OpenSearch connection failed: {str(e)}") from e

    def _test_connection(self) -> None:
        """Test OpenSearch connection by pinging the cluster.

        Verifies that the OpenSearch client can successfully communicate
        with the cluster by sending a ping request.

        Raises:
            ConnectionError: If ping fails, cluster is unreachable, or
                client is not properly initialized.
        """
        if self._client is None:
            raise ConnectionError("OpenSearch client not initialized")

        try:
            if not self._client.ping():
                raise ConnectionError("OpenSearch cluster ping failed")
        except Exception as e:
            raise ConnectionError(f"OpenSearch connection test failed: {str(e)}") from e

    def get_client(self) -> OpenSearch:
        """Get the underlying OpenSearch client instance.

        Returns:
            OpenSearch: The configured opensearch-py client instance ready for use.

        Raises:
            ConnectionError: If client is not initialized or connection failed.

        Example:
            >>> client = OpenSearchClient(config)
            >>> opensearch = client.get_client()
            >>> result = opensearch.search(index="my-index", body={"query": {"match_all": {}}})
        """
        if self._client is None:
            raise ConnectionError("OpenSearch client not initialized")
        return self._client

    def is_healthy(self) -> bool:
        """Check if OpenSearch connection is healthy.

        Performs a ping operation to verify that the OpenSearch cluster
        is reachable and responding to requests.

        Returns:
            bool: True if connection is healthy and cluster responds to ping,
                False if connection is down or cluster is unreachable.

        Example:
            >>> client = OpenSearchClient(config)
            >>> if client.is_healthy():
            ...     print("OpenSearch cluster is responding")
            ... else:
            ...     print("OpenSearch cluster is unreachable")
        """
        try:
            if self._client is None:
                return False
            return bool(self._client.ping())
        except Exception:
            return False

    def get_cluster_info(self) -> dict[str, Any]:
        """Get OpenSearch cluster information and status.

        Retrieves comprehensive information about the OpenSearch cluster
        including version, name, and cluster UUID.

        Returns:
            dict[str, Any]: Dictionary containing cluster information with keys
                such as 'name', 'cluster_name', 'cluster_uuid', 'version', etc.

        Raises:
            ConnectionError: If unable to retrieve cluster info due to
                connection issues or cluster unavailability.

        Example:
            >>> client = OpenSearchClient(config)
            >>> info = client.get_cluster_info()
            >>> print(f"Cluster: {info['cluster_name']}")
            >>> print(f"Version: {info['version']['number']}")
        """
        try:
            client = self.get_client()
            info: dict[str, Any] = client.info()
            return info
        except Exception as e:
            raise ConnectionError(f"Failed to retrieve cluster info: {str(e)}") from e
