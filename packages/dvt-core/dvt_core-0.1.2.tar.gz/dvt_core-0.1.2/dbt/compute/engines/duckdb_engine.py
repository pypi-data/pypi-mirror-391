"""
DuckDB Compute Engine

Provides an ephemeral in-process DuckDB instance for federated query execution.
DuckDB is used for small to medium workloads and provides excellent performance
with PyArrow integration.

Key characteristics:
- In-process embedded database
- Excellent Arrow integration (zero-copy)
- Fast analytical queries
- No materialization (ephemeral only)
"""

import duckdb
import pyarrow as pa
from typing import Any, Dict, List, Optional
from dbt_common.exceptions import DbtRuntimeError


class DuckDBEngine:
    """
    Ephemeral DuckDB compute engine for federated query execution.

    Each instance creates an in-memory DuckDB database that exists only
    for the duration of the query execution. All tables are registered
    from PyArrow tables and results are returned as PyArrow tables.
    """

    def __init__(self, memory_limit: str = "80%", threads: Optional[int] = None):
        """
        Initialize DuckDB engine.

        :param memory_limit: Memory limit for DuckDB (e.g., '80%', '8GB')
        :param threads: Number of threads (None = auto-detect)
        """
        self.memory_limit = memory_limit
        self.threads = threads
        self.connection: Optional[duckdb.DuckDBPyConnection] = None
        self.registered_tables: Dict[str, str] = {}  # table_name -> alias mapping

    def __enter__(self):
        """Context manager entry - initialize DuckDB connection."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close DuckDB connection."""
        self.close()

    def connect(self) -> None:
        """
        Create ephemeral in-memory DuckDB connection.

        Configures DuckDB for optimal performance with Arrow data.
        """
        try:
            # Create in-memory database
            self.connection = duckdb.connect(database=":memory:")

            # Configure DuckDB
            if self.memory_limit:
                self.connection.execute(f"SET memory_limit='{self.memory_limit}'")

            if self.threads:
                self.connection.execute(f"SET threads={self.threads}")

            # Enable Arrow optimization
            self.connection.execute("SET enable_object_cache=true")

        except Exception as e:
            raise DbtRuntimeError(f"Failed to initialize DuckDB engine: {str(e)}") from e

    def close(self) -> None:
        """Close DuckDB connection and release resources."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass  # Best effort cleanup
            finally:
                self.connection = None
                self.registered_tables.clear()

    def register_arrow_table(
        self,
        arrow_table: pa.Table,
        table_name: str,
        replace: bool = False
    ) -> None:
        """
        Register a PyArrow table with DuckDB.

        Uses DuckDB's native Arrow integration for zero-copy data access.

        :param arrow_table: PyArrow Table to register
        :param table_name: Name to use for the table in DuckDB
        :param replace: If True, replace existing table with same name
        :raises DbtRuntimeError: If registration fails
        """
        if not self.connection:
            raise DbtRuntimeError("DuckDB engine not connected")

        try:
            # Check if table already exists
            if table_name in self.registered_tables and not replace:
                raise DbtRuntimeError(
                    f"Table '{table_name}' already registered. Use replace=True to overwrite."
                )

            # Register Arrow table directly with DuckDB
            # DuckDB can query Arrow tables with zero-copy
            self.connection.register(table_name, arrow_table)
            self.registered_tables[table_name] = table_name

        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to register Arrow table '{table_name}' with DuckDB: {str(e)}"
            ) from e

    def execute_query(self, sql: str) -> pa.Table:
        """
        Execute SQL query and return results as PyArrow Table.

        The query can reference any tables registered via register_arrow_table().

        :param sql: SQL query to execute
        :returns: PyArrow Table with query results
        :raises DbtRuntimeError: If query execution fails
        """
        if not self.connection:
            raise DbtRuntimeError("DuckDB engine not connected")

        try:
            # Execute query and fetch as Arrow
            result = self.connection.execute(sql).fetch_arrow_table()
            return result

        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to execute query in DuckDB: {str(e)}\nSQL: {sql}"
            ) from e

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get metadata about a registered table.

        :param table_name: Name of the table
        :returns: Dictionary with table metadata (columns, row_count, etc.)
        :raises DbtRuntimeError: If table not found
        """
        if not self.connection:
            raise DbtRuntimeError("DuckDB engine not connected")

        if table_name not in self.registered_tables:
            raise DbtRuntimeError(f"Table '{table_name}' not registered")

        try:
            # Get table schema
            schema_query = f"DESCRIBE {table_name}"
            schema_result = self.connection.execute(schema_query).fetchall()

            columns = []
            for row in schema_result:
                columns.append({
                    "name": row[0],
                    "type": row[1],
                    "null": row[2] == "YES"
                })

            # Get row count
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            row_count = self.connection.execute(count_query).fetchone()[0]

            return {
                "table_name": table_name,
                "columns": columns,
                "row_count": row_count
            }

        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to get info for table '{table_name}': {str(e)}"
            ) from e

    def list_tables(self) -> List[str]:
        """
        List all registered tables.

        :returns: List of table names
        """
        return list(self.registered_tables.keys())

    def explain_query(self, sql: str) -> str:
        """
        Get query execution plan.

        Useful for debugging and optimization.

        :param sql: SQL query to explain
        :returns: Query execution plan as string
        """
        if not self.connection:
            raise DbtRuntimeError("DuckDB engine not connected")

        try:
            explain_sql = f"EXPLAIN {sql}"
            result = self.connection.execute(explain_sql).fetchall()
            return "\n".join(str(row[0]) for row in result)

        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to explain query: {str(e)}\nSQL: {sql}"
            ) from e
