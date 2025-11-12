"""OpenSearch configuration builder module.

This module provides a fluent builder interface for constructing OpenSearch
connection configurations with support for URLs, authentication, SSL,
timeouts, and retry settings.
"""

from typing import Any

__all__ = ("OpenSearchConfig",)


class OpenSearchConfig:
    """Builder for constructing OpenSearch connection configuration.

    Provides a fluent interface for setting OpenSearch connection parameters
    including URLs, hosts, authentication, SSL, timeouts, and retry options.
    All setter methods return self for method chaining.

    Example:
        >>> config = OpenSearchConfig() \\
        ...     .set_hosts(["https://localhost:9200"]) \\
        ...     .set_username("admin") \\
        ...     .set_password("admin") \\
        ...     .set_verify_certs(False) \\
        ...     .set_timeout(60)
    """

    def __init__(self) -> None:
        """Initialize an empty OpenSearch configuration.

        Creates a new configuration builder with no preset values.
        """
        self._config_data: dict[str, Any] = {}

    def set_url(self, url: str) -> "OpenSearchConfig":
        """Set a single OpenSearch cluster URL.

        Args:
            url: Complete OpenSearch cluster URL including protocol and port
                (e.g., "https://localhost:9200", "http://opensearch.example.com:9200").

        Returns:
            OpenSearchConfig: Self for method chaining.

        Example:
            >>> config = OpenSearchConfig().set_url("https://localhost:9200")
        """
        self._config_data["url"] = url
        return self

    def set_hosts(self, hosts: list[str]) -> "OpenSearchConfig":
        """Set multiple OpenSearch cluster hosts/URLs.

        Args:
            hosts: List of OpenSearch cluster URLs or host strings. Can include
                protocol, port, and path (e.g., ["https://node1:9200", "https://node2:9200"]).

        Returns:
            OpenSearchConfig: Self for method chaining.

        Example:
            >>> config = OpenSearchConfig().set_hosts([
            ...     "https://node1.example.com:9200",
            ...     "https://node2.example.com:9200"
            ... ])
        """
        self._config_data["hosts"] = hosts
        return self

    def set_username(self, username: str) -> "OpenSearchConfig":
        """Set the OpenSearch authentication username.

        Args:
            username: The username for OpenSearch authentication (basic auth or
                security plugin authentication).

        Returns:
            OpenSearchConfig: Self for method chaining.

        Note:
            Typically used with set_password() for basic authentication.
        """
        self._config_data["username"] = username
        return self

    def set_password(self, password: str) -> "OpenSearchConfig":
        """Set the OpenSearch authentication password.

        Args:
            password: The password for OpenSearch authentication.

        Returns:
            OpenSearchConfig: Self for method chaining.

        Note:
            Should be used together with set_username() for complete authentication.
        """
        self._config_data["password"] = password
        return self

    def set_verify_certs(self, verify_certs: bool) -> "OpenSearchConfig":
        """Enable or disable SSL certificate verification.

        Args:
            verify_certs: True to verify SSL certificates (recommended for production),
                False to skip certificate verification (useful for development with
                self-signed certificates).

        Returns:
            OpenSearchConfig: Self for method chaining.

        Note:
            Disabling certificate verification reduces security. Only disable
            in development environments or with proper network security.
        """
        self._config_data["verify_certs"] = verify_certs
        return self

    def set_use_ssl(self, use_ssl: bool) -> "OpenSearchConfig":
        """Enable or disable SSL/TLS for OpenSearch connections.

        Args:
            use_ssl: True to use HTTPS connections, False for HTTP connections.

        Returns:
            OpenSearchConfig: Self for method chaining.

        Note:
            Production deployments should use SSL (HTTPS). HTTP should only
            be used in local development environments.
        """
        self._config_data["use_ssl"] = use_ssl
        return self

    def set_timeout(self, timeout: int) -> "OpenSearchConfig":
        """Set the request timeout in seconds.

        Args:
            timeout: Timeout in seconds for OpenSearch operations. Requests
                exceeding this time will raise a timeout error.

        Returns:
            OpenSearchConfig: Self for method chaining.

        Note:
            Default is typically 30 seconds. Increase for complex queries or
            large bulk operations that may take longer to complete.
        """
        self._config_data["timeout"] = timeout
        return self

    def set_max_retries(self, max_retries: int) -> "OpenSearchConfig":
        """Set the maximum number of retry attempts for failed requests.

        Args:
            max_retries: Maximum number of times to retry failed requests before
                giving up. Set to 0 to disable retries.

        Returns:
            OpenSearchConfig: Self for method chaining.

        Note:
            Retries help handle transient network issues and cluster failover.
            Too many retries may mask persistent problems.
        """
        self._config_data["max_retries"] = max_retries
        return self

    def set_retry_on_timeout(self, retry_on_timeout: bool) -> "OpenSearchConfig":
        """Enable or disable retries on timeout errors.

        Args:
            retry_on_timeout: True to retry requests that timeout, False to
                fail immediately on timeout.

        Returns:
            OpenSearchConfig: Self for method chaining.

        Note:
            Enabling timeout retries can help with temporary cluster overload
            but may increase total request time.
        """
        self._config_data["retry_on_timeout"] = retry_on_timeout
        return self

    def set_ca_certs(self, ca_certs: str) -> "OpenSearchConfig":
        """Set the path to CA certificate bundle for SSL verification.

        Args:
            ca_certs: Path to the CA certificate bundle file for verifying
                SSL certificates from the OpenSearch cluster.

        Returns:
            OpenSearchConfig: Self for method chaining.

        Note:
            Required when using custom CA certificates or self-signed certificates
            with certificate verification enabled.
        """
        self._config_data["ca_certs"] = ca_certs
        return self

    def set_client_cert(self, client_cert: str) -> "OpenSearchConfig":
        """Set the path to client certificate for mutual TLS authentication.

        Args:
            client_cert: Path to the client certificate file for mutual TLS
                authentication with the OpenSearch cluster.

        Returns:
            OpenSearchConfig: Self for method chaining.

        Note:
            Used for client certificate authentication. Must be paired with
            set_client_key() for complete mutual TLS setup.
        """
        self._config_data["client_cert"] = client_cert
        return self

    def set_client_key(self, client_key: str) -> "OpenSearchConfig":
        """Set the path to client private key for mutual TLS authentication.

        Args:
            client_key: Path to the client private key file for mutual TLS
                authentication with the OpenSearch cluster.

        Returns:
            OpenSearchConfig: Self for method chaining.

        Note:
            Used with set_client_cert() for client certificate authentication.
            Keep the private key file secure and properly protected.
        """
        self._config_data["client_key"] = client_key
        return self

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key.

        Args:
            key: The configuration parameter name to retrieve (e.g., "hosts",
                "username", "timeout", "verify_certs").
            default: The default value to return if the key is not found.

        Returns:
            Any: The configuration value if it exists, otherwise the default value.

        Example:
            >>> config = OpenSearchConfig().set_timeout(60)
            >>> timeout = config.get("timeout")  # Returns 60
            >>> retries = config.get("max_retries", 3)  # Returns 3 (default)
        """
        return self._config_data.get(key, default)
