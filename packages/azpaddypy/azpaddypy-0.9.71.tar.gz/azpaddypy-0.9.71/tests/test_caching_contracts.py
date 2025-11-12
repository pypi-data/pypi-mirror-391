"""
Caching behavior contract tests.

These tests verify that factory caching works correctly across all resource types.
These tests would have caught the id() caching bug before it reached production.

Critical behaviors tested:
1. Cache based on configuration, not object identity
2. Cache includes all relevant configuration parameters
3. Cache distinguishes different resources
4. Cache provides performance benefits
"""

from unittest.mock import MagicMock, patch

import pytest

pytestmark = [pytest.mark.contract, pytest.mark.caching, pytest.mark.unit]

from _test_utils import (
    assert_cache_hit,
    assert_cache_miss,
    create_mock_credential,
    get_test_keyvault_url,
    get_test_storage_url,
)

from azpaddypy.resources.keyvault import create_azure_keyvault
from azpaddypy.resources.storage import create_azure_storage


class TestStorageCachingContracts:
    """Test storage factory caching contracts."""

    @patch("azpaddypy.resources.storage.BlobServiceClient")
    def test_cache_survives_credential_object_changes(self, mock_blob_client):
        """
        CRITICAL: Cache should be configuration-based, not object-identity based.

        This test would have FAILED with the old id()-based caching bug.
        Different credential objects with same config should hit cache.
        """
        mock_blob_client.return_value = MagicMock()

        url = get_test_storage_url()
        cred1 = create_mock_credential()
        cred2 = create_mock_credential()

        # Verify credentials are different objects
        assert cred1 is not cred2

        storage1 = create_azure_storage(account_url=url, credential=cred1, service_name="test_service")

        storage2 = create_azure_storage(account_url=url, credential=cred2, service_name="test_service")

        # Cache should hit despite different credential objects
        assert_cache_hit(storage1, storage2, "Cache must be config-based, not credential-object-based (id() bug)")

    @patch("azpaddypy.resources.storage.BlobServiceClient")
    def test_cache_key_includes_account_url(self, mock_blob_client):
        """Cache must distinguish different storage account URLs."""
        mock_blob_client.return_value = MagicMock()
        cred = create_mock_credential()

        storage1 = create_azure_storage(
            account_url=get_test_storage_url("account1"), credential=cred, service_name="test"
        )

        storage2 = create_azure_storage(
            account_url=get_test_storage_url("account2"), credential=cred, service_name="test"
        )

        assert_cache_miss(storage1, storage2, "Different URLs must create different instances")

    @patch("azpaddypy.resources.storage.BlobServiceClient")
    def test_cache_key_includes_service_name(self, mock_blob_client):
        """Cache must distinguish different service names."""
        mock_blob_client.return_value = MagicMock()
        cred = create_mock_credential()
        url = get_test_storage_url()

        storage1 = create_azure_storage(account_url=url, credential=cred, service_name="service1")

        storage2 = create_azure_storage(account_url=url, credential=cred, service_name="service2")

        assert_cache_miss(storage1, storage2, "Different service names must create different instances")

    @patch("azpaddypy.resources.storage.BlobServiceClient")
    def test_cache_key_includes_feature_flags(self, mock_blob_client):
        """Cache must distinguish different feature flag combinations."""
        mock_blob_client.return_value = MagicMock()
        cred = create_mock_credential()
        url = get_test_storage_url()

        storage1 = create_azure_storage(
            account_url=url, credential=cred, service_name="test", enable_blob_storage=True, enable_file_storage=False
        )

        storage2 = create_azure_storage(
            account_url=url, credential=cred, service_name="test", enable_blob_storage=True, enable_file_storage=True
        )

        assert_cache_miss(storage1, storage2, "Different feature flags must create different instances")

    @patch("azpaddypy.resources.storage.BlobServiceClient")
    def test_cache_provides_shared_state(self, mock_blob_client):
        """
        Cached instances should share state.

        This is a behavioral test: if caching works, instances share state.
        """
        mock_blob_client.return_value = MagicMock()
        cred = create_mock_credential()
        url = get_test_storage_url()

        storage1 = create_azure_storage(account_url=url, credential=cred, service_name="test")

        storage2 = create_azure_storage(account_url=url, credential=cred, service_name="test")

        # Modify state on one instance
        storage1.test_property = "test_value"

        # Should be visible on the other (same object)
        assert hasattr(storage2, "test_property")
        assert storage2.test_property == "test_value"

    @patch("azpaddypy.resources.storage.BlobServiceClient")
    def test_multiple_cache_hits_return_same_instance(self, mock_blob_client):
        """Multiple calls with same config should all return the same instance."""
        mock_blob_client.return_value = MagicMock()
        cred = create_mock_credential()
        url = get_test_storage_url()

        instances = [create_azure_storage(account_url=url, credential=cred, service_name="test") for _ in range(10)]

        # All should be the same object
        first_instance = instances[0]
        assert all(instance is first_instance for instance in instances)


class TestKeyVaultCachingContracts:
    """Test KeyVault factory caching contracts."""

    @patch("azpaddypy.resources.keyvault.SecretClient")
    def test_cache_survives_credential_object_changes(self, mock_secret_client):
        """
        CRITICAL: Cache should be configuration-based, not object-identity based.

        This test would have FAILED with the old id()-based caching bug.
        """
        mock_secret_client.return_value = MagicMock()

        url = get_test_keyvault_url()
        cred1 = create_mock_credential()
        cred2 = create_mock_credential()

        assert cred1 is not cred2

        kv1 = create_azure_keyvault(vault_url=url, credential=cred1, service_name="test")

        kv2 = create_azure_keyvault(vault_url=url, credential=cred2, service_name="test")

        assert_cache_hit(kv1, kv2, "KeyVault cache must be config-based, not credential-object-based")

    @patch("azpaddypy.resources.keyvault.SecretClient")
    def test_cache_key_includes_vault_url(self, mock_secret_client):
        """Cache must distinguish different vault URLs."""
        mock_secret_client.return_value = MagicMock()
        cred = create_mock_credential()

        kv1 = create_azure_keyvault(vault_url=get_test_keyvault_url("vault1"), credential=cred, service_name="test")

        kv2 = create_azure_keyvault(vault_url=get_test_keyvault_url("vault2"), credential=cred, service_name="test")

        assert_cache_miss(kv1, kv2, "Different vault URLs must create different instances")

    @patch("azpaddypy.resources.keyvault.SecretClient")
    def test_cache_key_includes_enabled_features(self, mock_secret_client):
        """Cache must distinguish different enabled features."""
        mock_secret_client.return_value = MagicMock()
        cred = create_mock_credential()
        url = get_test_keyvault_url()

        kv1 = create_azure_keyvault(
            vault_url=url, credential=cred, service_name="test", enable_secrets=True, enable_keys=False
        )

        kv2 = create_azure_keyvault(
            vault_url=url, credential=cred, service_name="test", enable_secrets=True, enable_keys=True
        )

        assert_cache_miss(kv1, kv2, "Different feature configurations must create different instances")


class TestCachingEdgeCases:
    """Test edge cases and corner scenarios for caching."""

    @patch("azpaddypy.resources.storage.BlobServiceClient")
    def test_cache_handles_none_vs_empty_string(self, mock_blob_client):
        """Cache should distinguish None from empty string."""
        mock_blob_client.return_value = MagicMock()
        cred = create_mock_credential()
        url = get_test_storage_url()

        storage1 = create_azure_storage(account_url=url, credential=cred, service_name="test", connection_string=None)

        storage2 = create_azure_storage(account_url=url, credential=cred, service_name="test", connection_string="")

        # These should be different instances (None != "")
        assert_cache_miss(storage1, storage2, "None vs empty string should create different instances")

    @patch("azpaddypy.resources.storage.BlobServiceClient")
    def test_cache_is_case_sensitive_for_urls(self, mock_blob_client):
        """Cache keys should be case-sensitive for URLs."""
        mock_blob_client.return_value = MagicMock()
        cred = create_mock_credential()

        storage1 = create_azure_storage(
            account_url="https://TestAccount.blob.core.windows.net", credential=cred, service_name="test"
        )

        storage2 = create_azure_storage(
            account_url="https://testaccount.blob.core.windows.net", credential=cred, service_name="test"
        )

        # Different case = different instances
        assert_cache_miss(storage1, storage2, "URLs should be case-sensitive in cache keys")
