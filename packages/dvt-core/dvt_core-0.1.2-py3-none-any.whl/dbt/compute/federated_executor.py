"""
Federated Query Executor

Orchestrates multi-source query execution using compute engines.
This is the core component that enables DVT's data virtualization capabilities.

Execution flow:
1. Identify all source tables/models from compiled SQL
2. Use adapters to read data from each source → PyArrow
3. Load Arrow tables into compute engine (DuckDB/Spark)
4. Execute model SQL in compute engine
5. Return results as PyArrow Table
6. Use target adapter to materialize results

Key principle: Adapters for I/O only, compute engines for processing only.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

import pyarrow as pa

from dbt.adapters.base import BaseAdapter
from dbt.compute.arrow_bridge import adapter_to_arrow, arrow_to_adapter
from dbt.compute.engines.duckdb_engine import DuckDBEngine
from dbt.compute.engines.spark_engine import SparkEngine
from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.graph.nodes import ManifestNode
from dbt.query_analyzer import QueryAnalysisResult
from dbt_common.exceptions import DbtRuntimeError


@dataclass
class SourceTableMetadata:
    """Metadata about a source table needed for federated execution."""

    source_id: str  # Unique ID from manifest
    connection_name: str  # Which connection to read from
    database: str  # Database name
    schema: str  # Schema name
    identifier: str  # Table name
    qualified_name: str  # Fully qualified name for SQL


@dataclass
class FederatedExecutionResult:
    """Result of federated query execution."""

    arrow_table: pa.Table  # Query results as Arrow table
    source_tables: List[SourceTableMetadata]  # Sources used
    compute_engine: str  # Engine used (duckdb/spark)
    execution_time_ms: float  # Execution time in milliseconds
    rows_read: int  # Total rows read from sources
    rows_returned: int  # Rows in result


class FederatedExecutor:
    """
    Orchestrates federated query execution across multiple data sources.

    This executor:
    1. Extracts data from multiple sources via adapters
    2. Loads data into a compute engine
    3. Executes the query
    4. Returns results as Arrow table
    """

    def __init__(
        self,
        manifest: Manifest,
        adapters: Dict[str, BaseAdapter],
        default_compute_engine: str = "duckdb"
    ):
        """
        Initialize federated executor.

        :param manifest: The dbt manifest with all nodes and sources
        :param adapters: Dict of connection_name → adapter instances
        :param default_compute_engine: Default compute engine ("duckdb" or "spark")
        """
        self.manifest = manifest
        self.adapters = adapters
        self.default_compute_engine = default_compute_engine

    def execute(
        self,
        node: ManifestNode,
        analysis_result: QueryAnalysisResult,
        compute_engine_override: Optional[str] = None,
        spark_config: Optional[Dict[str, str]] = None
    ) -> FederatedExecutionResult:
        """
        Execute a node using federated query processing.

        :param node: The compiled node to execute
        :param analysis_result: Query analysis result
        :param compute_engine_override: Override compute engine choice
        :param spark_config: Spark configuration (if using Spark)
        :returns: FederatedExecutionResult with query results
        :raises DbtRuntimeError: If execution fails
        """
        import time
        start_time = time.time()

        # Determine compute engine
        compute_engine = compute_engine_override or analysis_result.user_override or self.default_compute_engine

        # Extract source table metadata
        source_tables = self._extract_source_tables(analysis_result)

        # Create compute engine
        if compute_engine == "duckdb":
            engine = DuckDBEngine()
        elif compute_engine == "spark" or compute_engine.startswith("spark:"):
            # Parse spark mode (embedded or external cluster)
            if compute_engine == "spark":
                engine = SparkEngine(mode="embedded")
            else:
                # External cluster: spark:cluster_name
                engine = SparkEngine(mode="external", spark_config=spark_config or {})
        else:
            raise DbtRuntimeError(f"Unknown compute engine: {compute_engine}")

        try:
            with engine:
                # Step 1: Load source data into compute engine
                total_rows_read = self._load_sources(engine, source_tables, analysis_result)

                # Step 2: Execute query in compute engine
                compiled_sql = node.compiled_code if hasattr(node, 'compiled_code') else node.raw_code
                result_table = engine.execute_query(compiled_sql)

                # Calculate execution time
                execution_time_ms = (time.time() - start_time) * 1000

                return FederatedExecutionResult(
                    arrow_table=result_table,
                    source_tables=source_tables,
                    compute_engine=compute_engine,
                    execution_time_ms=execution_time_ms,
                    rows_read=total_rows_read,
                    rows_returned=len(result_table)
                )

        except Exception as e:
            raise DbtRuntimeError(
                f"Federated execution failed for node {node.unique_id}: {str(e)}"
            ) from e

    def _extract_source_tables(
        self,
        analysis_result: QueryAnalysisResult
    ) -> List[SourceTableMetadata]:
        """
        Extract metadata for all source tables referenced in the query.

        :param analysis_result: Query analysis result
        :returns: List of SourceTableMetadata
        """
        source_tables = []

        for source_id in analysis_result.source_refs:
            source = self.manifest.sources.get(source_id)
            if not source:
                raise DbtRuntimeError(f"Source {source_id} not found in manifest")

            # Get connection name
            connection_name = source.connection if hasattr(source, 'connection') else None
            if not connection_name:
                raise DbtRuntimeError(
                    f"Source {source_id} does not have a connection specified. "
                    "DVT requires all sources to specify a connection."
                )

            # Build qualified name for SQL
            qualified_name = f"{source.database}.{source.schema}.{source.identifier}"

            metadata = SourceTableMetadata(
                source_id=source_id,
                connection_name=connection_name,
                database=source.database,
                schema=source.schema,
                identifier=source.identifier,
                qualified_name=qualified_name
            )

            source_tables.append(metadata)

        return source_tables

    def _load_sources(
        self,
        engine: Any,  # DuckDBEngine or SparkEngine
        source_tables: List[SourceTableMetadata],
        analysis_result: QueryAnalysisResult
    ) -> int:
        """
        Load all source tables into the compute engine.

        :param engine: Compute engine instance
        :param source_tables: List of source table metadata
        :param analysis_result: Query analysis result
        :returns: Total number of rows loaded
        """
        total_rows = 0

        for source_meta in source_tables:
            # Get adapter for this source's connection
            adapter = self.adapters.get(source_meta.connection_name)
            if not adapter:
                raise DbtRuntimeError(
                    f"No adapter found for connection '{source_meta.connection_name}'"
                )

            # Build SELECT query to read from source
            select_sql = f"SELECT * FROM {source_meta.qualified_name}"

            # Execute via adapter and convert to Arrow
            arrow_table, response = adapter_to_arrow(
                adapter=adapter,
                sql=select_sql,
                connection_name=source_meta.connection_name
            )

            # Register table in compute engine
            # Use a normalized table name (compute engines may not support dots in names)
            table_alias = self._get_table_alias(source_meta)
            engine.register_arrow_table(arrow_table, table_alias)

            total_rows += len(arrow_table)

        return total_rows

    def _get_table_alias(self, source_meta: SourceTableMetadata) -> str:
        """
        Generate a safe table alias for the compute engine.

        Compute engines may not support dots or special characters in table names,
        so we create a normalized alias.

        :param source_meta: Source table metadata
        :returns: Safe table alias
        """
        # Extract source name and table name from source_id
        # source_id format: source.{project}.{source_name}.{table_name}
        parts = source_meta.source_id.split('.')
        if len(parts) >= 4:
            source_name = parts[2]
            table_name = parts[3]
            return f"{source_name}_{table_name}"
        else:
            # Fallback: use identifier
            return source_meta.identifier

    def materialize_result(
        self,
        result: FederatedExecutionResult,
        target_adapter: BaseAdapter,
        target_table: str,
        mode: str = "create"
    ) -> Any:
        """
        Materialize federated query results to target database.

        :param result: Federated execution result
        :param target_adapter: Adapter to use for materialization
        :param target_table: Target table name (qualified)
        :param mode: Write mode ('create', 'append', 'replace')
        :returns: AdapterResponse from write operation
        """
        return arrow_to_adapter(
            adapter=target_adapter,
            arrow_table=result.arrow_table,
            target_table=target_table,
            mode=mode
        )

    def explain_execution(
        self,
        node: ManifestNode,
        analysis_result: QueryAnalysisResult
    ) -> str:
        """
        Generate an execution plan explanation for a federated query.

        Useful for debugging and optimization.

        :param node: The node to explain
        :param analysis_result: Query analysis result
        :returns: Human-readable execution plan
        """
        source_tables = self._extract_source_tables(analysis_result)

        plan_parts = [
            "=== DVT Federated Execution Plan ===",
            f"Node: {node.unique_id}",
            f"Compute Engine: {self.default_compute_engine}",
            "",
            "Data Sources:",
        ]

        for i, source_meta in enumerate(source_tables, 1):
            plan_parts.append(
                f"  {i}. {source_meta.qualified_name} "
                f"(connection: {source_meta.connection_name})"
            )

        plan_parts.extend([
            "",
            "Execution Steps:",
            "  1. Extract data from each source via adapters → PyArrow",
            f"  2. Load {len(source_tables)} table(s) into {self.default_compute_engine}",
            "  3. Execute query in compute engine",
            "  4. Return results as PyArrow Table",
            "  5. Materialize to target via adapter",
            "",
            f"Strategy: {analysis_result.strategy.upper()}",
            f"Reason: {analysis_result.reason}"
        ])

        return "\n".join(plan_parts)


class SourceRewriter:
    """
    Rewrites SQL queries to use compute engine table aliases.

    When sources are loaded into compute engines, they may be registered with
    different names (aliases). This class rewrites the SQL to use those aliases.
    """

    @staticmethod
    def rewrite_sources(
        sql: str,
        source_mapping: Dict[str, str]
    ) -> str:
        """
        Rewrite SQL to use compute engine table aliases.

        :param sql: Original SQL with qualified source names
        :param source_mapping: Dict of qualified_name → alias
        :returns: Rewritten SQL
        """
        rewritten = sql

        # Replace each qualified name with its alias
        for qualified_name, alias in source_mapping.items():
            # Match qualified name (database.schema.table)
            pattern = re.compile(
                rf'\b{re.escape(qualified_name)}\b',
                re.IGNORECASE
            )
            rewritten = pattern.sub(alias, rewritten)

        return rewritten
