"""
DVT Compute Engines

This module provides ephemeral compute engines for federated query execution.
Compute engines are used ONLY for processing, never for materialization.
"""

from dbt.compute.engines.duckdb_engine import DuckDBEngine
from dbt.compute.engines.spark_engine import SparkEngine

__all__ = ["DuckDBEngine", "SparkEngine"]
