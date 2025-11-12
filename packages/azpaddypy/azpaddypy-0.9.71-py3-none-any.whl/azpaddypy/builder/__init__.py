"""
Azure configuration and builder patterns.

This module provides sophisticated builder patterns for orchestrating Azure services
with comprehensive configuration management and environment detection.
"""

from .configuration import (
    AzureConfiguration,
    # Builder pattern classes
    AzureManagementBuilder,
    AzureManagementConfiguration,
    AzureResourceBuilder,
    AzureResourceConfiguration,
    # Configuration setup classes
    ConfigurationSetupBuilder,
    EnvironmentConfiguration,
)
from .directors import (
    AzureManagementDirector,
    AzureResourceDirector,
    # Director pattern classes
    ConfigurationSetupDirector,
)

__all__ = [
    "AzureConfiguration",
    # Builder pattern classes
    "AzureManagementBuilder",
    "AzureManagementConfiguration",
    "AzureManagementDirector",
    "AzureResourceBuilder",
    "AzureResourceConfiguration",
    "AzureResourceDirector",
    # Configuration setup classes
    "ConfigurationSetupBuilder",
    # Director pattern classes
    "ConfigurationSetupDirector",
    "EnvironmentConfiguration",
]
