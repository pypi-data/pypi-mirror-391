import logging
import re

from delta.tables import *
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

from .common import *
from .repo import *

_logger = logging.getLogger(__name__)
S = NDS_get_instance()
Q = S.sql
_DB = "emdm"
_FILE = "s3a://emdm/{}/table"
_JVM = S._jvm
_JSC = S._jsc
_CATA = S.catalog


def NDS_import_data(data):
    assert S is not None
    return data if hasattr(data, "schema") else S.createDataFrame(data)


def NDS_exist_table(file):
    try:
        fs = _JVM.org.apache.hadoop.fs.FileSystem.get(
            _JSC.hadoopConfiguration())
        return fs.exists(_JVM.org.apache.hadoop.fs.Path(f"{file}/{NDS_LOG_NAME}"))
    except Exception:
        return False


def NDS_describe_table(table):
    assert S is not None and NDS_is_table_or_db(table) is True
    data = S.table(table)
    return [{"col_name": f.name,
             "data_type": str(f.dataType),
             "comment": f.metadata.get("comment", "")}
            for f in data.schema.fields
            ]


def NDS_list_tables(db):
    assert NDS_is_table_or_db(db) is True
    return [{"tableName": f"{db}.{t.name}"} for t in _CATA.listTables(db)]


def NDS_query_table(table, fields, body):
    sqlwhere: str = body.get("sqlwhere", "").strip()
    pageNo: int = int(body.get("pageNo", 1))
    pageSize: int = int(body.get("pageSize", 10))
    where_clause = ""

    if not fields or fields.strip() == "*":
        select_fields = "*"

    if sqlwhere:
        if ";" in sqlwhere or "drop" in sqlwhere.lower():
            raise ValueError("非法片段")
        where_clause = f"WHERE {sqlwhere}"

    base_sql = f"SELECT {select_fields} FROM {table} {where_clause}"
    NDS_check_table(base_sql)
    total_sql = f"SELECT COUNT(*) AS cnt FROM ({base_sql}) AS t"
    total = Q(total_sql).collect()[0]["cnt"]

    offset, limit = (pageNo - 1) * pageSize, pageSize
    rows = Q(f""" {base_sql} LIMIT {limit} OFFSET {offset} """).collect()
    return {
        "rows": [r.asDict() for r in rows],
        "total": total
    }


def NDS_execute(data=None, keys=None, branch="main", file="", db=_DB):
    if not data:
        return

    if not file:
        file = _FILE.format(branch)

    table = NDS_get_table(file)
    table = f"{db}.{table}"
    data = NDS_import_data(data)
    _logger.debug(data.head())

    try:
        if not _CATA.databaseExists(db):
            _CATA.createDatabase(db)
        _CATA.setCurrentDatabase(db)

        _logger.info(f"file: {file}")
        if keys and NDS_exist_table(file):
            _logger.info(f"keys: {keys}")
            condition = " AND ".join([f"d.{k} = s.{k}" for k in keys])
            assert S is not None
            delta_table = DeltaTable.forPath(S, file)
            (delta_table.alias("d")
             .merge(data.alias("s"), condition)
             .whenMatchedUpdateAll()
             .whenNotMatchedInsertAll()
             .execute())
            _CATA.refreshTable(table)
            return table

        Q(f"DROP TABLE IF EXISTS {table}")
        NDS_write(data, file, table)

        return table
    except Exception as e:
        _logger.exception("error")
