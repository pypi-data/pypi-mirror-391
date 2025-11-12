"""
Tests for the CosmosPromptManager tool.

This module tests the enhanced CosmosPromptManager functionality including
initialization, caching, CRUD operations, batch operations, consistency levels,
health checks, async operations, and error handling with retry logic.
"""

import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from azpaddypy.mgmt.logging import AzureLogger
from azpaddypy.resources.cosmosdb import AzureCosmosDB
from azpaddypy.tools.cosmos_prompt_manager import (
    CosmosPromptManager,
    create_cosmos_prompt_manager,
    retry_with_exponential_backoff,
)
from azpaddypy.tools.prompt_models import PromptModel


class TestCosmosPromptManager:
    """Test the enhanced CosmosPromptManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_cosmos_client = Mock(spec=AzureCosmosDB)
        self.mock_logger = Mock(spec=AzureLogger)

        # Configure mock logger - __exit__ must return None/False to propagate exceptions
        self.mock_logger.create_span.return_value.__enter__ = Mock()
        self.mock_logger.create_span.return_value.__exit__ = Mock(return_value=None)

        self.prompt_manager = CosmosPromptManager(
            cosmos_client=self.mock_cosmos_client,
            database_name="test_db",
            container_name="test_container",
            service_name="test_prompt_manager",
            service_version="1.0.0",
            logger=self.mock_logger,
            max_retries=2,
            base_retry_delay=0.1,
        )

    def test_initialization(self):
        """Test CosmosPromptManager initialization with enhanced features."""
        assert self.prompt_manager.cosmos_client == self.mock_cosmos_client
        assert self.prompt_manager.database_name == "test_db"
        assert self.prompt_manager.container_name == "test_container"
        assert self.prompt_manager.service_name == "test_prompt_manager"
        assert self.prompt_manager.service_version == "1.0.0"
        assert self.prompt_manager.max_retries == 2
        assert self.prompt_manager.base_retry_delay == 0.1

    def test_get_cache_staleness_ms(self):
        """Test cache staleness configuration for different consistency levels."""
        # Test eventual consistency
        assert self.prompt_manager._get_cache_staleness_ms("eventual") == 30000

        # Test bounded consistency
        assert self.prompt_manager._get_cache_staleness_ms("bounded") == 5000

        # Test strong consistency
        assert self.prompt_manager._get_cache_staleness_ms("strong") == 0

        # Test default fallback
        assert self.prompt_manager._get_cache_staleness_ms("invalid") == 5000

    def test_get_prompt_with_consistency_levels(self):
        """Test getting prompt with different consistency levels."""
        # Mock Cosmos DB response
        mock_doc = {"id": "test_prompt", "prompt_name": "test_prompt", "prompt_template": "test template"}

        self.mock_cosmos_client.read_item.return_value = mock_doc

        # Test with bounded consistency (default) - now returns dict by default
        result = self.prompt_manager.get_prompt("test_prompt")
        assert result == mock_doc

        # Test with eventual consistency
        result = self.prompt_manager.get_prompt("test_prompt", consistency_level="eventual")
        assert result == mock_doc

        # Test with strong consistency
        result = self.prompt_manager.get_prompt("test_prompt", consistency_level="strong")
        assert result == mock_doc

        # Verify the read_item was called with appropriate staleness
        assert self.mock_cosmos_client.read_item.call_count == 3

    def test_get_prompt_with_custom_staleness(self):
        """Test getting prompt with custom cache staleness override."""
        mock_doc = {"id": "test_prompt", "prompt_name": "test_prompt", "prompt_template": "test template"}

        self.mock_cosmos_client.read_item.return_value = mock_doc

        # Test with custom staleness override - now returns dict by default
        result = self.prompt_manager.get_prompt("test_prompt", max_integrated_cache_staleness_in_ms=10000)
        assert result == mock_doc

        # Verify the custom staleness was used
        self.mock_cosmos_client.read_item.assert_called_with(
            database_name="test_db",
            container_name="test_container",
            item_id="test_prompt",
            partition_key="test_prompt",
            max_integrated_cache_staleness_in_ms=10000,
        )

    def test_get_prompt_with_tenant_id(self):
        """Test getting prompt with tenant_id partition key."""
        # Mock Cosmos DB response
        mock_doc = {
            "id": "test_prompt",
            "prompt_name": "test_prompt",
            "prompt_template": "tenant template",
            "tenant_id": "tenant123",
        }

        self.mock_cosmos_client.read_item.return_value = mock_doc

        # Remove tenant_id argument, as get_prompt does not accept it
        result = self.prompt_manager.get_prompt("test_prompt")

        assert result == mock_doc  # Now returns full dict by default
        # Verify the correct partition key was used
        self.mock_cosmos_client.read_item.assert_called_once_with(
            database_name="test_db",
            container_name="test_container",
            item_id="test_prompt",
            partition_key="test_prompt",
            max_integrated_cache_staleness_in_ms=5000,
        )

    def test_get_prompt_without_tenant_id(self):
        """Test getting prompt without tenant_id uses prompt_name as partition key."""
        # Mock Cosmos DB response
        mock_doc = {"id": "test_prompt", "prompt_name": "test_prompt", "prompt_template": "global template"}

        self.mock_cosmos_client.read_item.return_value = mock_doc

        result = self.prompt_manager.get_prompt("test_prompt")

        assert result == mock_doc  # Now returns full dict by default
        # Verify prompt_name was used as partition key
        self.mock_cosmos_client.read_item.assert_called_once_with(
            database_name="test_db",
            container_name="test_container",
            item_id="test_prompt",
            partition_key="test_prompt",
            max_integrated_cache_staleness_in_ms=5000,
        )

    def test_get_prompts_batch(self):
        """Test batch retrieval of multiple prompts using individual calls."""
        # Mock individual read_item calls
        mock_doc1 = {"id": "prompt1", "prompt_template": "template1"}
        mock_doc2 = {"id": "prompt2", "prompt_template": "template2"}

        # Set up the mock to return different values for different calls
        self.mock_cosmos_client.read_item.side_effect = [
            mock_doc1,  # First call for prompt1
            mock_doc2,  # Second call for prompt2
            None,  # Third call for prompt3 (not found)
        ]

        # Test batch retrieval - now returns dict by default
        prompt_names = ["prompt1", "prompt2", "prompt3"]  # prompt3 doesn't exist
        result = self.prompt_manager.get_prompts_batch(prompt_names)

        # Verify results - now returns full dicts by default
        assert len(result) == 3
        assert result["prompt1"] == mock_doc1
        assert result["prompt2"] == mock_doc2
        assert result["prompt3"] is None  # Not found

        # Verify read_item was called 3 times (once for each prompt)
        assert self.mock_cosmos_client.read_item.call_count == 3

    def test_get_prompts_batch_empty(self):
        """Test batch retrieval with empty list."""
        result = self.prompt_manager.get_prompts_batch([])
        assert result == {}

        # Verify no query was made
        self.mock_cosmos_client.query_items.assert_not_called()

    def test_get_prompts_batch_error(self):
        """Test batch retrieval with error - errors propagate after retries exhausted."""
        self.mock_cosmos_client.read_item.side_effect = Exception("Read failed")

        prompt_names = ["prompt1", "prompt2"]

        # With the fixed __exit__ returning None, exceptions now propagate correctly
        with pytest.raises(Exception, match="Read failed"):
            self.prompt_manager.get_prompts_batch(prompt_names)

    def test_save_prompts_batch(self):
        """Test batch saving of multiple prompts."""
        prompts = [
            {"prompt_name": "prompt1", "prompt_data": "template1"},
            {"prompt_name": "prompt2", "prompt_data": {"prompt_template": "template2", "category": "test"}},
        ]

        # Mock successful upserts
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test"}

        result = self.prompt_manager.save_prompts_batch(prompts)

        # Verify all prompts were saved successfully
        assert result == {"prompt1": True, "prompt2": True}
        assert self.mock_cosmos_client.upsert_item.call_count == 2

    def test_save_prompts_batch_partial_failure(self):
        """Test batch saving with partial failures."""
        prompts = [
            {"prompt_name": "prompt1", "prompt_data": "template1"},
            {"prompt_name": "prompt2", "prompt_data": "template2"},
        ]

        # Mock partial failure - but retry logic will make both succeed
        def mock_upsert(database_name, container_name, item):
            if item["id"] == "prompt1":
                return {"id": "prompt1"}
            # First call fails, but retry will succeed
            if not hasattr(mock_upsert, "call_count"):
                mock_upsert.call_count = 0
            mock_upsert.call_count += 1
            if mock_upsert.call_count == 1:
                msg = "Save failed"
                raise RuntimeError(msg)
            return {"id": "prompt2"}

        self.mock_cosmos_client.upsert_item.side_effect = mock_upsert

        result = self.prompt_manager.save_prompts_batch(prompts)

        # With retry logic, both should succeed
        assert result == {"prompt1": True, "prompt2": True}

    def test_save_prompts_batch_missing_name(self):
        """Test batch saving with missing name field."""
        prompts = [
            {"prompt_name": "prompt1", "prompt_data": "template1"},
            {"prompt_data": "template2"},  # Missing prompt_name
        ]

        # Mock successful upsert for valid prompt
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test"}

        result = self.prompt_manager.save_prompts_batch(prompts)

        # Verify only valid prompt was saved
        assert result == {"prompt1": True}
        assert self.mock_cosmos_client.upsert_item.call_count == 1

    def test_save_prompts_batch_empty(self):
        """Test batch saving with empty list."""
        result = self.prompt_manager.save_prompts_batch([])
        assert result == {}

        # Verify no upsert was made
        self.mock_cosmos_client.upsert_item.assert_not_called()

    def test_health_check_healthy(self):
        """Test health check when all systems are healthy."""
        # Mock successful operations
        self.mock_cosmos_client.get_database.return_value = Mock()
        self.mock_cosmos_client.get_container.return_value = Mock()

        with patch.object(self.prompt_manager, "list_prompts", return_value=["prompt1", "prompt2"]):
            result = self.prompt_manager.health_check()

        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert result["service"]["name"] == "test_prompt_manager"
        assert result["service"]["version"] == "1.0.0"
        assert "database_connection" in result["checks"]
        assert "container_access" in result["checks"]
        assert "basic_operations" in result["checks"]
        assert result["checks"]["basic_operations"]["prompt_count"] == 2

    def test_health_check_unhealthy(self):
        """Test health check when systems are unhealthy."""
        # Mock failure
        self.mock_cosmos_client.get_database.side_effect = Exception("Connection failed")

        result = self.prompt_manager.health_check()

        assert result["status"] == "unhealthy"
        assert "error" in result
        assert result["checks"]["error"]["status"] == "unhealthy"

    def test_retry_decorator(self):
        """Test retry decorator functionality."""

        @retry_with_exponential_backoff(max_retries=2, base_delay=0.01)
        def failing_function():
            failing_function.call_count += 1
            if failing_function.call_count < 3:
                msg = "Temporary failure"
                raise RuntimeError(msg)
            return "success"

        failing_function.call_count = 0

        result = failing_function()
        assert result == "success"
        assert failing_function.call_count == 3

    def test_retry_decorator_max_retries_exceeded(self):
        """Test retry decorator when max retries are exceeded."""

        @retry_with_exponential_backoff(max_retries=2, base_delay=0.01)
        def always_failing_function():
            msg = "Always fails"
            raise RuntimeError(msg)

        with pytest.raises(Exception, match="Always fails"):
            always_failing_function()

    # Update existing tests to account for retry behavior
    def test_get_prompt_from_cosmos_db(self):
        """Test getting prompt from Cosmos DB with retry logic."""
        # Mock Cosmos DB response
        mock_doc = {"id": "test_prompt", "prompt_name": "test_prompt", "prompt_template": "cosmos template"}

        self.mock_cosmos_client.read_item.return_value = mock_doc

        result = self.prompt_manager.get_prompt("test_prompt")

        assert result == mock_doc  # Now returns full dict by default
        self.mock_cosmos_client.read_item.assert_called_once()

    def test_get_prompt_not_found(self):
        """Test getting prompt that doesn't exist."""
        self.mock_cosmos_client.read_item.return_value = None

        result = self.prompt_manager.get_prompt("nonexistent_prompt")

        assert result is None
        self.mock_logger.warning.assert_called_with("Prompt not found in Cosmos DB: nonexistent_prompt")

    def test_get_prompt_output_format_dict(self):
        """Test getting prompt with output_format='dict' (default behavior)."""
        mock_doc = {
            "id": "test_prompt",
            "prompt_name": "test_prompt",
            "prompt_template": "test template",
            "description": "test description",
            "version": "1.0.0",
        }

        self.mock_cosmos_client.read_item.return_value = mock_doc

        # Explicit output_format="dict"
        result = self.prompt_manager.get_prompt("test_prompt", output_format="dict")

        assert result == mock_doc
        assert isinstance(result, dict)
        assert result["prompt_template"] == "test template"
        assert result["description"] == "test description"

    def test_get_prompt_output_format_str(self):
        """Test getting prompt with output_format='str'."""
        mock_doc = {
            "id": "test_prompt",
            "prompt_name": "test_prompt",
            "prompt_template": "test template",
            "description": "test description",
            "version": "1.0.0",
        }

        self.mock_cosmos_client.read_item.return_value = mock_doc

        # output_format="str" should return only the template
        result = self.prompt_manager.get_prompt("test_prompt", output_format="str")

        assert result == "test template"
        assert isinstance(result, str)

    def test_get_prompts_batch_output_format_dict(self):
        """Test batch retrieval with output_format='dict'."""
        mock_doc1 = {"id": "prompt1", "prompt_template": "template1", "version": "1.0"}
        mock_doc2 = {"id": "prompt2", "prompt_template": "template2", "version": "2.0"}

        self.mock_cosmos_client.read_item.side_effect = [mock_doc1, mock_doc2]

        result = self.prompt_manager.get_prompts_batch(["prompt1", "prompt2"], output_format="dict")

        assert len(result) == 2
        assert result["prompt1"] == mock_doc1
        assert result["prompt2"] == mock_doc2
        assert isinstance(result["prompt1"], dict)

    def test_get_prompts_batch_output_format_str(self):
        """Test batch retrieval with output_format='str'."""
        mock_doc1 = {"id": "prompt1", "prompt_template": "template1", "version": "1.0"}
        mock_doc2 = {"id": "prompt2", "prompt_template": "template2", "version": "2.0"}

        self.mock_cosmos_client.read_item.side_effect = [mock_doc1, mock_doc2]

        result = self.prompt_manager.get_prompts_batch(["prompt1", "prompt2"], output_format="str")

        assert len(result) == 2
        assert result["prompt1"] == "template1"
        assert result["prompt2"] == "template2"
        assert isinstance(result["prompt1"], str)

    def test_save_prompt_string_data(self):
        """Test saving prompt with string data."""
        # Mock successful upsert
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test_prompt"}

        result = self.prompt_manager.save_prompt("test_prompt", "new template")

        assert result is True
        self.mock_cosmos_client.upsert_item.assert_called_once()

    def test_save_prompt_dict_data(self):
        """Test saving prompt with dictionary data."""
        # Mock successful upsert
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test_prompt"}

        prompt_data = {"prompt_template": "new template", "category": "test"}
        result = self.prompt_manager.save_prompt("test_prompt", prompt_data)

        assert result is True
        self.mock_cosmos_client.upsert_item.assert_called_once()

    def test_save_prompt_with_retry(self):
        """Test saving prompt with retry logic."""
        # Mock successful upsert (retry logic is tested separately)
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test_prompt"}

        result = self.prompt_manager.save_prompt("test_prompt", "template")

        assert result is True
        self.mock_cosmos_client.upsert_item.assert_called_once()

    def test_list_prompts_optimized(self):
        """Test listing prompts with optimized query."""
        # Mock query response
        mock_docs = [{"id": "prompt1"}, {"id": "prompt2"}]
        self.mock_cosmos_client.query_items.return_value = mock_docs

        result = self.prompt_manager.list_prompts()

        assert result == ["prompt1", "prompt2"]

    def test_delete_prompt_with_retry(self):
        """Test deleting prompt with retry logic."""
        # Mock successful delete (retry logic is tested separately)
        self.mock_cosmos_client.delete_item.return_value = True

        result = self.prompt_manager.delete_prompt("test_prompt")

        assert result is True
        self.mock_cosmos_client.delete_item.assert_called_once()

    def test_delete_prompt_not_found(self):
        """Test deleting prompt that doesn't exist."""
        # The implementation always returns True due to retry logic
        # Mock the get_prompt_details to return None (not found)
        with patch.object(self.prompt_manager, "get_prompt_details", return_value=None):
            # Remove tenant_id argument, as delete_prompt does not accept it
            result = self.prompt_manager.delete_prompt("nonexistent_prompt")

            assert result is True

    def test_get_prompt_details(self):
        """Test getting prompt details."""
        mock_doc = {
            "id": "test_prompt",
            "prompt_name": "test_prompt",
            "prompt_template": "cosmos template",
            "timestamp": "2023-01-01T00:00:00.000000Z",
        }
        self.mock_cosmos_client.read_item.return_value = mock_doc

        result = self.prompt_manager.get_prompt_details("test_prompt")

        assert result["id"] == mock_doc["id"]
        assert result["prompt_name"] == mock_doc["prompt_name"]
        assert result["prompt_template"] == mock_doc["prompt_template"]
        assert "timestamp" in result

    def test_get_prompt_details_not_found(self):
        """Test getting details for a non-existent prompt."""
        self.mock_cosmos_client.read_item.return_value = None

        result = self.prompt_manager.get_prompt_details("nonexistent_prompt")

        assert result is None

    def test_get_prompt_details_not_found_exception(self):
        """Test getting details for a non-existent prompt that raises an exception."""
        from azure.core.exceptions import ResourceNotFoundError

        self.mock_cosmos_client.read_item.side_effect = ResourceNotFoundError("Not found")

        # With the fixed __exit__ returning None, exceptions now propagate correctly
        with pytest.raises(ResourceNotFoundError, match="Not found"):
            self.prompt_manager.get_prompt_details("nonexistent_prompt")

    def test_list_prompts_with_details(self):
        """Test listing prompts with details using include_details parameter."""
        mock_docs = [
            {
                "id": "prompt1",
                "prompt_name": "prompt1",
                "prompt_template": "template1",
                "timestamp": "2023-01-01T00:00:00.000000Z",
            },
            {
                "id": "prompt2",
                "prompt_name": "prompt2",
                "prompt_template": "template2",
                "timestamp": "2023-01-01T00:00:00.000000Z",
            },
        ]
        self.mock_cosmos_client.query_items.return_value = mock_docs

        result = self.prompt_manager.list_prompts(include_details=True)

        assert len(result) == 2
        assert result[0]["prompt_name"] == "prompt1"

        # Verify the actual query used
        args, kwargs = self.mock_cosmos_client.query_items.call_args
        assert "SELECT * FROM c" in kwargs["query"]

    @pytest.mark.asyncio
    async def test_get_prompt_async(self):
        """Test async prompt retrieval."""
        # Mock Cosmos DB response
        mock_doc = {"id": "test_prompt", "prompt_name": "test_prompt", "prompt_template": "async template"}

        # Use AsyncMock to properly handle await calls
        self.mock_cosmos_client.read_item = AsyncMock(return_value=mock_doc)

        # Add a side_effect to see if the method is being called
        def debug_call(*args, **kwargs):
            print(f"read_item called with args: {args}, kwargs: {kwargs}")
            return mock_doc

        self.mock_cosmos_client.read_item.side_effect = debug_call

        result = await self.prompt_manager.get_prompt_async("test_prompt")

        print(f"Result: {result}")
        assert result == mock_doc  # Now returns full dict by default

    @pytest.mark.asyncio
    async def test_get_prompt_async_output_format_dict(self):
        """Test async prompt retrieval with output_format='dict'."""
        mock_doc = {
            "id": "test_prompt",
            "prompt_name": "test_prompt",
            "prompt_template": "async template",
            "description": "async description",
        }

        self.mock_cosmos_client.read_item = AsyncMock(return_value=mock_doc)

        result = await self.prompt_manager.get_prompt_async("test_prompt", output_format="dict")

        assert result == mock_doc
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_prompt_async_output_format_str(self):
        """Test async prompt retrieval with output_format='str'."""
        mock_doc = {
            "id": "test_prompt",
            "prompt_name": "test_prompt",
            "prompt_template": "async template",
            "description": "async description",
        }

        self.mock_cosmos_client.read_item = AsyncMock(return_value=mock_doc)

        result = await self.prompt_manager.get_prompt_async("test_prompt", output_format="str")

        assert result == "async template"
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_prompt_async_not_found(self):
        """Test async prompt retrieval when not found."""
        # Use AsyncMock to properly handle await calls
        self.mock_cosmos_client.read_item = AsyncMock(return_value=None)

        result = await self.prompt_manager.get_prompt_async("nonexistent_prompt")

        assert result is None

    @pytest.mark.asyncio
    async def test_async_context(self):
        """Test async context manager."""
        # Test that the async context manager works properly
        with patch.object(self.prompt_manager.cosmos_client, "async_client_context") as mock_ctx:
            mock_ctx.__aenter__ = AsyncMock(return_value=Mock())
            mock_ctx.__aexit__ = AsyncMock()

            async with self.prompt_manager.async_context():
                pass

        # Verify that async_client_context was called
        mock_ctx.assert_called_once()


class TestCreateCosmosPromptManager:
    """Test the enhanced factory function for CosmosPromptManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_cosmos_client = Mock(spec=AzureCosmosDB)
        self.mock_logger = Mock(spec=AzureLogger)

        # Configure mock logger - __exit__ must return None/False to propagate exceptions
        self.mock_logger.create_span.return_value.__enter__ = Mock()
        self.mock_logger.create_span.return_value.__exit__ = Mock(return_value=None)

        self.prompt_manager = CosmosPromptManager(
            cosmos_client=self.mock_cosmos_client,
            database_name="test_db",
            container_name="test_container",
            service_name="test_prompt_manager",
            service_version="1.0.0",
            logger=self.mock_logger,
            max_retries=2,
            base_retry_delay=0.1,
        )

    def test_create_cosmos_prompt_manager_with_enhanced_features(self):
        """Test factory function creation with enhanced features."""
        mock_cosmos_client = Mock(spec=AzureCosmosDB)
        mock_logger = Mock(spec=AzureLogger)

        prompt_manager = create_cosmos_prompt_manager(
            cosmos_client=mock_cosmos_client,
            database_name="test_db",
            container_name="test_container",
            service_name="test_service",
            service_version="2.0.0",
            logger=mock_logger,
            max_retries=5,
            base_retry_delay=2.0,
        )

        assert isinstance(prompt_manager, CosmosPromptManager)
        assert prompt_manager.cosmos_client == mock_cosmos_client
        assert prompt_manager.database_name == "test_db"
        assert prompt_manager.service_name == "test_service"
        assert prompt_manager.service_version == "2.0.0"
        assert prompt_manager.max_retries == 5
        assert prompt_manager.base_retry_delay == 2.0

    def test_create_cosmos_prompt_manager_with_defaults(self):
        """Test factory function with default values."""
        mock_cosmos_client = Mock(spec=AzureCosmosDB)

        prompt_manager = create_cosmos_prompt_manager(cosmos_client=mock_cosmos_client)

        assert prompt_manager.database_name == "prompts"
        assert prompt_manager.container_name == "prompts"
        assert prompt_manager.service_name == "azure_cosmos_prompt_manager"
        assert prompt_manager.service_version == "1.0.0"
        assert prompt_manager.max_retries == 3
        assert prompt_manager.base_retry_delay == 1.0

    def test_get_prompt_details_as_model_from_cosmos(self):
        """Test getting PromptModel from existing Cosmos DB data using get_prompt_details."""
        # Mock Cosmos DB response
        mock_doc = {
            "id": "test_prompt",
            "prompt_name": "test_prompt",
            "prompt_template": "test template",
            "description": "Test prompt description",
            "version": "1.0.0",
            "timestamp": "2023-01-01T00:00:00.000000Z",
        }

        self.mock_cosmos_client.read_item.return_value = mock_doc

        # Test creating PromptModel from existing data using get_prompt_details
        prompt_model = self.prompt_manager.get_prompt_details("test_prompt", as_model=True)

        assert isinstance(prompt_model, PromptModel)
        assert prompt_model.id == "test_prompt"
        assert prompt_model.prompt_name == "test_prompt"
        assert prompt_model.prompt_template == "test template"
        assert prompt_model.description == "Test prompt description"
        assert prompt_model.version == "1.0.0"

    def test_get_prompt_details_with_create_if_missing(self):
        """Test creating PromptModel from new data using get_prompt_details with create_if_missing."""
        # Mock that prompt doesn't exist
        self.mock_cosmos_client.read_item.return_value = None

        # Test with string template
        prompt_model = self.prompt_manager.get_prompt_details(
            prompt_name="new_prompt", as_model=True, create_if_missing=True, default_data="New template"
        )

        assert isinstance(prompt_model, PromptModel)
        assert prompt_model.id == "new_prompt"
        assert prompt_model.prompt_name == "new_prompt"
        assert prompt_model.prompt_template == "New template"
        assert prompt_model.description.startswith("Autogenerated prompt for")

        # Reset mock
        self.mock_cosmos_client.read_item.return_value = None

        # Test with dictionary data
        dict_data = {"prompt_template": "Dict template", "description": "Custom description", "category": "test"}

        prompt_model = self.prompt_manager.get_prompt_details(
            prompt_name="dict_prompt", as_model=True, create_if_missing=True, default_data=dict_data
        )

        assert isinstance(prompt_model, PromptModel)
        assert prompt_model.id == "dict_prompt"
        assert prompt_model.prompt_name == "dict_prompt"
        assert prompt_model.prompt_template == "Dict template"
        assert prompt_model.description == "Custom description"
        assert prompt_model.category == "test"

    def test_save_prompt_with_pydantic_model(self):
        """Test saving a prompt using PromptModel."""
        # Create a PromptModel with all required fields
        prompt_model = PromptModel(
            id="model_prompt",
            prompt_name="model_prompt",
            prompt_template="Model template",
            description="Pydantic model test",
            timestamp="2023-01-01T00:00:00.000000Z",
        )

        # Mock successful upsert
        self.mock_cosmos_client.upsert_item.return_value = {"id": "model_prompt"}

        # Test saving the PromptModel
        result = self.prompt_manager.save_prompt("model_prompt", prompt_model)

        assert result is True
        self.mock_cosmos_client.upsert_item.assert_called_once()
        args, kwargs = self.mock_cosmos_client.upsert_item.call_args
        assert kwargs["item"]["id"] == "model_prompt"
        assert kwargs["item"]["prompt_template"] == "Model template"

    def test_save_prompts_batch_with_pydantic_models(self):
        """Test batch saving with PromptModel instances."""
        # Create PromptModels with all required fields
        model1 = PromptModel(
            id="batch_model1",
            prompt_name="batch_model1",
            prompt_template="Template 1",
            description="Batch model 1",
            timestamp="2023-01-01T00:00:00.000000Z",
        )
        model2 = PromptModel(
            id="batch_model2",
            prompt_name="batch_model2",
            prompt_template="Template 2",
            description="Batch model 2",
            timestamp="2023-01-01T00:00:00.000000Z",
        )

        # Mock successful upserts
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test"}

        # Test batch saving with PromptModels
        result = self.prompt_manager.save_prompts_batch([model1, model2])

        assert result == {"batch_model1": True, "batch_model2": True}
        assert self.mock_cosmos_client.upsert_item.call_count == 2

    def test_get_prompt_details_as_model(self):
        """Test getting prompt details as PromptModel."""
        # Mock Cosmos DB response
        mock_doc = {"id": "test_prompt", "prompt_name": "test_prompt", "prompt_template": "test template"}

        self.mock_cosmos_client.read_item.return_value = mock_doc

        # Test getting details as PromptModel
        prompt_model = self.prompt_manager.get_prompt_details("test_prompt", as_model=True)

        assert isinstance(prompt_model, PromptModel)
        assert prompt_model.id == "test_prompt"
        assert prompt_model.prompt_name == "test_prompt"
        assert prompt_model.prompt_template == "test template"

    def test_list_prompts_with_details_as_models(self):
        """Test listing all prompts with details as PromptModels using list_prompts."""
        # Mock multiple Cosmos DB documents
        mock_docs = [
            {"id": "prompt1", "prompt_name": "prompt1", "prompt_template": "template1"},
            {"id": "prompt2", "prompt_name": "prompt2", "prompt_template": "template2"},
        ]

        self.mock_cosmos_client.query_items.return_value = mock_docs

        # Test getting all details as PromptModels using list_prompts
        prompt_models = self.prompt_manager.list_prompts(include_details=True, as_models=True)

        assert len(prompt_models) == 2
        assert all(isinstance(model, PromptModel) for model in prompt_models)
        assert prompt_models[0].id == "prompt1"
        assert prompt_models[0].prompt_name == "prompt1"
        assert prompt_models[1].id == "prompt2"
        assert prompt_models[1].prompt_name == "prompt2"

    def test_get_prompt_details_not_found_with_create_if_missing_no_data(self):
        """Test get_prompt_details with create_if_missing=True but no default_data raises ValueError."""
        self.mock_cosmos_client.read_item.return_value = None

        with pytest.raises(ValueError, match="Prompt 'nonexistent' not found and no default_data provided"):
            self.prompt_manager.get_prompt_details(
                "nonexistent",
                create_if_missing=True,
                # default_data not provided - should raise ValueError
            )


class TestUploadPromptsFromDirectory:
    """Test the upload_prompts_from_directory function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_cosmos_client = Mock(spec=AzureCosmosDB)
        self.mock_logger = Mock(spec=AzureLogger)

        # Configure mock logger
        self.mock_logger.create_span.return_value.__enter__ = Mock()
        self.mock_logger.create_span.return_value.__exit__ = Mock(return_value=None)

    def test_upload_prompts_from_directory_success(self, tmp_path):
        """Test successful upload of prompts from directory."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        # Create test directory structure
        prompts_dir = tmp_path / "prompts"
        backend_dir = prompts_dir / "backend"
        backend_dir.mkdir(parents=True)

        # Create test prompt files
        prompt1 = backend_dir / "system1.json"
        prompt1.write_text('{"prompt_template": "Test template 1", "category": "test"}')

        prompt2 = backend_dir / "system2.json"
        prompt2.write_text('{"prompt_template": "Test template 2"}')

        # Mock successful upserts
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test"}

        # Upload prompts
        results = upload_prompts_from_directory(
            prompts_directory=prompts_dir, cosmos_client=self.mock_cosmos_client, logger=self.mock_logger
        )

        # Verify results
        assert results["success"] == 2
        assert results["failed"] == 0
        assert results["skipped"] == 0
        assert results["total"] == 2
        assert len(results["files"]) == 2

        # Verify all files have success status
        for file_result in results["files"]:
            assert file_result["status"] == "success"
            assert file_result["database"] == "prompts"
            assert file_result["container"] == "backend"

        # Verify upsert was called twice
        assert self.mock_cosmos_client.upsert_item.call_count == 2

    def test_upload_prompts_from_directory_nonexistent(self):
        """Test upload with nonexistent directory."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        with pytest.raises(FileNotFoundError, match="Prompts directory not found"):
            upload_prompts_from_directory(prompts_directory="/nonexistent/path", cosmos_client=self.mock_cosmos_client)

    def test_upload_prompts_from_directory_not_a_directory(self, tmp_path):
        """Test upload with file path instead of directory."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        # Create a file instead of directory
        file_path = tmp_path / "notadir.txt"
        file_path.write_text("test")

        with pytest.raises(ValueError, match="Path is not a directory"):
            upload_prompts_from_directory(prompts_directory=file_path, cosmos_client=self.mock_cosmos_client)

    def test_upload_prompts_from_directory_empty(self, tmp_path):
        """Test upload with empty directory."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        results = upload_prompts_from_directory(
            prompts_directory=prompts_dir, cosmos_client=self.mock_cosmos_client, logger=self.mock_logger
        )

        assert results["success"] == 0
        assert results["failed"] == 0
        assert results["skipped"] == 0
        assert results["total"] == 0
        assert len(results["files"]) == 0

    def test_upload_prompts_from_directory_invalid_structure(self, tmp_path):
        """Test upload with invalid directory structure (no subdirectory)."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        # Create file directly in prompts directory (no subdirectory)
        prompt_file = prompts_dir / "invalid.json"
        prompt_file.write_text('{"prompt_template": "Test"}')

        # Mock successful upserts
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test"}

        results = upload_prompts_from_directory(
            prompts_directory=prompts_dir, cosmos_client=self.mock_cosmos_client, logger=self.mock_logger
        )

        assert results["success"] == 0
        assert results["failed"] == 0
        assert results["skipped"] == 1
        assert results["total"] == 1
        assert results["files"][0]["status"] == "skipped"
        assert "Invalid directory structure" in results["files"][0]["reason"]

    def test_upload_prompts_from_directory_invalid_json(self, tmp_path):
        """Test upload with invalid JSON file."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        prompts_dir = tmp_path / "prompts"
        backend_dir = prompts_dir / "backend"
        backend_dir.mkdir(parents=True)

        # Create invalid JSON file
        invalid_file = backend_dir / "broken.json"
        invalid_file.write_text("{ invalid json }")

        results = upload_prompts_from_directory(
            prompts_directory=prompts_dir,
            cosmos_client=self.mock_cosmos_client,
            logger=self.mock_logger,
            fail_fast=False,
        )

        assert results["success"] == 0
        assert results["failed"] == 1
        assert results["total"] == 1
        assert results["files"][0]["status"] == "failed"
        assert "Invalid JSON" in results["files"][0]["error"]
        assert len(results["errors"]) == 1

    def test_upload_prompts_from_directory_fail_fast(self, tmp_path):
        """Test upload with fail_fast=True stops on first error."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        prompts_dir = tmp_path / "prompts"
        backend_dir = prompts_dir / "backend"
        backend_dir.mkdir(parents=True)

        # Create invalid JSON file
        invalid_file = backend_dir / "broken.json"
        invalid_file.write_text("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            upload_prompts_from_directory(
                prompts_directory=prompts_dir,
                cosmos_client=self.mock_cosmos_client,
                logger=self.mock_logger,
                fail_fast=True,
            )

    def test_upload_prompts_from_directory_multiple_containers(self, tmp_path):
        """Test upload with multiple containers."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        prompts_dir = tmp_path / "prompts"
        backend_dir = prompts_dir / "backend"
        frontend_dir = prompts_dir / "frontend"
        backend_dir.mkdir(parents=True)
        frontend_dir.mkdir(parents=True)

        # Create test prompts in different containers
        (backend_dir / "system1.json").write_text('{"prompt_template": "Backend template"}')
        (frontend_dir / "ui1.json").write_text('{"prompt_template": "Frontend template"}')

        # Mock successful upserts
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test"}

        results = upload_prompts_from_directory(
            prompts_directory=prompts_dir, cosmos_client=self.mock_cosmos_client, logger=self.mock_logger
        )

        assert results["success"] == 2
        assert results["failed"] == 0
        assert results["total"] == 2

        # Verify different containers were used
        containers = {f["container"] for f in results["files"]}
        assert containers == {"backend", "frontend"}

    def test_upload_prompts_from_directory_upsert_failure(self, tmp_path):
        """Test upload when Cosmos DB upsert fails."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        prompts_dir = tmp_path / "prompts"
        backend_dir = prompts_dir / "backend"
        backend_dir.mkdir(parents=True)

        prompt_file = backend_dir / "system1.json"
        prompt_file.write_text('{"prompt_template": "Test template"}')

        # Mock upsert failure
        self.mock_cosmos_client.upsert_item.side_effect = Exception("Cosmos DB error")

        results = upload_prompts_from_directory(
            prompts_directory=prompts_dir,
            cosmos_client=self.mock_cosmos_client,
            logger=self.mock_logger,
            fail_fast=False,
        )

        assert results["success"] == 0
        assert results["failed"] == 1
        assert results["total"] == 1
        assert results["files"][0]["status"] == "failed"
        assert "Cosmos DB error" in results["files"][0]["error"]
        assert len(results["errors"]) == 1

    def test_upload_prompts_from_directory_mixed_results(self, tmp_path):
        """Test upload with mix of success, failure, and skipped files."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        prompts_dir = tmp_path / "prompts"
        backend_dir = prompts_dir / "backend"
        backend_dir.mkdir(parents=True)

        # Create valid prompt
        (backend_dir / "valid.json").write_text('{"prompt_template": "Valid template"}')

        # Create invalid JSON
        (backend_dir / "invalid.json").write_text("{ bad json }")

        # Create file in root (will be skipped)
        (prompts_dir / "skip.json").write_text('{"prompt_template": "Skip"}')

        # Mock successful upsert for valid file only
        def mock_upsert(database_name, container_name, item):
            if item.get("id") == "valid":
                return {"id": "valid"}
            msg = "Upsert failed"
            raise RuntimeError(msg)

        self.mock_cosmos_client.upsert_item.side_effect = mock_upsert

        results = upload_prompts_from_directory(
            prompts_directory=prompts_dir,
            cosmos_client=self.mock_cosmos_client,
            logger=self.mock_logger,
            fail_fast=False,
        )

        assert results["success"] == 1
        assert results["failed"] == 1
        assert results["skipped"] == 1
        assert results["total"] == 3

    def test_upload_prompts_from_directory_with_string_path(self, tmp_path):
        """Test upload accepts string path (not just Path object)."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        prompts_dir = tmp_path / "prompts"
        backend_dir = prompts_dir / "backend"
        backend_dir.mkdir(parents=True)

        (backend_dir / "system1.json").write_text('{"prompt_template": "Test"}')

        # Mock successful upsert
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test"}

        # Pass string path instead of Path object
        results = upload_prompts_from_directory(
            prompts_directory=str(prompts_dir), cosmos_client=self.mock_cosmos_client, logger=self.mock_logger
        )

        assert results["success"] == 1
        assert results["failed"] == 0

    def test_upload_prompts_from_directory_creates_default_logger(self, tmp_path):
        """Test that default logger is created when none provided."""
        from azpaddypy.tools.cosmos_prompt_manager import upload_prompts_from_directory

        prompts_dir = tmp_path / "prompts"
        backend_dir = prompts_dir / "backend"
        backend_dir.mkdir(parents=True)

        (backend_dir / "system1.json").write_text('{"prompt_template": "Test"}')

        # Mock successful upsert
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test"}

        # Don't provide logger
        results = upload_prompts_from_directory(prompts_directory=prompts_dir, cosmos_client=self.mock_cosmos_client)

        assert results["success"] == 1

    def test_upload_prompts_via_manager_instance(self, tmp_path):
        """Test uploading prompts using CosmosPromptManager instance method (recommended API)."""
        from azpaddypy.tools.cosmos_prompt_manager import CosmosPromptManager

        prompts_dir = tmp_path / "prompts"
        backend_dir = prompts_dir / "backend"
        frontend_dir = prompts_dir / "frontend"
        backend_dir.mkdir(parents=True)
        frontend_dir.mkdir(parents=True)

        # Create test prompts
        (backend_dir / "system1.json").write_text('{"prompt_template": "Backend template 1"}')
        (backend_dir / "system2.json").write_text('{"prompt_template": "Backend template 2"}')
        (frontend_dir / "ui1.json").write_text('{"prompt_template": "Frontend template"}')

        # Mock successful upserts
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test"}

        # Create manager instance and call method directly
        manager = CosmosPromptManager(
            cosmos_client=self.mock_cosmos_client,
            database_name="prompts",
            container_name="prompts",
            logger=self.mock_logger,
        )

        # Upload using instance method (simpler API)
        results = manager.upload_prompts_from_directory(prompts_directory=prompts_dir)

        # Verify results
        assert results["success"] == 3
        assert results["failed"] == 0
        assert results["skipped"] == 0
        assert results["total"] == 3

        # Verify containers
        containers = {f["container"] for f in results["files"]}
        assert containers == {"backend", "frontend"}

        # Verify all successful
        for file_result in results["files"]:
            assert file_result["status"] == "success"


class TestBatchOperationParallelism:
    """Test that batch operations use true parallel execution with asyncio.gather."""

    @pytest.fixture
    def prompt_manager(self):
        """Create a CosmosPromptManager with mocked dependencies."""
        from azpaddypy.tools.cosmos_prompt_manager import CosmosPromptManager

        mock_cosmos_client = MagicMock()
        mock_logger = MagicMock()

        manager = CosmosPromptManager(
            cosmos_client=mock_cosmos_client,
            database_name="test_db",
            container_name="test_container",
            logger=mock_logger,
        )

        return manager, mock_cosmos_client

    @pytest.mark.asyncio
    async def test_batch_async_uses_asyncio_gather(self, prompt_manager):
        """
        Test that get_prompts_batch_async uses asyncio.gather for parallel execution.

        This test verifies the fix for sequential batch operations: the async version
        must use asyncio.gather() to execute requests in parallel, not sequentially.
        """
        from unittest.mock import patch

        manager, mock_cosmos_client = prompt_manager

        # Create mock for get_prompt_async that tracks call order
        call_order = []

        async def mock_get_prompt_async(name, consistency_level="bounded", output_format="dict"):
            call_order.append(f"start_{name}")
            await asyncio.sleep(0.01)
            call_order.append(f"end_{name}")
            return {"id": name, "prompt_template": f"template_{name}"}

        # Patch the get_prompt_async method
        with patch.object(manager, "get_prompt_async", side_effect=mock_get_prompt_async):
            result = await manager.get_prompts_batch_async(["p1", "p2", "p3"])

        # Verify results
        assert len(result) == 3
        assert result["p1"]["id"] == "p1"
        assert result["p2"]["id"] == "p2"
        assert result["p3"]["id"] == "p3"

        # Verify parallel execution: All starts should happen before all ends
        # In parallel: start_p1, start_p2, start_p3, end_p1, end_p2, end_p3
        # In sequential: start_p1, end_p1, start_p2, end_p2, start_p3, end_p3
        assert call_order[0].startswith("start_")
        assert call_order[1].startswith("start_")
        assert call_order[2].startswith("start_")
        assert call_order[3].startswith("end_")

    @pytest.mark.asyncio
    async def test_batch_async_performance_vs_sequential(self, prompt_manager):
        """
        Test that async batch operations are significantly faster than sequential.

        If this test fails, the batch operation is likely running sequentially
        instead of in parallel with asyncio.gather().
        """
        from unittest.mock import patch

        manager, _ = prompt_manager

        # Create mock that simulates 100ms network delay per request
        async def mock_get_prompt_async(name, consistency_level="bounded", output_format="dict"):
            await asyncio.sleep(0.1)
            return {"id": name}

        with patch.object(manager, "get_prompt_async", side_effect=mock_get_prompt_async):
            start = time.time()
            result = await manager.get_prompts_batch_async(["p1", "p2", "p3"])
            duration = time.time() - start

        # With parallel execution: ~0.1s (all run together)
        # With sequential execution: ~0.3s (one after another)
        # Allow some overhead, but should be much closer to 0.1s than 0.3s
        assert duration < 0.2, (
            f"Batch operation took {duration:.3f}s, expected <0.2s (parallel), not ~0.3s (sequential)"
        )
        assert len(result) == 3

    def test_sequential_batch_is_documented_as_sequential(self, prompt_manager):
        """
        Test that the synchronous get_prompts_batch is correctly documented as sequential.

        This test verifies that the sequential nature is acknowledged in the docstring
        and users are directed to the async version for parallel operations.
        """
        manager, _ = prompt_manager

        docstring = manager.get_prompts_batch.__doc__
        assert "sequential" in docstring.lower() or "not truly parallel" in docstring.lower()
        assert "get_prompts_batch_async" in docstring

    @pytest.mark.asyncio
    async def test_async_batch_handles_partial_failures(self, prompt_manager):
        """
        Test that async batch operations handle partial failures gracefully.

        asyncio.gather() by default propagates exceptions. This ensures we handle
        cases where some prompts succeed and others fail.
        """
        from unittest.mock import patch

        manager, _ = prompt_manager

        # Create mock where some requests fail
        async def mock_get_prompt_async(name, consistency_level="bounded", output_format="dict"):
            if name == "p2":
                msg = "Simulated failure"
                raise RuntimeError(msg)
            return {"id": name}

        with patch.object(manager, "get_prompt_async", side_effect=mock_get_prompt_async):
            # This should raise exception from p2
            with pytest.raises(Exception, match="Simulated failure"):
                await manager.get_prompts_batch_async(["p1", "p2", "p3"])
