"""
Shared utilities for Azure resource clients.

Provides common setup functions for credential and logger initialization
to reduce code duplication across resource classes (AzureStorage, AzureKeyVault, AzureCosmosDB).
"""

from azure.core.credentials import TokenCredential

from ..mgmt.identity import AzureIdentity
from ..mgmt.logging import AzureLogger


def setup_logger(
    logger: AzureLogger | None,
    service_name: str,
    service_version: str,
    connection_string: str | None,
) -> AzureLogger:
    """
    Setup logger with fallback to default creation.

    Args:
        logger: Optional existing AzureLogger instance
        service_name: Service name for tracing context
        service_version: Service version for metadata
        connection_string: Application Insights connection string

    Returns:
        AzureLogger instance (provided or newly created)

    """
    if logger is not None:
        return logger

    return AzureLogger(
        service_name=service_name,
        service_version=service_version,
        connection_string=connection_string,
        enable_console_logging=True,
    )


def setup_credential(
    credential: TokenCredential | None,
    azure_identity: AzureIdentity | None,
) -> tuple[TokenCredential, AzureIdentity | None]:
    """
    Setup credential from either credential or azure_identity parameter.

    Args:
        credential: Optional Azure credential for authentication
        azure_identity: Optional AzureIdentity instance for credential management

    Returns:
        Tuple of (credential, azure_identity)

    Raises:
        ValueError: If neither credential nor azure_identity is provided

    """
    if azure_identity is not None:
        return azure_identity.get_credential(), azure_identity
    if credential is not None:
        return credential, None
    msg = "Either 'credential' or 'azure_identity' must be provided"
    raise ValueError(msg)
