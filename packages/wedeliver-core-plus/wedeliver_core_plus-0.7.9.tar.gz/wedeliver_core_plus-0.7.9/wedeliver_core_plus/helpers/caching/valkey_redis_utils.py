import json
import hashlib
from datetime import timedelta
from redis import Redis, exceptions as redis_exceptions
from sqlalchemy import event, inspect
from flask import current_app


class BaseCacheRule:
    """
    Base caching rule that:
    - Uses a singleton Redis (Valkey) client
    - Reads config from Flask app
    - Prefixes all cache keys with SERVICE_NAME for service isolation
    - Supports multiple models + per-model events/columns
    - Invalidates cache when model events or watched columns change
    - Uses dynamic API path set by the route decorator
    - Supports granular invalidation via invalidation_key_fields
    - Supports per-model field mapping via key_mapping in model_invalidation_map

    Cache key format:
        - Without tags: {service_name}:/path:hash
        - With tags: {service_name}:/path:field1=value1:field2=value2:hash

        Example:
            thrivve-service:/finance/api/v1/me/balance:customer_id=123:abc123

    invalidation_key_fields format:
        - Empty list []: Path-based invalidation (invalidates all cache for endpoint)
        - List of strings: Granular invalidation using API parameter names

        Example:
            invalidation_key_fields = ["customer_id", "country_code"]

    model_invalidation_map format:
        - key_mapping: Optional dict mapping DB column names to API parameter names
        - If key_mapping is not provided, assumes DB column name = API param name

        Example:
            model_invalidation_map = {
                CustomerTransactionEntry: {
                    "events": ["after_update", "after_insert"],
                    "columns": ["status", "amount"],
                    "key_mapping": {
                        "party_id": "customer_id",  # DB column → API param
                        "country": "country_code"
                    }
                },
                Customer: {
                    "events": ["after_update"],
                    # No key_mapping needed if DB columns match API params
                }
            }
    """

    _listeners_registered = set()
    _cache_rule_registry = {}  # {(model, events_tuple): [cache_rule_instance1, cache_rule_instance2, ...]}
    _redis_client = None  # Singleton Redis connection
    _service_name = None  # Service name prefix for cache keys
    ttl = timedelta(minutes=5)
    model_invalidation_map = {}
    invalidation_key_fields = []  # Empty = path-based, String = same name, Tuple = alias mapping

    def __init__(self, path: str = None):
        self.path = path

        # Initialize service name from Flask config (once per class)
        if BaseCacheRule._service_name is None:
            BaseCacheRule._service_name = current_app.config.get("SERVICE_NAME", "default-service")

        # Use shared Redis connection (singleton)
        if BaseCacheRule._redis_client is None:
            BaseCacheRule._redis_client = self._create_redis_client()

        self.cache = BaseCacheRule._redis_client

        # Only register invalidation events if cache is available
        if self.cache is not None:
            self._register_all_invalidation_events()

    # ---------------- Redis Singleton Setup ----------------

    def _create_redis_client(self):
        """Create a shared Redis/Valkey client safely, reading config from Flask."""
        app = current_app

        # Check if Redis is enabled via ENABLE_REDIS flag
        enable_redis = app.config.get("ENABLE_REDIS", False)

        if not enable_redis:
            print("[Valkey] Redis is disabled via ENABLE_REDIS flag")
            return None

        host = app.config.get("VALKEY_HOST", "valkey-redis")
        port = app.config.get("VALKEY_PORT", 6379)
        ssl = app.config.get("VALKEY_SSL", False)

        try:
            client = Redis(
                host=host,
                port=port,
                ssl=ssl,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            client.ping()
            print(f"[Valkey] Connected to {host}:{port}")
            return client
        except redis_exceptions.ConnectionError as e:
            # Gracefully handle connection failures in ALL environments
            print(f"[Valkey WARNING] Connection failed: {e}")
            return None

    # ---------------- Core cache ops ----------------

    def make_key(self, params: dict) -> str:
        """
        Create cache key with optional metadata tags for granular invalidation.

        Format without tags: {service_name}:/path:hash
        Format with tags: {service_name}:/path:field1=value1:field2=value2:hash

        Args:
            params: Dictionary of parameters to hash

        Returns:
            Cache key string with optional metadata tags and service prefix

        Note:
            invalidation_key_fields contains API parameter names (strings only).
            Field mapping from DB columns to API params is handled in model_invalidation_map.
        """
        raw = json.dumps(params or {}, sort_keys=True)
        digest = hashlib.md5(raw.encode()).hexdigest()

        # Add metadata tags if invalidation_key_fields are defined
        if self.invalidation_key_fields:
            tags = []

            for api_param in self.invalidation_key_fields:
                # invalidation_key_fields now contains only API param names (strings)
                if api_param in params:
                    value = self._format_value(params[api_param])
                    tags.append(f"{api_param}={value}")

            if tags:
                tag_str = ":".join(tags)
                return f"{self._service_name}:{self.path}:{tag_str}:{digest}"

        return f"{self._service_name}:{self.path}:{digest}"

    def get(self, key: str):
        if not self.cache:
            return None
        try:
            data = self.cache.get(key)
            return json.loads(data) if data else None
        except redis_exceptions.RedisError as e:
            self._warn(f"get() failed: {e}")
            return None

    def set(self, key: str, data: dict):
        if not self.cache:
            return
        try:
            self.cache.setex(key, int(self.ttl.total_seconds()), json.dumps(data))
        except redis_exceptions.RedisError as e:
            self._warn(f"set() failed: {e}")

    def invalidate_by_path(self):
        """Invalidate all cache entries for this path (path-based invalidation)."""
        if not self.cache or not self.path:
            return
        try:
            deleted = 0
            pattern = f"{self._service_name}:{self.path}:*"
            for key in self.cache.scan_iter(pattern):
                self.cache.delete(key)
                deleted += 1
            print(f"[Cache] Invalidated {deleted} keys for {self.path}")
        except redis_exceptions.RedisError as e:
            self._warn(f"invalidate_by_path() failed: {e}")

    def invalidate_by_params(self, params: dict):
        """
        Invalidate cache entries matching specific parameters (granular invalidation).

        Uses pattern matching with metadata tags to find and delete matching keys.

        Args:
            params: Dictionary of parameters to match (e.g., {"customer_id": 123})

        Example:
            params = {"customer_id": 123}
            Pattern: {service_name}:/api/profile:customer_id=123:*
            Matches: {service_name}:/api/profile:customer_id=123:abc123...
                     {service_name}:/api/profile:customer_id=123:def456...

        Note:
            invalidation_key_fields contains API parameter names (strings only).
            Field mapping from DB columns to API params is handled in model_invalidation_map.
        """
        if not self.cache or not self.path:
            return

        if not params:
            print("[Cache WARNING] invalidate_by_params called with empty params, falling back to path invalidation")
            self.invalidate_by_path()
            return

        try:
            # Build pattern with metadata tags
            tags = []

            for api_param in self.invalidation_key_fields:
                # invalidation_key_fields now contains only API param names (strings)
                if api_param in params:
                    value = self._format_value(params[api_param])
                    tags.append(f"{api_param}={value}")

            if not tags:
                print("[Cache WARNING] No valid invalidation fields found in params, falling back to path invalidation")
                self.invalidate_by_path()
                return

            # Create pattern: {service_name}:/path:field1=value1:field2=value2:*
            tag_str = ":".join(tags)
            pattern = f"{self._service_name}:{self.path}:{tag_str}:*"

            deleted = 0
            for key in self.cache.scan_iter(pattern):
                self.cache.delete(key)
                deleted += 1

            print(f"[Cache] Invalidated {deleted} key(s) matching pattern: {pattern}")
        except redis_exceptions.RedisError as e:
            self._warn(f"invalidate_by_params() failed: {e}")

    # ---------------- SQLAlchemy event setup ----------------

    def _register_all_invalidation_events(self):
        for model, cfg in self.model_invalidation_map.items():
            events = cfg.get("events", [])
            columns = cfg.get("columns", [])
            key_mapping = cfg.get("key_mapping", {})

            registry_key = (model, tuple(events))

            # Add this cache rule instance to the registry
            if registry_key not in self._cache_rule_registry:
                self._cache_rule_registry[registry_key] = []

            # Check if this specific path is already registered (prevent duplicate paths)
            existing_paths = [rule.path for rule in self._cache_rule_registry[registry_key]]
            if self.path not in existing_paths:
                self._cache_rule_registry[registry_key].append(self)
                print(f"[Cache] Added {self.path} to registry for {model.__name__} → {events}")
            else:
                print(f"[Cache] Skipped duplicate registration for {self.path} on {model.__name__}")

            # Register SQLAlchemy listener ONCE per model+events (not per cache rule)
            if registry_key not in self._listeners_registered:
                # Register a GLOBAL handler (class method)
                for ev in events:
                    event.listen(model, ev, self._global_invalidation_handler)

                self._listeners_registered.add(registry_key)

                # Enhanced logging with key_mapping info
                mapping_str = f", key_mapping={key_mapping}" if key_mapping else ""
                print(f"[Cache] Registered global listener for {model.__name__} → {events}, columns={columns}{mapping_str}")

    @classmethod
    def _global_invalidation_handler(cls, mapper, connection, target):
        """
        Global handler that fires invalidation for ALL cache rules using this model.

        This is a CLASS METHOD, not an instance method, so it can access the registry
        and iterate over all cache rule instances that depend on this model.

        Args:
            mapper: SQLAlchemy mapper
            connection: Database connection
            target: Model instance that triggered the event
        """
        model = target.__class__

        # Find all cache rules that registered this model
        for registry_key, cache_rules in cls._cache_rule_registry.items():
            registered_model, events = registry_key

            if registered_model != model:
                continue  # Skip models we're not interested in

            # Iterate over ALL cache rule instances that depend on this model
            for cache_rule in cache_rules:
                # Delegate to instance method for actual invalidation logic
                cache_rule._invalidate_for_model_change(target)

    def _invalidate_for_model_change(self, target):
        """
        Instance method that handles invalidation logic for THIS cache rule.
        Called by the global handler for each cache rule that depends on the changed model.

        Args:
            target: SQLAlchemy model instance that triggered the event
        """
        model = target.__class__
        cfg = self.model_invalidation_map.get(model, {})

        if not cfg:
            return  # This cache rule doesn't use this model

        watched_cols = cfg.get("columns", [])
        events = cfg.get("events", [])

        state = inspect(target)
        changed = [
            attr.key
            for attr in state.attrs
            if attr.key in watched_cols and attr.history.has_changes()
        ]

        # Invalidate if any configured event fired OR watched columns changed
        if changed or events:
            print(
                f"[Cache] Invalidation triggered for {self.path} by {model.__name__}, changed={changed}"
            )

            # Conditional invalidation based on invalidation_key_fields
            if self.invalidation_key_fields:
                # Granular invalidation - extract params and invalidate specific keys
                invalidation_params = self._extract_invalidation_params(target)
                self.invalidate_by_params(invalidation_params)
            else:
                # Path-based invalidation - invalidate all keys for this path
                self.invalidate_by_path()

    def _extract_invalidation_params(self, target):
        """
        Extract invalidation key field values from the changed model instance.
        Uses per-model key_mapping to map DB columns to API parameters.

        Args:
            target: SQLAlchemy model instance that triggered the event

        Returns:
            dict: Parameters to use for cache key invalidation (using API param names)

        Examples:
            # Without key_mapping (DB column = API param)
            invalidation_key_fields = ["customer_id", "country_code"]
            model_invalidation_map = {
                Customer: {"events": ["after_update"]}
            }
            target.customer_id = 123, target.country_code = "sa"
            Returns: {"customer_id": 123, "country_code": "sa"}

            # With key_mapping (DB column → API param)
            invalidation_key_fields = ["customer_id"]
            model_invalidation_map = {
                CustomerTransactionEntry: {
                    "events": ["after_update"],
                    "key_mapping": {"party_id": "customer_id"}
                }
            }
            target.party_id = 123
            Returns: {"customer_id": 123}
        """
        params = {}
        model = target.__class__
        cfg = self.model_invalidation_map.get(model, {})
        key_mapping = cfg.get("key_mapping", {})  # {db_column: api_param}

        for api_param in self.invalidation_key_fields:
            # Find the DB column name for this API param
            # Check if there's a mapping for this API param
            db_column = None

            # Look for reverse mapping: find db_column where key_mapping[db_column] == api_param
            for db_col, mapped_api_param in key_mapping.items():
                if mapped_api_param == api_param:
                    db_column = db_col
                    break

            # If no mapping found, assume db_column = api_param (same name)
            if db_column is None:
                db_column = api_param

            # Extract value from target model
            if hasattr(target, db_column):
                value = getattr(target, db_column)
                params[api_param] = value
            else:
                print(
                    f"[Cache WARNING] Field '{db_column}' not found on {model.__name__}. "
                    f"Check key_mapping in model_invalidation_map."
                )

        return params

    # ---------------- Helpers ----------------

    def _format_value(self, value):
        """
        Format a value for use in cache keys.

        Args:
            value: The value to format (int, str, bool, dict, list, etc.)

        Returns:
            str: Formatted value suitable for cache key
        """
        if isinstance(value, (int, str)):
            return str(value)
        else:
            return json.dumps(value)

    def _warn(self, msg: str):
        print(f"[Valkey WARNING] {msg}")

    @classmethod
    def flush_all_cache(cls):
        """
        Flush all cache entries for the current service.

        This is a CLASS METHOD that can be called without instantiating the cache rule.
        Useful for clearing all cache on application startup to prevent stale data issues
        after deployments.

        Uses SCAN pattern to only delete keys prefixed with the service name.
        This allows multiple services to share the same Redis instance safely.
        Respects ENABLE_REDIS flag - only flushes if Redis is enabled.

        Returns:
            bool: True if flush succeeded, False if Redis is disabled or flush failed

        Example:
            # In app initialization
            from wedeliver_core_plus import BaseCacheRule
            BaseCacheRule.flush_all_cache()
        """
        from flask import current_app

        try:
            app = current_app

            # Check if Redis is enabled via ENABLE_REDIS flag
            enable_redis = app.config.get("ENABLE_REDIS", False)

            if not enable_redis:
                print("[Cache] Redis is disabled via ENABLE_REDIS flag, skipping cache flush")
                return False

            # Initialize service name if not set
            if cls._service_name is None:
                cls._service_name = app.config.get("SERVICE_NAME", "default-service")

            # Use singleton client if exists, otherwise create it
            if cls._redis_client is None:
                # Create singleton client using existing method
                temp_instance = cls.__new__(cls)  # Create instance without calling __init__
                cls._redis_client = temp_instance._create_redis_client()

            # If client creation failed, return False
            if cls._redis_client is None:
                print("[Cache] Redis client unavailable, skipping cache flush")
                return False

            # Scan and delete only keys for this service
            pattern = f"{cls._service_name}:*"
            deleted = 0

            for key in cls._redis_client.scan_iter(pattern):
                cls._redis_client.delete(key)
                deleted += 1

            print(f"[Cache] Successfully flushed {deleted} cache entries for service '{cls._service_name}'")
            return True

        except redis_exceptions.RedisError as e:
            print(f"[Cache] Failed to flush cache: {e}")
            return False
        except Exception as e:
            print(f"[Cache] Unexpected error during cache flush: {e}")
            return False

    @classmethod
    def flush_service_cache(cls, service_name=None):
        """
        Flush all cache entries for a specific service.

        This is a CLASS METHOD that can be called to clear cache for any service.
        Useful for cross-service cache management or administrative operations.

        Args:
            service_name: Service name to flush. If None, uses current service from config.

        Returns:
            int: Number of keys deleted, or -1 if operation failed

        Example:
            # Flush cache for a specific service
            from wedeliver_core_plus import BaseCacheRule
            deleted = BaseCacheRule.flush_service_cache("thrivve-service")
            print(f"Deleted {deleted} keys")
        """
        from flask import current_app

        try:
            app = current_app

            # Check if Redis is enabled via ENABLE_REDIS flag
            enable_redis = app.config.get("ENABLE_REDIS", False)

            if not enable_redis:
                print("[Cache] Redis is disabled via ENABLE_REDIS flag, skipping cache flush")
                return -1

            # Use provided service name or get from config
            target_service = service_name
            if target_service is None:
                target_service = app.config.get("SERVICE_NAME", "default-service")

            # Use singleton client if exists, otherwise create it
            if cls._redis_client is None:
                # Create singleton client using existing method
                temp_instance = cls.__new__(cls)  # Create instance without calling __init__
                cls._redis_client = temp_instance._create_redis_client()

            # If client creation failed, return -1
            if cls._redis_client is None:
                print("[Cache] Redis client unavailable, skipping cache flush")
                return -1

            # Scan and delete only keys for the target service
            pattern = f"{target_service}:*"
            deleted = 0

            for key in cls._redis_client.scan_iter(pattern):
                cls._redis_client.delete(key)
                deleted += 1

            print(f"[Cache] Flushed {deleted} cache entries for service '{target_service}'")
            return deleted

        except redis_exceptions.RedisError as e:
            print(f"[Cache] Failed to flush cache for service '{target_service}': {e}")
            return -1
        except Exception as e:
            print(f"[Cache] Unexpected error during cache flush: {e}")
            return -1
