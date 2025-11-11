"""
PyArrow Integration Bridge

This module provides conversion utilities between dbt adapters and PyArrow format.
PyArrow serves as the universal data format for efficient data transfer between
heterogeneous data sources and compute engines.

Architecture:
- Adapters read/write data (I/O only)
- PyArrow is the intermediary format
- Compute engines (DuckDB/Spark) process PyArrow tables
"""

import pyarrow as pa
from typing import Any, Dict, List, Optional, Tuple
from dbt.adapters.base import BaseAdapter
from dbt.adapters.contracts.connection import AdapterResponse
from dbt_common.exceptions import DbtRuntimeError


class ArrowBridge:
    """
    Bridge between dbt adapters and PyArrow format.

    Handles type mapping and data conversion between various database systems
    and PyArrow's columnar format.
    """

    # Type mapping from common SQL types to PyArrow types
    SQL_TO_ARROW_TYPE_MAP = {
        # Integer types
        "TINYINT": pa.int8(),
        "SMALLINT": pa.int16(),
        "INTEGER": pa.int32(),
        "INT": pa.int32(),
        "BIGINT": pa.int64(),
        # Floating point types
        "REAL": pa.float32(),
        "FLOAT": pa.float32(),
        "DOUBLE": pa.float64(),
        "DOUBLE PRECISION": pa.float64(),
        # Decimal/Numeric types
        "DECIMAL": pa.decimal128(38, 9),  # Default precision
        "NUMERIC": pa.decimal128(38, 9),
        # String types
        "VARCHAR": pa.string(),
        "CHAR": pa.string(),
        "TEXT": pa.string(),
        "STRING": pa.string(),
        # Date/Time types
        "DATE": pa.date32(),
        "TIMESTAMP": pa.timestamp("us"),
        "TIMESTAMPTZ": pa.timestamp("us", tz="UTC"),
        "TIME": pa.time64("us"),
        # Boolean
        "BOOLEAN": pa.bool_(),
        "BOOL": pa.bool_(),
        # Binary
        "BINARY": pa.binary(),
        "VARBINARY": pa.binary(),
        "BYTEA": pa.binary(),
        # JSON (stored as string for portability)
        "JSON": pa.string(),
        "JSONB": pa.string(),
        # Array (stored as string for portability)
        "ARRAY": pa.string(),
    }

    @staticmethod
    def infer_arrow_type(sql_type: str, precision: Optional[int] = None, scale: Optional[int] = None) -> pa.DataType:
        """
        Infer PyArrow type from SQL type string.

        :param sql_type: SQL type name (e.g., 'VARCHAR', 'DECIMAL')
        :param precision: Precision for numeric types
        :param scale: Scale for numeric types
        :returns: PyArrow DataType
        """
        # Normalize type name
        sql_type_upper = sql_type.upper().strip()

        # Handle parametrized types
        if "(" in sql_type_upper:
            base_type = sql_type_upper.split("(")[0].strip()
            sql_type_upper = base_type

        # Handle DECIMAL/NUMERIC with precision/scale
        if sql_type_upper in ("DECIMAL", "NUMERIC") and precision is not None:
            scale = scale or 0
            return pa.decimal128(precision, scale)

        # Look up in mapping
        if sql_type_upper in ArrowBridge.SQL_TO_ARROW_TYPE_MAP:
            return ArrowBridge.SQL_TO_ARROW_TYPE_MAP[sql_type_upper]

        # Default to string for unknown types
        return pa.string()

    @staticmethod
    def build_arrow_schema(column_names: List[str], column_types: List[str]) -> pa.Schema:
        """
        Build PyArrow schema from column names and SQL types.

        :param column_names: List of column names
        :param column_types: List of SQL type strings
        :returns: PyArrow Schema
        """
        fields = []
        for name, sql_type in zip(column_names, column_types):
            arrow_type = ArrowBridge.infer_arrow_type(sql_type)
            fields.append(pa.field(name, arrow_type))

        return pa.schema(fields)


def adapter_to_arrow(
    adapter: BaseAdapter,
    sql: str,
    connection_name: Optional[str] = None
) -> Tuple[pa.Table, AdapterResponse]:
    """
    Execute SQL query via adapter and convert results to PyArrow Table.

    This is the primary interface for reading data from a database via an adapter
    and converting it to Arrow format for compute layer processing.

    :param adapter: The dbt adapter to use for query execution
    :param sql: SQL query to execute
    :param connection_name: Optional connection name for adapter
    :returns: Tuple of (PyArrow Table, AdapterResponse with metadata)
    :raises DbtRuntimeError: If query execution or conversion fails
    """
    try:
        # Execute query via adapter
        # The adapter's execute() method returns rows and metadata
        response, table = adapter.execute(sql, auto_begin=False, fetch=True)

        if table is None:
            # No results (e.g., DDL statement)
            return pa.table({}), response

        # Extract column names and data
        # table is typically an agate.Table or similar
        column_names = table.column_names
        rows = list(table.rows)

        if not rows:
            # Empty result set - infer schema from column names only
            schema = pa.schema([pa.field(name, pa.string()) for name in column_names])
            return pa.table({}, schema=schema), response

        # Convert rows to columnar format
        columns_data = {name: [] for name in column_names}
        for row in rows:
            for name, value in zip(column_names, row):
                columns_data[name].append(value)

        # Create PyArrow table
        # PyArrow will infer types from Python values
        arrow_table = pa.table(columns_data)

        return arrow_table, response

    except Exception as e:
        raise DbtRuntimeError(
            f"Failed to convert adapter query results to Arrow format: {str(e)}"
        ) from e


def arrow_to_adapter(
    adapter: BaseAdapter,
    arrow_table: pa.Table,
    target_table: str,
    connection_name: Optional[str] = None,
    mode: str = "create"
) -> AdapterResponse:
    """
    Convert PyArrow Table to adapter format and write to database.

    This is the primary interface for writing compute layer results back to
    a database via an adapter.

    :param adapter: The dbt adapter to use for writing
    :param arrow_table: PyArrow Table with data to write
    :param target_table: Target table name (qualified: schema.table)
    :param connection_name: Optional connection name for adapter
    :param mode: Write mode - 'create', 'append', or 'replace'
    :returns: AdapterResponse with write metadata
    :raises DbtRuntimeError: If conversion or write fails
    """
    try:
        # Convert Arrow table to list of rows
        # This is adapter-agnostic
        column_names = arrow_table.column_names
        rows = []

        # Convert to Python objects for adapter consumption
        for batch in arrow_table.to_batches():
            for i in range(len(batch)):
                row = tuple(batch.column(j)[i].as_py() for j in range(len(column_names)))
                rows.append(row)

        # Generate appropriate SQL based on mode
        if mode == "create":
            # Generate CREATE TABLE from arrow schema
            col_defs = []
            for field in arrow_table.schema:
                # Map Arrow type back to SQL type (adapter-specific)
                sql_type = _arrow_type_to_sql(field.type, adapter.type())
                col_defs.append(f"{field.name} {sql_type}")

            create_sql = f"CREATE TABLE {target_table} ({', '.join(col_defs)})"
            response = adapter.execute(create_sql, auto_begin=True, fetch=False)

        elif mode == "replace":
            # DROP and CREATE
            drop_sql = f"DROP TABLE IF EXISTS {target_table}"
            adapter.execute(drop_sql, auto_begin=True, fetch=False)

            col_defs = []
            for field in arrow_table.schema:
                sql_type = _arrow_type_to_sql(field.type, adapter.type())
                col_defs.append(f"{field.name} {sql_type}")

            create_sql = f"CREATE TABLE {target_table} ({', '.join(col_defs)})"
            response = adapter.execute(create_sql, auto_begin=True, fetch=False)

        # Insert data (for all modes)
        if rows:
            # Use adapter's bulk insert if available, otherwise batch inserts
            placeholders = ", ".join(["%s"] * len(column_names))
            insert_sql = f"INSERT INTO {target_table} VALUES ({placeholders})"

            # Batch insert for performance
            batch_size = 1000
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                adapter.execute_batch(insert_sql, batch)

        return response

    except Exception as e:
        raise DbtRuntimeError(
            f"Failed to write Arrow data via adapter: {str(e)}"
        ) from e


def _arrow_type_to_sql(arrow_type: pa.DataType, adapter_type: str) -> str:
    """
    Convert PyArrow type to SQL type string.

    This is adapter-specific and provides best-effort conversion.

    :param arrow_type: PyArrow DataType
    :param adapter_type: Adapter type (e.g., 'postgres', 'snowflake')
    :returns: SQL type string
    """
    # Type mapping from Arrow to SQL
    type_id = arrow_type.id

    # Common mappings
    if pa.types.is_integer(arrow_type):
        if arrow_type == pa.int8():
            return "SMALLINT"
        elif arrow_type == pa.int16():
            return "SMALLINT"
        elif arrow_type == pa.int32():
            return "INTEGER"
        elif arrow_type == pa.int64():
            return "BIGINT"

    elif pa.types.is_floating(arrow_type):
        if arrow_type == pa.float32():
            return "REAL"
        elif arrow_type == pa.float64():
            return "DOUBLE PRECISION"

    elif pa.types.is_decimal(arrow_type):
        decimal_type = arrow_type
        return f"DECIMAL({decimal_type.precision}, {decimal_type.scale})"

    elif pa.types.is_string(arrow_type) or pa.types.is_unicode(arrow_type):
        return "TEXT"

    elif pa.types.is_boolean(arrow_type):
        return "BOOLEAN"

    elif pa.types.is_date(arrow_type):
        return "DATE"

    elif pa.types.is_timestamp(arrow_type):
        if arrow_type.tz:
            return "TIMESTAMPTZ"
        else:
            return "TIMESTAMP"

    elif pa.types.is_time(arrow_type):
        return "TIME"

    elif pa.types.is_binary(arrow_type):
        # Adapter-specific binary type
        if adapter_type in ("postgres", "redshift"):
            return "BYTEA"
        else:
            return "VARBINARY"

    # Default to TEXT for unknown types
    return "TEXT"
