"""
Spark Compute Engine

Provides Spark integration for large-scale federated query execution.
Supports both embedded PySpark (in-process) and external Spark clusters.

Key characteristics:
- Scalable to large datasets
- Distributed processing
- Can connect to external Spark clusters
- Excellent Arrow integration via Arrow-optimized Spark
- No materialization (ephemeral only)
"""

import pyarrow as pa
from typing import Any, Dict, List, Optional
from dbt_common.exceptions import DbtRuntimeError

try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql.types import StructType
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkSession = None
    DataFrame = None


class SparkEngine:
    """
    Ephemeral Spark compute engine for federated query execution.

    Supports two modes:
    1. Embedded: Creates local PySpark session (in-process)
    2. External: Connects to existing Spark cluster (via compute.yml)

    All data is loaded from PyArrow tables and results returned as PyArrow tables.
    """

    def __init__(
        self,
        mode: str = "embedded",
        spark_config: Optional[Dict[str, str]] = None,
        app_name: str = "DVT-Compute"
    ):
        """
        Initialize Spark engine.

        :param mode: 'embedded' for local Spark, 'external' for cluster
        :param spark_config: Spark configuration dict (master, deploy-mode, etc.)
        :param app_name: Spark application name
        :raises DbtRuntimeError: If PySpark not available
        """
        if not PYSPARK_AVAILABLE:
            raise DbtRuntimeError(
                "PySpark is not available. Install it with: pip install pyspark"
            )

        self.mode = mode
        self.spark_config = spark_config or {}
        self.app_name = app_name
        self.spark: Optional[SparkSession] = None
        self.registered_tables: Dict[str, str] = {}

    def __enter__(self):
        """Context manager entry - initialize Spark session."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop Spark session."""
        self.close()

    def connect(self) -> None:
        """
        Create Spark session.

        For embedded mode, creates local Spark session.
        For external mode, connects to cluster specified in config.
        """
        try:
            builder = SparkSession.builder.appName(self.app_name)

            if self.mode == "embedded":
                # Local mode configuration
                builder = builder.master("local[*]")
                builder = builder.config("spark.driver.memory", "4g")
                builder = builder.config("spark.sql.execution.arrow.pyspark.enabled", "true")
                builder = builder.config("spark.sql.execution.arrow.pyspark.fallback.enabled", "true")

            elif self.mode == "external":
                # External cluster configuration
                if "master" not in self.spark_config:
                    raise DbtRuntimeError(
                        "External Spark mode requires 'master' in spark_config"
                    )
                builder = builder.master(self.spark_config["master"])

                # Apply custom config
                for key, value in self.spark_config.items():
                    if key != "master":
                        builder = builder.config(key, value)

            else:
                raise DbtRuntimeError(
                    f"Invalid Spark mode: {self.mode}. Must be 'embedded' or 'external'"
                )

            # Enable Arrow optimization
            builder = builder.config("spark.sql.execution.arrow.enabled", "true")

            # Create session
            self.spark = builder.getOrCreate()

            # Set log level to WARN to reduce noise
            self.spark.sparkContext.setLogLevel("WARN")

        except Exception as e:
            raise DbtRuntimeError(f"Failed to initialize Spark engine: {str(e)}") from e

    def close(self) -> None:
        """Stop Spark session and release resources."""
        if self.spark:
            try:
                # Only stop if embedded mode (don't stop external clusters)
                if self.mode == "embedded":
                    self.spark.stop()
            except Exception:
                pass  # Best effort cleanup
            finally:
                self.spark = None
                self.registered_tables.clear()

    def register_arrow_table(
        self,
        arrow_table: pa.Table,
        table_name: str,
        replace: bool = False
    ) -> None:
        """
        Register a PyArrow table with Spark as a temporary view.

        Uses Spark's Arrow-optimized conversion for efficient data transfer.

        :param arrow_table: PyArrow Table to register
        :param table_name: Name to use for the table in Spark
        :param replace: If True, replace existing table with same name
        :raises DbtRuntimeError: If registration fails
        """
        if not self.spark:
            raise DbtRuntimeError("Spark engine not connected")

        try:
            # Check if table already exists
            if table_name in self.registered_tables and not replace:
                raise DbtRuntimeError(
                    f"Table '{table_name}' already registered. Use replace=True to overwrite."
                )

            # Convert Arrow table to Spark DataFrame
            # This uses Arrow-optimized conversion (zero-copy where possible)
            df = self.spark.createDataFrame(arrow_table.to_pandas())

            # Register as temporary view
            if replace:
                df.createOrReplaceTempView(table_name)
            else:
                df.createTempView(table_name)

            self.registered_tables[table_name] = table_name

        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to register Arrow table '{table_name}' with Spark: {str(e)}"
            ) from e

    def execute_query(self, sql: str) -> pa.Table:
        """
        Execute SQL query and return results as PyArrow Table.

        The query can reference any tables registered via register_arrow_table().

        :param sql: SQL query to execute
        :returns: PyArrow Table with query results
        :raises DbtRuntimeError: If query execution fails
        """
        if not self.spark:
            raise DbtRuntimeError("Spark engine not connected")

        try:
            # Execute SQL query
            df = self.spark.sql(sql)

            # Convert to Arrow table using Arrow-optimized path
            # This is efficient due to Spark's Arrow integration
            arrow_table = pa.Table.from_pandas(
                df.toPandas(),
                preserve_index=False
            )

            return arrow_table

        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to execute query in Spark: {str(e)}\nSQL: {sql}"
            ) from e

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get metadata about a registered table.

        :param table_name: Name of the table
        :returns: Dictionary with table metadata (columns, row_count, etc.)
        :raises DbtRuntimeError: If table not found
        """
        if not self.spark:
            raise DbtRuntimeError("Spark engine not connected")

        if table_name not in self.registered_tables:
            raise DbtRuntimeError(f"Table '{table_name}' not registered")

        try:
            # Get DataFrame for the table
            df = self.spark.table(table_name)

            # Get schema
            columns = []
            for field in df.schema.fields:
                columns.append({
                    "name": field.name,
                    "type": str(field.dataType),
                    "nullable": field.nullable
                })

            # Get row count
            row_count = df.count()

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
        if not self.spark:
            raise DbtRuntimeError("Spark engine not connected")

        try:
            df = self.spark.sql(sql)
            # Get extended explain with cost model and optimizations
            return df._jdf.queryExecution().toString()

        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to explain query: {str(e)}\nSQL: {sql}"
            ) from e

    def cache_table(self, table_name: str) -> None:
        """
        Cache a table in Spark memory for faster subsequent queries.

        Useful for tables that are accessed multiple times.

        :param table_name: Name of the table to cache
        :raises DbtRuntimeError: If table not found or caching fails
        """
        if not self.spark:
            raise DbtRuntimeError("Spark engine not connected")

        if table_name not in self.registered_tables:
            raise DbtRuntimeError(f"Table '{table_name}' not registered")

        try:
            self.spark.catalog.cacheTable(table_name)
        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to cache table '{table_name}': {str(e)}"
            ) from e

    def uncache_table(self, table_name: str) -> None:
        """
        Remove a table from Spark memory cache.

        :param table_name: Name of the table to uncache
        """
        if self.spark and table_name in self.registered_tables:
            try:
                self.spark.catalog.uncacheTable(table_name)
            except Exception:
                pass  # Best effort
