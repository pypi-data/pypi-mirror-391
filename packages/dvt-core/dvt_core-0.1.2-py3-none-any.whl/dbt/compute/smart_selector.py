"""
Smart Compute Engine Selector

Automatically selects the optimal compute engine (DuckDB vs Spark) based on
workload characteristics when user doesn't specify a preference.

Selection criteria:
- Estimated data size
- Number of sources
- Query complexity
- Available resources
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.graph.nodes import ManifestNode
from dbt.query_analyzer import QueryAnalysisResult


@dataclass
class WorkloadEstimate:
    """Estimated workload characteristics for a query."""

    estimated_rows: int  # Estimated total rows to process
    source_count: int  # Number of source tables
    connection_count: int  # Number of different connections
    has_aggregations: bool  # Query contains GROUP BY or aggregations
    has_joins: bool  # Query contains JOIN operations
    complexity_score: float  # 0.0 to 1.0, higher = more complex

    @property
    def estimated_data_mb(self) -> float:
        """Rough estimate of data size in MB (assuming ~100 bytes/row)."""
        return (self.estimated_rows * 100) / (1024 * 1024)


class SmartComputeSelector:
    """
    Intelligently selects compute engine based on workload characteristics.

    Default thresholds:
    - Small workload (< 100MB, < 3 sources): DuckDB
    - Large workload (> 1GB, > 5 sources): Spark
    - Medium workload: DuckDB (for simplicity)
    """

    # Default thresholds (can be configured)
    DUCKDB_MAX_MB = 1000  # 1GB
    DUCKDB_MAX_SOURCES = 5
    SPARK_MIN_MB = 1000  # 1GB
    SPARK_MIN_SOURCES = 5

    def __init__(
        self,
        manifest: Manifest,
        duckdb_max_mb: Optional[int] = None,
        spark_min_mb: Optional[int] = None
    ):
        """
        Initialize smart selector.

        :param manifest: The dbt manifest
        :param duckdb_max_mb: Max data size for DuckDB (default: 1GB)
        :param spark_min_mb: Min data size to use Spark (default: 1GB)
        """
        self.manifest = manifest
        self.duckdb_max_mb = duckdb_max_mb or self.DUCKDB_MAX_MB
        self.spark_min_mb = spark_min_mb or self.SPARK_MIN_MB

    def select_engine(
        self,
        node: ManifestNode,
        analysis_result: QueryAnalysisResult
    ) -> str:
        """
        Select the optimal compute engine for a node.

        :param node: The node to execute
        :param analysis_result: Query analysis result
        :returns: "duckdb" or "spark"
        """
        # Estimate workload
        estimate = self._estimate_workload(node, analysis_result)

        # Apply selection logic
        return self._apply_selection_logic(estimate)

    def _estimate_workload(
        self,
        node: ManifestNode,
        analysis_result: QueryAnalysisResult
    ) -> WorkloadEstimate:
        """
        Estimate workload characteristics for a node.

        :param node: The node to analyze
        :param analysis_result: Query analysis result
        :returns: WorkloadEstimate
        """
        # Count sources
        source_count = len(analysis_result.source_refs)
        connection_count = len(analysis_result.source_connections)

        # Estimate row count from sources
        estimated_rows = self._estimate_row_count(analysis_result.source_refs)

        # Analyze SQL for complexity
        sql = node.compiled_code if hasattr(node, 'compiled_code') else node.raw_code
        has_aggregations = self._has_aggregations(sql)
        has_joins = self._has_joins(sql)

        # Calculate complexity score
        complexity_score = self._calculate_complexity(
            source_count=source_count,
            connection_count=connection_count,
            has_aggregations=has_aggregations,
            has_joins=has_joins
        )

        return WorkloadEstimate(
            estimated_rows=estimated_rows,
            source_count=source_count,
            connection_count=connection_count,
            has_aggregations=has_aggregations,
            has_joins=has_joins,
            complexity_score=complexity_score
        )

    def _estimate_row_count(self, source_refs: set) -> int:
        """
        Estimate total row count from source tables.

        Uses catalog metadata if available, otherwise uses heuristics.

        :param source_refs: Set of source unique_ids
        :returns: Estimated row count
        """
        total_rows = 0

        for source_id in source_refs:
            source = self.manifest.sources.get(source_id)
            if not source:
                # Unknown source, use conservative estimate
                total_rows += 100000
                continue

            # Check if we have catalog metadata with row counts
            # Note: This would come from `dbt docs generate`
            # For now, use a heuristic based on naming
            if "fact" in source.identifier.lower() or "events" in source.identifier.lower():
                # Fact tables tend to be larger
                total_rows += 1000000
            elif "dim" in source.identifier.lower() or "lookup" in source.identifier.lower():
                # Dimension tables tend to be smaller
                total_rows += 10000
            else:
                # Default estimate
                total_rows += 100000

        return total_rows

    def _has_aggregations(self, sql: str) -> bool:
        """Check if SQL contains aggregations."""
        sql_upper = sql.upper()
        return any(keyword in sql_upper for keyword in [
            " GROUP BY ",
            " SUM(",
            " COUNT(",
            " AVG(",
            " MIN(",
            " MAX(",
            " HAVING "
        ])

    def _has_joins(self, sql: str) -> bool:
        """Check if SQL contains joins."""
        sql_upper = sql.upper()
        return any(keyword in sql_upper for keyword in [
            " JOIN ",
            " INNER JOIN ",
            " LEFT JOIN ",
            " RIGHT JOIN ",
            " FULL JOIN ",
            " CROSS JOIN "
        ])

    def _calculate_complexity(
        self,
        source_count: int,
        connection_count: int,
        has_aggregations: bool,
        has_joins: bool
    ) -> float:
        """
        Calculate query complexity score (0.0 to 1.0).

        :returns: Complexity score
        """
        score = 0.0

        # Source count contributes
        score += min(source_count / 10.0, 0.3)

        # Multiple connections increases complexity
        score += min(connection_count / 5.0, 0.2)

        # Aggregations add complexity
        if has_aggregations:
            score += 0.2

        # Joins add complexity
        if has_joins:
            score += 0.3

        return min(score, 1.0)

    def _apply_selection_logic(self, estimate: WorkloadEstimate) -> str:
        """
        Apply selection logic based on workload estimate.

        :param estimate: WorkloadEstimate
        :returns: "duckdb" or "spark"
        """
        # Rule 1: Very large data → Spark
        if estimate.estimated_data_mb > self.spark_min_mb:
            return "spark"

        # Rule 2: Many sources → Spark
        if estimate.source_count > self.SPARK_MIN_SOURCES:
            return "spark"

        # Rule 3: High complexity → Spark
        if estimate.complexity_score > 0.7:
            return "spark"

        # Rule 4: Everything else → DuckDB (default)
        # DuckDB is excellent for most workloads and has lower overhead
        return "duckdb"

    def get_recommendation_reason(
        self,
        node: ManifestNode,
        analysis_result: QueryAnalysisResult
    ) -> str:
        """
        Get human-readable explanation for engine selection.

        :param node: The node
        :param analysis_result: Query analysis result
        :returns: Explanation string
        """
        estimate = self._estimate_workload(node, analysis_result)
        engine = self._apply_selection_logic(estimate)

        reasons = []

        if estimate.estimated_data_mb > self.spark_min_mb:
            reasons.append(f"Large dataset ({estimate.estimated_data_mb:.0f} MB)")

        if estimate.source_count > self.SPARK_MIN_SOURCES:
            reasons.append(f"Many sources ({estimate.source_count})")

        if estimate.complexity_score > 0.7:
            reasons.append(f"High complexity (score: {estimate.complexity_score:.2f})")

        if not reasons:
            reasons.append(f"Small/medium workload ({estimate.estimated_data_mb:.0f} MB, {estimate.source_count} sources)")

        reason_str = "; ".join(reasons)
        return f"Selected {engine.upper()}: {reason_str}"
