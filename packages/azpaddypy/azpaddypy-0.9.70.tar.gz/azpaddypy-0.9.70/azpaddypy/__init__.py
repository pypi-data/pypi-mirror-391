"""
AzPaddyPy - Azure configuration management with builder patterns.

A comprehensive Python package for Azure cloud services integration with
standardized configuration management, OpenTelemetry tracing, and builder patterns.

Key Features:
- Azure Identity management with token caching
- Azure Key Vault integration for secrets management
- Azure Storage operations (blob, file, queue)
- Comprehensive logging with Application Insights
- Builder patterns for flexible service composition
- Environment detection and configuration management

Usage:
    # Direct imports (simplified)
    from azpaddypy import logger, identity, keyvault, storage_account

    # Builder pattern (recommended for complex scenarios)
    from azpaddypy.builder import AzureManagementBuilder, AzureResourceBuilder
    from azpaddypy.builder.directors import ConfigurationSetupDirector
"""

from .builder import (
    AzureConfiguration,
    AzureManagementBuilder,
    AzureManagementConfiguration,
    AzureManagementDirector,
    AzureResourceBuilder,
    AzureResourceConfiguration,
    AzureResourceDirector,
    ConfigurationSetupBuilder,
    ConfigurationSetupDirector,
    EnvironmentConfiguration,
)
from .mgmt import (
    AzureIdentity,
    AzureLogger,
    LocalDevelopmentSettings,
    create_local_env_manager,
)
from .resources import (
    AzureKeyVault,
    AzureStorage,
    create_azure_keyvault,
    create_azure_storage,
)
from .tools import (
    ConfigurationManager,
    CosmosPromptManager,
    create_configuration_manager,
    create_cosmos_prompt_manager,
    upload_prompts_from_directory,
)

__all__ = [
    # Builder pattern classes
    "AzureConfiguration",
    # Management classes
    "AzureIdentity",
    # Resource classes
    "AzureKeyVault",
    "AzureLogger",
    "AzureManagementBuilder",
    "AzureManagementConfiguration",
    "AzureManagementDirector",
    "AzureResourceBuilder",
    "AzureResourceConfiguration",
    "AzureResourceDirector",
    "AzureStorage",
    # Tool classes
    "ConfigurationManager",
    "ConfigurationSetupBuilder",
    "ConfigurationSetupDirector",
    "CosmosPromptManager",
    "EnvironmentConfiguration",
    "LocalDevelopmentSettings",
    "create_azure_keyvault",
    "create_azure_storage",
    "create_configuration_manager",
    "create_cosmos_prompt_manager",
    "create_local_env_manager",
    "upload_prompts_from_directory",
]
