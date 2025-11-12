"""
Azure Cosmos DB Prompt Management Tool

This module provides a robust prompt management system using Azure Cosmos DB
for storing and retrieving prompts with real-time updates and optimized performance.

Features:
- Batch operations: implemented as sequential single operations (no true Cosmos batch)
- Configurable consistency levels (eventual, bounded, strong)
- Real-time updates across all instances
- Async support for high-throughput applications
- Retry logic with exponential backoff for resilience
- Comprehensive error handling and logging
- Backward compatibility with existing system
- Standardized azpaddypy logging and error handling

Best Practices:
- Use prompt_name as partition key for all operations
- For large-scale batch operations, consider Cosmos DB stored procedures for efficiency
"""

import asyncio
import inspect
import json
import time
from contextlib import asynccontextmanager
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Literal, TypeVar

from ..mgmt.logging import AzureLogger
from ..resources.cosmosdb import AzureCosmosDB
from .prompt_models import PromptModel

# Type variable for prompt models
PromptType = TypeVar("PromptType", bound=dict[str, Any])


def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_exceptions: tuple[type[BaseException], ...] | None = None,
):
    """
    Decorator for retry logic with exponential backoff.
    Supports both synchronous and asynchronous functions.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for the first retry
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        retry_exceptions: Tuple of exception types that should trigger a retry

    """

    def decorator(func):
        # Check if function is async
        is_async = inspect.iscoroutinefunction(func)
        exceptions_to_handle: tuple[type[BaseException], ...] = (
            retry_exceptions if retry_exceptions is not None else (Exception,)
        )

        if is_async:

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None

                for attempt in range(max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions_to_handle as e:
                        last_exception = e

                        if attempt == max_retries:
                            # Last attempt failed, raise the exception
                            break

                        # Calculate delay for next attempt
                        delay = min(base_delay * (exponential_base**attempt), max_delay)

                        # Log the retry attempt
                        if args and hasattr(args[0], "logger"):
                            args[0].logger.warning(
                                f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s",
                                extra={"error": str(e), "attempt": attempt + 1, "function": func.__name__},
                            )

                        await asyncio.sleep(delay)

                # All attempts failed
                raise last_exception

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions_to_handle as e:
                    last_exception = e

                    if attempt == max_retries:
                        # Last attempt failed, raise the exception
                        break

                    # Calculate delay for next attempt
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # Log the retry attempt
                    if args and hasattr(args[0], "logger"):
                        args[0].logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s",
                            extra={"error": str(e), "attempt": attempt + 1, "function": func.__name__},
                        )

                    time.sleep(delay)

            # All attempts failed
            raise last_exception

        return sync_wrapper

    return decorator


class CosmosPromptManager:
    """
    Azure Cosmos DB-based prompt management tool with optimized performance,
    batch operations, and configurable consistency levels.

    This tool follows the azpaddypy pattern for Azure resource management with
    proper logging, error handling, and configuration management. It leverages
    Cosmos DB's integrated cache for optimal performance without additional
    local caching layers.

    Features:
    - Optimized Cosmos DB integrated cache usage
    - Batch operations for multiple prompts
    - Configurable consistency levels (eventual, bounded, strong)
    - Async support for high-throughput scenarios
    - Retry logic with exponential backoff
    - Comprehensive error handling and logging
    """

    def __init__(
        self,
        cosmos_client: AzureCosmosDB,
        database_name: str = "prompts",
        container_name: str = "prompts",
        service_name: str = "azure_cosmos_prompt_manager",
        service_version: str = "1.0.0",
        logger: AzureLogger | None = None,
        max_retries: int = 3,
        base_retry_delay: float = 1.0,
    ):
        """
        Initialize CosmosPromptManager.

        Args:
            cosmos_client: AzureCosmosDB client instance
            database_name: Name of the Cosmos DB database
            container_name: Name of the Cosmos DB container
            service_name: Service name for logging
            service_version: Service version for logging
            logger: Optional AzureLogger instance
            max_retries: Maximum number of retry attempts for failed operations
            base_retry_delay: Base delay in seconds for retry logic

        """
        self.cosmos_client = cosmos_client
        self.database_name = database_name
        self.container_name = container_name
        self.service_name = service_name
        self.service_version = service_version
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay

        if logger:
            self.logger = logger
        else:
            self.logger = AzureLogger(
                service_name=service_name,
                service_version=service_version,
                enable_console_logging=True,
            )

        self.logger.info(
            f"Cosmos Prompt Manager initialized for service '{service_name}' v{service_version}",
            extra={
                "database_name": database_name,
                "container_name": container_name,
                "max_retries": max_retries,
                "base_retry_delay": base_retry_delay,
            },
        )

    def _create_prompt_document(
        self, prompt_name: str, prompt_data: str | dict[str, Any] | PromptModel
    ) -> dict[str, Any]:
        """
        Create Cosmos DB document from prompt data.

        Args:
            prompt_name: Name of the prompt
            prompt_data: Either a string template, dictionary with prompt data, or PromptModel instance

        Returns:
            Dictionary formatted for Cosmos DB storage

        """
        if isinstance(prompt_data, PromptModel):
            # If it's already a PromptModel, convert to dict
            return prompt_data.to_dict()
        if isinstance(prompt_data, dict):
            # prompt_data is already a dictionary, merge with context
            context = {
                "id": prompt_name,
                "prompt_name": prompt_name,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
            # Ensure prompt_template exists in dict data
            if "prompt_template" not in prompt_data:
                msg = "Dictionary must contain 'prompt_template' field"
                raise ValueError(msg)
            merged_data = {**prompt_data, **context}
        else:
            # prompt_data is a string or other type, treat as prompt_template
            merged_data = {
                "id": prompt_name,
                "prompt_name": prompt_name,
                "description": f"Autogenerated prompt for {prompt_name}",
                "version": "1.0.0",
                "prompt_template": prompt_data,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        return merged_data

    def _get_cache_staleness_ms(self, consistency_level: Literal["eventual", "bounded", "strong"]) -> int:
        """
        Get cache staleness in milliseconds based on consistency level.

        Args:
            consistency_level: The consistency level for the operation

        Returns:
            Cache staleness in milliseconds

        """
        staleness_config = {
            "eventual": 30000,  # 30 seconds for non-critical prompts
            "bounded": 5000,  # 5 seconds for normal prompts
            "strong": 0,  # 0 milliseconds for critical prompts (no cache)
        }
        return staleness_config.get(consistency_level, 5000)

    def get_prompt(
        self,
        prompt_name: str,
        consistency_level: Literal["eventual", "bounded", "strong"] = "bounded",
        max_integrated_cache_staleness_in_ms: int | None = None,
        output_format: Literal["dict", "str"] = "dict",
    ) -> dict[str, Any] | str | None:
        """
        Retrieve a prompt from Cosmos DB.

        Args:
            prompt_name: Name of the prompt
            consistency_level: Consistency level for the read operation
            max_integrated_cache_staleness_in_ms: Optional override for cache staleness
            output_format: Output format - "dict" returns full prompt document (default), "str" returns template only

        Returns:
            If output_format="dict": Full prompt document as dictionary if found, None otherwise
            If output_format="str": Prompt template string if found, None otherwise

        Notes:
            - Uses prompt_name as partition key
            - Default behavior (output_format="dict") returns the complete prompt document

        """

        @retry_with_exponential_backoff(max_retries=self.max_retries)
        def _get_with_retry():
            attributes = {
                "prompt_name": prompt_name,
                "consistency_level": consistency_level,
                "output_format": output_format,
            }

            with self.logger.create_span("CosmosPromptManager.get_prompt", attributes=attributes):
                # Determine cache staleness
                if max_integrated_cache_staleness_in_ms is None:
                    staleness_ms = self._get_cache_staleness_ms(consistency_level)
                else:
                    staleness_ms = max_integrated_cache_staleness_in_ms

                # Read from Cosmos DB with optimized cache settings
                doc = self.cosmos_client.read_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item_id=prompt_name,
                    partition_key=prompt_name,
                    max_integrated_cache_staleness_in_ms=staleness_ms,
                )

                # Check if document was found
                if doc is None:
                    self.logger.warning(f"Prompt not found in Cosmos DB: {prompt_name}")
                    return None

                # Return based on output_format
                if output_format == "str":
                    return doc.get("prompt_template", "")
                # output_format == "dict"
                return doc

        return _get_with_retry()

    def get_prompts_batch(
        self,
        prompt_names: list[str],
        consistency_level: Literal["eventual", "bounded", "strong"] = "bounded",
        output_format: Literal["dict", "str"] = "dict",
    ) -> dict[str, dict[str, Any] | str | None]:
        """
        Retrieve multiple prompts from Cosmos DB (synchronous, sequential).

        Args:
            prompt_names: List of prompt names to retrieve
            consistency_level: Consistency level for the read operations
            output_format: Output format - "dict" returns full prompt documents (default), "str" returns templates only

        Returns:
            Dictionary with prompt names as keys and prompts as values
            If output_format="dict": Values are full prompt documents
            If output_format="str": Values are prompt template strings

        Notes:
            - This performs sequential single gets (not truly parallel)
            - For parallel batch operations, use get_prompts_batch_async()
            - For large-scale batch with Cosmos optimizations, consider stored procedures

        """
        prompts = {}
        for name in prompt_names:
            prompts[name] = self.get_prompt(name, consistency_level, output_format=output_format)
        return prompts

    async def get_prompts_batch_async(
        self,
        prompt_names: list[str],
        consistency_level: Literal["eventual", "bounded", "strong"] = "bounded",
        output_format: Literal["dict", "str"] = "dict",
    ) -> dict[str, dict[str, Any] | str | None]:
        """
        Retrieve multiple prompts from Cosmos DB in parallel (asynchronous).

        This method uses asyncio.gather() to execute all prompt retrievals concurrently,
        providing significant performance improvements over sequential operations.

        Args:
            prompt_names: List of prompt names to retrieve
            consistency_level: Consistency level for the read operations
            output_format: Output format - "dict" returns full prompt documents (default), "str" returns templates only

        Returns:
            Dictionary with prompt names as keys and prompts as values
            If output_format="dict": Values are full prompt documents
            If output_format="str": Values are prompt template strings

        Notes:
            - Uses asyncio.gather() for true parallel execution
            - Performance scales with number of prompts (O(1) time vs O(n) for sequential)
            - Recommended for retrieving multiple prompts efficiently

        """
        # Create tasks for all prompt retrievals
        tasks = [self.get_prompt_async(name, consistency_level, output_format=output_format) for name in prompt_names]

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks)

        # Combine results into dictionary
        return dict(zip(prompt_names, results, strict=False))

    def save_prompt(self, prompt_name: str, prompt_data: str | dict[str, Any] | PromptModel) -> bool:
        """
        Save or update a prompt in Cosmos DB.

        Args:
            prompt_name: Name of the prompt
            prompt_data: Either a string template, dictionary with prompt data, or PromptModel instance

        Returns:
            True if successful, False otherwise

        Notes:
            - Uses prompt_name as partition key
            - Uses retry logic for resilience

        """
        # Validate and convert input to document format
        if isinstance(prompt_data, str):
            # String template - create basic document
            prompt_document = self._create_prompt_document(prompt_name, prompt_data)
        elif isinstance(prompt_data, dict):
            # Dictionary data - merge with context
            prompt_document = self._create_prompt_document(prompt_name, prompt_data)
        elif isinstance(prompt_data, PromptModel):
            # PromptModel instance - convert to document format
            if prompt_data.id != prompt_name:
                msg = "PromptModel id must match prompt_name"
                raise ValueError(msg)
            prompt_document = prompt_data.to_dict()
        else:
            msg = "prompt_data must be str, dict, or PromptModel"
            raise TypeError(msg)

        @retry_with_exponential_backoff(max_retries=self.max_retries)
        def _save_with_retry():
            attributes = {"prompt_name": prompt_name}

            with self.logger.create_span("CosmosPromptManager.save_prompt", attributes=attributes):
                self.cosmos_client.upsert_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item=prompt_document,
                )
            return True

        return _save_with_retry()

    def save_prompts_batch(self, prompts: list[dict[str, Any] | PromptModel]) -> dict[str, bool]:
        """
        Save or update multiple prompts in Cosmos DB.

        Args:
            prompts: List of dictionaries or PromptModel instances, each containing 'prompt_name' and 'prompt_data'

        Returns:
            Dictionary with prompt names as keys and success status as values

        Notes:
            - This is not a true Cosmos DB batch; it performs sequential single upserts
            - For large-scale batch, consider using stored procedures
            - Invalid prompts are skipped with a warning

        """
        results = {}
        for prompt in prompts:
            if isinstance(prompt, PromptModel):
                # If it's already a PromptModel, use its id as name
                prompt_name = prompt.id
                try:
                    results[prompt_name] = self.save_prompt(prompt_name, prompt)
                except Exception as e:  # noqa: BLE001
                    self.logger.warning(f"Failed to save PromptModel: {e}", extra={"prompt": prompt})
            elif isinstance(prompt, dict):
                # Dictionary format - extract name and data
                prompt_name = prompt.get("prompt_name")
                prompt_data = prompt.get("prompt_data")
                if prompt_name and prompt_data:
                    results[prompt_name] = self.save_prompt(prompt_name, prompt_data)
                else:
                    self.logger.warning("Invalid prompt format in batch, skipping.", extra={"prompt": prompt})
            else:
                self.logger.warning(f"Unsupported prompt type in batch: {type(prompt)}", extra={"prompt": prompt})
        return results

    def list_prompts(
        self, include_details: bool = False, as_models: bool = False
    ) -> list[str] | list[dict[str, Any]] | list[PromptModel]:
        """
        List all prompts from Cosmos DB.

        Args:
            include_details: If True, return full prompt details; if False, return only names
            as_models: If True and include_details=True, return PromptModel instances

        Returns:
            - If include_details=False: List of prompt names (strings)
            - If include_details=True and as_models=False: List of prompt dictionaries
            - If include_details=True and as_models=True: List of PromptModel instances

        Notes:
            - This replaces the old get_all_prompt_details() method
            - Returns only the prompt IDs when include_details=False

        """
        operation_name = "CosmosPromptManager.list_prompts"
        if include_details:
            operation_name = "CosmosPromptManager.list_prompts_with_details"

        with self.logger.create_span(operation_name):
            if include_details:
                # Return full details
                query = "SELECT * FROM c"
                items = self.cosmos_client.query_items(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    query=query,
                    parameters=[],
                    enable_cross_partition_query=True,
                )
                if as_models:
                    return [PromptModel.from_cosmos_doc(doc) for doc in items]
                return list(items)
            # Return only names
            query = "SELECT c.id FROM c"
            items = self.cosmos_client.query_items(
                database_name=self.database_name,
                container_name=self.container_name,
                query=query,
                parameters=[],
                enable_cross_partition_query=True,
            )
            return [item["id"] for item in items]

    def delete_prompt(self, prompt_name: str) -> bool:
        """
        Delete a prompt from Cosmos DB.

        Args:
            prompt_name: Name of the prompt to delete

        Returns:
            True if successful, False otherwise

        Notes:
            - Uses prompt_name as partition key
            - Uses retry logic for resilience

        """

        @retry_with_exponential_backoff(max_retries=self.max_retries)
        def _delete_with_retry():
            attributes = {"prompt_name": prompt_name}

            with self.logger.create_span("CosmosPromptManager.delete_prompt", attributes=attributes):
                self.cosmos_client.delete_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item_id=prompt_name,
                    partition_key=prompt_name,
                )
            return True

        return _delete_with_retry()

    def get_prompt_details(
        self,
        prompt_name: str,
        as_model: bool = False,
        create_if_missing: bool = False,
        default_data: str | dict[str, Any] | None = None,
    ) -> dict[str, Any] | PromptModel | None:
        """
        Get full details of a prompt from Cosmos DB.

        Args:
            prompt_name: Name of the prompt
            as_model: If True, return a PromptModel instance; if False, return raw dictionary
            create_if_missing: If True and prompt not found, create a new model from default_data
            default_data: Data to use when creating a new model (if create_if_missing=True)

        Returns:
            Dictionary or PromptModel with prompt details if found, otherwise None
            If create_if_missing=True and prompt not found, returns new model created from default_data

        Raises:
            ValueError: If create_if_missing=True but prompt not found and no default_data provided

        Notes:
            - Uses prompt_name as partition key
            - When create_if_missing=True, this replaces the old create_prompt_model() functionality

        """
        attributes = {"prompt_name": prompt_name}

        with self.logger.create_span("CosmosPromptManager.get_prompt_details", attributes=attributes):
            doc = self.cosmos_client.read_item(
                database_name=self.database_name,
                container_name=self.container_name,
                item_id=prompt_name,
                partition_key=prompt_name,
            )

            if doc:
                if as_model:
                    return PromptModel.from_cosmos_doc(doc)
                return doc

            # Handle create_if_missing case
            if create_if_missing:
                if default_data is None:
                    msg = f"Prompt '{prompt_name}' not found and no default_data provided"
                    raise ValueError(msg)

                # Create new model from default_data
                if isinstance(default_data, str):
                    new_model = PromptModel(
                        id=prompt_name,
                        prompt_name=prompt_name,
                        prompt_template=default_data,
                        description=f"Autogenerated prompt for {prompt_name}",
                        version="1.0.0",
                        timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    )
                elif isinstance(default_data, dict):
                    # Extract prompt_template (required)
                    prompt_template = default_data.get("prompt_template")
                    if not prompt_template:
                        msg = "default_data dict must contain 'prompt_template' field"
                        raise ValueError(msg)

                    # Extract all other fields as kwargs
                    kwargs = {
                        k: v for k, v in default_data.items() if k not in {"id", "prompt_name", "prompt_template"}
                    }

                    # Add defaults if not present
                    if "timestamp" not in kwargs:
                        kwargs["timestamp"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

                    new_model = PromptModel(
                        id=prompt_name, prompt_name=prompt_name, prompt_template=prompt_template, **kwargs
                    )
                else:
                    msg = "default_data must be str or dict"
                    raise TypeError(msg)

                if as_model:
                    return new_model
                return new_model.to_dict()

            return None

    def delete_prompts_batch(self, prompt_names: list[str]) -> dict[str, bool]:
        """
        Delete multiple prompts from Cosmos DB in a single batch.

        Args:
            prompt_names: List of prompt names to delete

        Returns:
            Dictionary with prompt names as keys and success status as values

        Notes:
            - This is not a true Cosmos DB batch; it performs sequential single deletes
            - For large-scale batch, consider using stored procedures

        """
        results = {}
        for prompt_name in prompt_names:
            results[prompt_name] = self.delete_prompt(prompt_name)
        return results

    def health_check(self) -> dict[str, Any]:
        """
        Perform health check on the prompt manager.

        Returns:
            Dictionary with health check results

        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": {"name": self.service_name, "version": self.service_version},
            "checks": {},
        }

        try:
            # Test database connection
            start_time = time.time()
            self.cosmos_client.get_database(self.database_name)
            connection_time = time.time() - start_time

            health_status["checks"]["database_connection"] = {
                "status": "healthy",
                "response_time_ms": int(connection_time * 1000),
            }

            # Test container access
            start_time = time.time()
            self.cosmos_client.get_container(self.database_name, self.container_name)
            container_time = time.time() - start_time

            health_status["checks"]["container_access"] = {
                "status": "healthy",
                "response_time_ms": int(container_time * 1000),
            }

            # Test basic operations
            start_time = time.time()
            prompts = self.list_prompts()
            list_time = time.time() - start_time

            health_status["checks"]["basic_operations"] = {
                "status": "healthy",
                "response_time_ms": int(list_time * 1000),
                "prompt_count": len(prompts),
            }

            self.logger.info("Health check completed successfully")

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            health_status["checks"]["error"] = {"status": "unhealthy", "error": str(e)}
            self.logger.exception("Health check failed")

        return health_status

    @asynccontextmanager
    async def async_context(self):
        """Asynchronous context manager for Cosmos DB client."""
        async with self.cosmos_client.async_client_context():
            yield self

    def upload_prompts_from_directory(
        self,
        prompts_directory: str | Path,
        fail_fast: bool = False,
    ) -> dict[str, Any]:
        """
        Upload prompt templates from directory structure to Cosmos DB.

        Directory structure automatically determines database and container names:
        - Root directory name becomes database name (e.g., "prompts")
        - Subdirectory name becomes container name (e.g., "backend")
        - JSON filename without extension becomes prompt name (e.g., "system1")

        Example directory structure:
            prompts/
              backend/
                system1.json  -> DB="prompts", Container="backend", id="system1"
                system2.json  -> DB="prompts", Container="backend", id="system2"
              frontend/
                ui_prompt.json -> DB="prompts", Container="frontend", id="ui_prompt"

        Args:
            prompts_directory: Path to prompts root directory (str or Path)
            fail_fast: If True, raise exception on first failure; if False, continue processing

        Returns:
            Dictionary with comprehensive upload results:
            {
                "success": 5,
                "failed": 0,
                "skipped": 1,
                "total": 6,
                "files": [
                    {
                        "file": "prompts/backend/system1.json",
                        "status": "success",
                        "prompt_name": "system1",
                        "database": "prompts",
                        "container": "backend"
                    },
                    {
                        "file": "prompts/frontend/invalid.txt",
                        "status": "skipped",
                        "reason": "not a JSON file"
                    },
                ],
                "errors": [
                    {
                        "file": "prompts/backend/broken.json",
                        "error": "Invalid JSON syntax",
                        "exception": "..."
                    }
                ]
            }

        Raises:
            FileNotFoundError: If prompts_directory does not exist
            ValueError: If directory structure is invalid
            Exception: If fail_fast=True and any upload fails

        """
        prompts_path = Path(prompts_directory)

        if not prompts_path.exists():
            msg = f"Prompts directory not found: {prompts_directory}"
            raise FileNotFoundError(msg)

        if not prompts_path.is_dir():
            msg = f"Path is not a directory: {prompts_directory}"
            raise ValueError(msg)

        results = {"success": 0, "failed": 0, "skipped": 0, "total": 0, "files": [], "errors": []}

        self.logger.info(
            f"Starting prompt upload from directory: {prompts_path}", extra={"directory": str(prompts_path)}
        )

        json_files = list(prompts_path.rglob("*.json"))
        results["total"] = len(json_files)

        self.logger.info(f"Found {len(json_files)} JSON files to process", extra={"file_count": len(json_files)})

        if len(json_files) == 0:
            self.logger.warning("No JSON files found in prompts directory")
            return results

        prompt_managers: dict[str, CosmosPromptManager] = {}

        for json_file in json_files:
            file_result = {"file": str(json_file.relative_to(prompts_path.parent)), "status": "pending"}

            try:
                relative_path = json_file.relative_to(prompts_path)
                path_parts = relative_path.parts

                if len(path_parts) < 2:
                    file_result["status"] = "skipped"
                    file_result["reason"] = "Invalid directory structure - must have at least one subdirectory"
                    results["files"].append(file_result)
                    results["skipped"] += 1
                    self.logger.warning(
                        f"Skipping {json_file.name} - invalid directory structure", extra={"file": str(json_file)}
                    )
                    continue

                database_name = prompts_path.name
                container_name = path_parts[0]
                prompt_name = json_file.stem

                file_result["database"] = database_name
                file_result["container"] = container_name
                file_result["prompt_name"] = prompt_name

                with json_file.open(encoding="utf-8") as f:
                    prompt_data = json.load(f)

                manager_key = f"{database_name}:{container_name}"
                if manager_key not in prompt_managers:
                    prompt_managers[manager_key] = CosmosPromptManager(
                        cosmos_client=self.cosmos_client,
                        database_name=database_name,
                        container_name=container_name,
                        service_name=self.service_name,
                        service_version=self.service_version,
                        logger=self.logger,
                        max_retries=self.max_retries,
                        base_retry_delay=self.base_retry_delay,
                    )

                manager = prompt_managers[manager_key]

                success = manager.save_prompt(prompt_name=prompt_name, prompt_data=prompt_data)

                if success:
                    file_result["status"] = "success"
                    results["success"] += 1
                    self.logger.info(
                        f"Successfully uploaded prompt: {prompt_name}",
                        extra={"prompt_name": prompt_name, "database": database_name, "container": container_name},
                    )
                else:
                    file_result["status"] = "failed"
                    file_result["error"] = "Upload returned False"
                    results["failed"] += 1
                    results["errors"].append(
                        {
                            "file": str(json_file.relative_to(prompts_path.parent)),
                            "error": "Upload returned False",
                            "exception": None,
                        }
                    )
                    self.logger.error(
                        f"Failed to upload prompt: {prompt_name}",
                        extra={"prompt_name": prompt_name, "database": database_name, "container": container_name},
                    )

                    if fail_fast:
                        msg = f"Failed to upload prompt: {prompt_name}"
                        raise RuntimeError(msg)

            except json.JSONDecodeError as e:
                file_result["status"] = "failed"
                file_result["error"] = f"Invalid JSON: {e!s}"
                results["failed"] += 1
                results["errors"].append(
                    {
                        "file": str(json_file.relative_to(prompts_path.parent)),
                        "error": f"Invalid JSON: {e!s}",
                        "exception": str(e),
                    }
                )
                self.logger.exception(
                    f"Invalid JSON in file: {json_file.name}", extra={"file": str(json_file), "error": str(e)}
                )

                if fail_fast:
                    raise

            except Exception as e:
                file_result["status"] = "failed"
                file_result["error"] = str(e)
                results["failed"] += 1
                results["errors"].append(
                    {"file": str(json_file.relative_to(prompts_path.parent)), "error": str(e), "exception": str(e)}
                )
                self.logger.exception(
                    f"Error processing file: {json_file.name}",
                    extra={"file": str(json_file), "error": str(e)},
                )

                if fail_fast:
                    raise

            results["files"].append(file_result)

        self.logger.info(
            f"Prompt upload completed - Success: {results['success']}, Failed: {results['failed']}, Skipped: {results['skipped']}",
            extra={
                "success": results["success"],
                "failed": results["failed"],
                "skipped": results["skipped"],
                "total": results["total"],
            },
        )

        return results

    async def get_prompt_async(
        self,
        prompt_name: str,
        consistency_level: Literal["eventual", "bounded", "strong"] = "bounded",
        output_format: Literal["dict", "str"] = "dict",
    ) -> dict[str, Any] | str | None:
        """
        Asynchronously get a prompt from Cosmos DB.

        Args:
            prompt_name: Name of the prompt
            consistency_level: Consistency level for the read operation
            output_format: Output format - "dict" returns full prompt document (default), "str" returns template only

        Returns:
            If output_format="dict": Full prompt document as dictionary if found, None otherwise
            If output_format="str": Prompt template string if found, None otherwise

        """
        try:
            # Determine cache staleness based on consistency level
            staleness_ms = self._get_cache_staleness_ms(consistency_level)
            options = {}
            if staleness_ms > 0:
                options["max_integrated_cache_staleness_in_ms"] = staleness_ms

            # Check for AsyncMock or async methods
            read_item_method = self.cosmos_client.read_item

            # Handle AsyncMock case (used in tests)
            from unittest.mock import AsyncMock

            if isinstance(read_item_method, AsyncMock):
                doc = await read_item_method(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item_id=prompt_name,
                    partition_key=prompt_name,
                    **options,
                )
            # Handle other async methods
            elif hasattr(read_item_method, "__await__"):
                try:
                    doc = await read_item_method(
                        database_name=self.database_name,
                        container_name=self.container_name,
                        item_id=prompt_name,
                        partition_key=prompt_name,
                        **options,
                    )
                except Exception:
                    self.logger.exception(f"Error in async read_item call for {prompt_name}")
                    return None
            else:
                # For sync clients or mocks that return sync values
                try:
                    doc = await asyncio.to_thread(
                        read_item_method,
                        database_name=self.database_name,
                        container_name=self.container_name,
                        item_id=prompt_name,
                        partition_key=prompt_name,
                        **options,
                    )
                except Exception:
                    self.logger.exception(f"Error in sync read_item call for {prompt_name}")
                    return None

            if doc:
                # Return based on output_format
                if output_format == "str":
                    return str(doc.get("prompt_template", ""))
                # output_format == "dict"
                return doc

            return None

        except Exception:
            self.logger.exception(f"Error accessing client context for {prompt_name}")
            return None


def create_cosmos_prompt_manager(
    cosmos_client: AzureCosmosDB,
    database_name: str = "prompts",
    container_name: str = "prompts",
    service_name: str = "azure_cosmos_prompt_manager",
    service_version: str = "1.0.0",
    logger: AzureLogger | None = None,
    max_retries: int = 3,
    base_retry_delay: float = 1.0,
) -> CosmosPromptManager:
    """
    Factory function to create an instance of CosmosPromptManager with enhanced features.

    Args:
        cosmos_client: AzureCosmosDB client instance
        database_name: Name of the Cosmos DB database
        container_name: Name of the Cosmos DB container
        service_name: Service name for logging
        service_version: Service version for logging
        logger: Optional AzureLogger instance
        max_retries: Maximum number of retry attempts
        base_retry_delay: Base delay in seconds for retry logic

    Returns:
        Configured CosmosPromptManager instance with enhanced features

    """
    return CosmosPromptManager(
        cosmos_client=cosmos_client,
        database_name=database_name,
        container_name=container_name,
        service_name=service_name,
        service_version=service_version,
        logger=logger,
        max_retries=max_retries,
        base_retry_delay=base_retry_delay,
    )


def upload_prompts_from_directory(
    prompts_directory: str | Path,
    cosmos_client: AzureCosmosDB,
    logger: AzureLogger | None = None,
    fail_fast: bool = False,
    service_name: str = "prompt_uploader",
    service_version: str = "1.0.0",
    max_retries: int = 3,
    base_retry_delay: float = 1.0,
) -> dict[str, Any]:
    """
    Upload prompt templates from directory structure to Cosmos DB.

    This is a convenience function that delegates to CosmosPromptManager.upload_prompts_from_directory().
    For cleaner code, consider using the class method directly:

        manager = CosmosPromptManager(cosmos_client=cosmos_client)
        results = manager.upload_prompts_from_directory(prompts_directory="prompts")

    Directory structure automatically determines database and container names:
    - Root directory name becomes database name (e.g., "prompts")
    - Subdirectory name becomes container name (e.g., "backend")
    - JSON filename without extension becomes prompt name (e.g., "system1")

    Example directory structure:
        prompts/
          backend/
            system1.json  -> DB="prompts", Container="backend", id="system1"
            system2.json  -> DB="prompts", Container="backend", id="system2"
          frontend/
            ui_prompt.json -> DB="prompts", Container="frontend", id="ui_prompt"

    Args:
        prompts_directory: Path to prompts root directory (str or Path)
        cosmos_client: AzureCosmosDB client instance for database operations
        logger: Optional AzureLogger for progress tracking (creates default if None)
        fail_fast: If True, raise exception on first failure; if False, continue processing
        service_name: Service name for logging context
        service_version: Service version for logging context
        max_retries: Maximum number of retry attempts for each upload
        base_retry_delay: Base delay in seconds for retry logic

    Returns:
        Dictionary with comprehensive upload results (see CosmosPromptManager.upload_prompts_from_directory)

    Raises:
        FileNotFoundError: If prompts_directory does not exist
        ValueError: If directory structure is invalid
        Exception: If fail_fast=True and any upload fails

    """
    manager = CosmosPromptManager(
        cosmos_client=cosmos_client,
        database_name="prompts",
        container_name="prompts",
        service_name=service_name,
        service_version=service_version,
        logger=logger,
        max_retries=max_retries,
        base_retry_delay=base_retry_delay,
    )

    return manager.upload_prompts_from_directory(
        prompts_directory=prompts_directory,
        fail_fast=fail_fast,
    )
