import logging
from typing import Any, Literal, TypeVar

from polycrud import cache, exceptions
from polycrud.connectors.base import DEFAULT_CACHE_TTL, AsyncBaseConnector
from polycrud.entity.base import ModelEntity

try:
    import asyncpg
    from asyncpg import Pool
except ImportError as e:
    raise ImportError("asyncpg is not installed. Please install it with 'pip install asyncpg'") from e

T = TypeVar("T", bound=ModelEntity)
P = TypeVar("P")

_Logger = logging.getLogger(__name__)


class AsyncPostgresConnector(AsyncBaseConnector):
    """
    Base class for asynchronous PostgreSQL connector.
    """

    def __init__(self, host: str, port: int, user: str, password: str, db: str):
        """
        Initialize the connector with the given parameters.
        """
        self.pool: Pool | None = None
        self.db_config: dict[str, Any] = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": db,
        }

    async def connect(self, pool_size: int = 10) -> None:
        """
        Connect to the data source.
        """
        try:
            self.pool = await asyncpg.create_pool(min_size=1, max_size=pool_size, **self.db_config)
            _Logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            _Logger.error(f"Failed to connect to PostgreSQL database: {e}")
            raise exceptions.ConnectionNotInitialized(f"Failed to connect to PostgreSQL: {e}") from e

    async def disconnect(self) -> None:
        """
        Disconnect from the data source.
        """
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
            _Logger.info("Successfully disconnected from PostgreSQL database")
        else:
            _Logger.warning("No active connection to disconnect")

    async def health_check(self) -> bool:
        """
        Check the health of the connection.

        Returns:
            bool: True if the connection is healthy, False otherwise.
        """
        if self.pool is None:
            _Logger.warning("No connection pool initialized")
            return False

        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return bool(result == 1)
        except Exception as e:
            _Logger.error(f"Health check failed: {e}")
            return False

    async def find_one(
        self,
        collection: type[T],
        query: str | None = None,
        raise_if_not_found: bool = False,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> T | None:
        """
        Find one entity in the database.
        Args:
            collection: The schema class to use for the entity.
            query (Optional): The query string to execute.
            raise_if_not_found: Flag to raise an exception if no entity is found.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.
            **kwargs: Search by key and value pairs.

        Returns:
            A single entity of type T

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
            EntityNotFound: If no entity is found matching the criteria
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        try:
            async with self.pool.acquire() as conn:
                if query:
                    # If a custom query is provided, use it with kwargs as parameters
                    result = await conn.fetchrow(query, *kwargs.values())
                else:
                    # Otherwise, build a query from kwargs
                    table_name = collection.__name__.lower()

                    # Handle the case with no search criteria
                    if not kwargs:
                        query = f"SELECT * FROM {table_name} LIMIT 1"
                        result = await conn.fetchrow(query)
                    else:
                        # Build WHERE clause from kwargs
                        where_conditions = " AND ".join([f"{key} = ${i + 1}" for i, key in enumerate(kwargs)])
                        query = f"SELECT * FROM {table_name} WHERE {where_conditions} LIMIT 1"
                        result = await conn.fetchrow(query, *kwargs.values())

                if not result:
                    if raise_if_not_found:
                        raise exceptions.NotFoundError(f"Entity not found in {collection.__name__}")
                    return None

                # Create an instance of the collection class with the result
                return collection(**dict(result))

        except asyncpg.PostgresError as e:
            _Logger.error(f"Database error in find_one: {e}")
            raise
        except Exception as e:
            _Logger.error(f"Unexpected error in find_one: {e}")
            raise

    async def find_many(
        self,
        collection: type[T],
        *,
        limit: int = 10_000,
        offset: int = 0,
        sort_field: str = "id",
        sort_dir: Literal["asc", "desc"] = "asc",
        query: str | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> list[T]:
        """
        Find multiple entities in the database.

        Args:
            collection: The schema class to use for the entities.
            limit: Maximum number of results to return.
            offset: Offset for pagination.
            sort_field: Field to sort by.
            sort_dir: Sort direction ('asc' or 'desc').
            query: Optional custom query string to execute.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.
            **kwargs: Search by key and value pairs.

        Returns:
            A list of entities of type T

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        try:
            async with self.pool.acquire() as conn:
                if query:
                    # If a custom query is provided, use it with kwargs as parameters
                    # Note: Custom queries should handle pagination and sorting themselves
                    results = await conn.fetch(query, *kwargs.values())
                else:
                    # Otherwise, build a query from kwargs
                    table_name = collection.__name__.lower()

                    # Build the base query
                    base_query = f"SELECT * FROM {table_name}"
                    params = []

                    # Build WHERE clause from kwargs if any
                    if kwargs:
                        where_conditions = " AND ".join([f"{key} = ${i + 1}" for i, key in enumerate(kwargs)])
                        base_query += f" WHERE {where_conditions}"
                        params.extend(list(kwargs.values()))

                    # Add sorting
                    base_query += f" ORDER BY {sort_field} {sort_dir.upper()}"

                    # Add pagination
                    param_offset = len(params)
                    base_query += f" LIMIT ${param_offset + 1} OFFSET ${param_offset + 2}"
                    params.extend([limit, offset])

                    # Execute the query
                    results = await conn.fetch(base_query, *params)

                # Create instances of the collection class with the results
                return [collection(**dict(row)) for row in results]

        except asyncpg.PostgresError as e:
            _Logger.error(f"Database error in find_many: {e}")
            raise
        except Exception as e:
            _Logger.error(f"Unexpected error in find_many: {e}")
            raise

    @cache.cache()
    async def insert_one(
        self,
        obj: T,
        *,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> T:
        """
        Insert a single entity into the database.

        Args:
            obj: The entity object to insert.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

        Returns:
            The inserted entity with updated fields (like auto-generated ID).

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            InsertionError: If the insertion operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        if not isinstance(obj, ModelEntity):
            raise ValueError("Object must be an instance of ModelEntity")

        # Get the table name from the object's class name
        table_name = obj.__class__.__name__.lower()

        # Convert the object to a dictionary
        data = obj.dict()

        # Remove None values from the data dictionary
        data = {k: v for k, v in data.items() if v is not None}

        # Prepare the fields and placeholders for the INSERT statement
        fields = ", ".join(data.keys())
        placeholders = ", ".join([f"${i + 1}" for i in range(len(data))])
        values = list(data.values())

        query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"

        # Add RETURNING clause to get the inserted ID
        if hasattr(obj, "id") and obj.id is None:
            query += " RETURNING id"

        try:
            async with self.pool.acquire() as conn:
                if hasattr(obj, "id") and obj.id is None:
                    result = await conn.fetchval(query, *values)
                    obj.id = result
                else:
                    await conn.execute(query, *values)

                _Logger.info(f"Successfully inserted entity into {table_name}")
                return obj

        except asyncpg.PostgresError as e:
            _Logger.error(f"Error inserting entity: {e}")
            raise exceptions.InsertionError(f"Failed to insert entity: {e}") from e
        except Exception as e:
            _Logger.error(f"Unexpected error inserting entity: {e}")
            raise exceptions.InsertionError(f"Failed to insert entity: {e}") from e

    @cache.cache()
    async def insert_many(
        self,
        objs: list[T],
        *,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> list[T]:
        """
        Insert multiple entities into the database.

        Args:
            objs: A list of entity objects to insert.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

        Returns:
            The inserted entities with updated fields (like auto-generated ID).

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            InsertionError: If the insertion operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        if not objs:
            return []

        if not all(isinstance(o, ModelEntity) for o in objs):
            raise ValueError("All objects must be instances of ModelEntity")

        # Get the table name from the first object's class name
        table_name = objs[0].__class__.__name__.lower()

        # Convert the objects to a list of dictionaries
        data_list = [o.dict() for o in objs]

        # Remove None values from each data dictionary
        data_list = [{k: v for k, v in data.items() if v is not None} for data in data_list]

        # Prepare the fields for the INSERT statement
        fields = list(data_list[0].keys())
        field_names = ", ".join(fields)

        # Prepare values for executemany
        values = [tuple(data[field] for field in fields) for data in data_list]

        # Build the query
        placeholders = ", ".join([f"${i + 1}" for i in range(len(fields))])
        query = f"INSERT INTO {table_name} ({field_names}) VALUES ({placeholders})"

        # Add RETURNING clause to get the inserted IDs
        if hasattr(objs[0], "id") and objs[0].id is None:
            query += " RETURNING id"

        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    if hasattr(objs[0], "id") and objs[0].id is None:
                        # Execute inserts one by one to get returning values
                        for i, obj in enumerate(objs):
                            single_query = f"INSERT INTO {table_name} ({field_names}) VALUES ({placeholders}) RETURNING id"
                            result = await conn.fetchval(single_query, *values[i])
                            obj.id = result
                    else:
                        # Use executemany for better performance
                        await conn.executemany(query, values)

                _Logger.info(f"Successfully inserted {len(objs)} entities into {table_name}")
                return objs

        except asyncpg.PostgresError as e:
            _Logger.error(f"Error inserting entities: {e}")
            raise exceptions.InsertionError(f"Failed to insert entities: {e}") from e
        except Exception as e:
            _Logger.error(f"Unexpected error inserting entities: {e}")
            raise exceptions.InsertionError(f"Failed to insert entities: {e}") from e

    @cache.cache()
    async def update_one(
        self,
        obj: T,
        *,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> T:
        """
        Update a single entity in the database.

        Args:
            obj: The entity object to update.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

        Returns:
            The updated entity.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            UpdateError: If the update operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        if not isinstance(obj, ModelEntity):
            raise ValueError("Object must be an instance of ModelEntity")

        # Get the table name from the object's class name
        table_name = obj.__class__.__name__.lower()

        # Convert the object to a dictionary
        data = obj.dict()

        # Remove None values and id from the data dictionary
        data = {k: v for k, v in data.items() if v is not None and k != "id"}

        # Prepare the fields and placeholders for the UPDATE statement
        set_clause = ", ".join([f"{key} = ${i + 1}" for i, key in enumerate(data.keys())])
        values = list(data.values())

        # Add the ID to the end of the values list for the WHERE clause
        values.append(obj.id)
        where_clause = f"id = ${len(values)}"

        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, *values)
                _Logger.info(f"Successfully updated entity in {table_name}")
                return obj

        except asyncpg.PostgresError as e:
            _Logger.error(f"Error updating entity: {e}")
            raise exceptions.UpdateError(f"Failed to update entity: {e}") from e
        except Exception as e:
            _Logger.error(f"Unexpected error updating entity: {e}")
            raise exceptions.UpdateError(f"Failed to update entity: {e}") from e

    @cache.cache()
    async def delete_one(
        self, collection: type[T], *, id: int, _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL
    ) -> None:
        """
        Delete a single entity from the database.

        Args:
            collection: The schema class to use for the entity.
            id: The ID of the entity to delete.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            DeletionError: If the deletion operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        try:
            async with self.pool.acquire() as conn:
                table_name = collection.__name__.lower()
                query = f"DELETE FROM {table_name} WHERE id = $1"
                await conn.execute(query, id)
                _Logger.info(f"Successfully deleted entity from {table_name}")

        except asyncpg.PostgresError as e:
            _Logger.error(f"Error deleting entity: {e}")
            raise exceptions.DeletionError(f"Failed to delete entity: {e}") from e
        except Exception as e:
            _Logger.error(f"Unexpected error deleting entity: {e}")
            raise exceptions.DeletionError(f"Failed to delete entity: {e}") from e

    @cache.cache()
    async def delete_many(
        self,
        collection: type[T],
        *,
        ids: list[int],
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> None:
        """
        Delete multiple entities from the database.

        Args:
            collection: The schema class to use for the entities.
            ids: A list of IDs of the entities to delete.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            DeletionError: If the deletion operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        try:
            async with self.pool.acquire() as conn:
                table_name = collection.__name__.lower()
                # Use ANY() operator for PostgreSQL IN clause
                query = f"DELETE FROM {table_name} WHERE id = ANY($1)"
                await conn.execute(query, ids)
                _Logger.info(f"Successfully deleted {len(ids)} entities from {table_name}")

        except asyncpg.PostgresError as e:
            _Logger.error(f"Error deleting entities: {e}")
            raise exceptions.DeletionError(f"Failed to delete entities: {e}") from e
        except Exception as e:
            _Logger.error(f"Unexpected error deleting entities: {e}")
            raise exceptions.DeletionError(f"Failed to delete entities: {e}") from e

    @cache.cache()
    async def count(
        self,
        collection: type[T],
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> int:
        """
        Count the number of entities in the database.

        Args:
            collection: The schema class to use for the entities.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.
            **kwargs: Search by key and value pairs.

        Returns:
            The count of entities of type T

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        try:
            async with self.pool.acquire() as conn:
                table_name = collection.__name__.lower()

                # Build base query
                query = f"SELECT COUNT(*) FROM {table_name}"

                params = []
                # Add WHERE clause if kwargs are provided
                if kwargs:
                    where_conditions = " AND ".join([f"{key} = ${i + 1}" for i, key in enumerate(kwargs)])
                    query += f" WHERE {where_conditions}"
                    params = list(kwargs.values())

                result = await conn.fetchval(query, *params)
                return result if result is not None else 0

        except asyncpg.PostgresError as e:
            _Logger.error(f"Database error in count: {e}")
            raise
        except Exception as e:
            _Logger.error(f"Unexpected error in count: {e}")
            raise

    @cache.cache()
    async def raw_query(
        self,
        query: str,
        params: list[Any] | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> Any:
        """
        Execute a raw SQL query.

        Args:
            query: The SQL query string.
            params: Optional parameters for the query.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

        Returns:
            A list of dictionaries representing the rows returned by the query.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
            QueryError: If the query execution fails
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        try:
            async with self.pool.acquire() as conn:
                if params:
                    results = await conn.fetch(query, *params)
                else:
                    results = await conn.fetch(query)

                return [dict(row) for row in results]

        except asyncpg.PostgresError as e:
            _Logger.error(f"Database error in raw_query: {e}")
            raise exceptions.QueryExecutionError(f"Failed to execute raw query: {e}") from e
        except Exception as e:
            _Logger.error(f"Unexpected error in raw_query: {e}")
            raise exceptions.QueryExecutionError(f"Failed to execute raw query: {e}") from e
