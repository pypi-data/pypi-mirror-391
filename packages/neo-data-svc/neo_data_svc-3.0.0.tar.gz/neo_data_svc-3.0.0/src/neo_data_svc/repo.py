from pyspark.sql import SparkSession as _s

from .common import *

_APP = "NDS"
_SEP = "/"
_PATH = "://"
_SQL_SEP = ";"
_NDS_PREFIX = "spark"
_HADOOP = f"{_NDS_PREFIX}.hadoop"
_SQL = f"{_NDS_PREFIX}.sql"
_BRICKS = f"{_NDS_PREFIX}.databricks"
_CORES = f"{_NDS_PREFIX}.cores.max"
_FMT = "delta"
NDS_LOG_NAME = "_delta_log"
_builder = _s.builder
_instance = None


def NDS_get_table(file):
    return file.rstrip(_SEP).split(_SEP)[-1].lower()


def NDS_is_table_or_db(s: str):
    return _PATH not in s


def NDS_check_table(statement):
    if _SQL_SEP in statement:
        raise ValueError("Illegal statement: {}".format(statement))


def NDS_write(data, file, table):
    return (data
            .write
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .option("path", file)
            .format(_FMT)
            .saveAsTable(table))


def NDS_get_instance():
    global _builder
    global _instance

    if not _instance:
        for f in [_add_name, _add_sql, _add_hadoop,  _add_bricks, _add_hive]:
            _builder = f(_builder)
        _instance = _builder
    return _instance


def _add_hive(b):
    return (b
            .enableHiveSupport()
            .getOrCreate()
            )


def _add_name(b):
    return (b
            .appName(_APP)
            )


def _add_sql(b):
    return (b
            .config(f"{_SQL}.warehouse.dir", "s3a://emdm/main/repo")
            .config(f"{_SQL}.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config(f"{_SQL}.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config(f"{_SQL}.hive.convertMetastoreParquet", "false")
            .config(f"{_SQL}.sources.default", _FMT)
            )


def _add_hadoop(b):
    return (b
            .config(f"{_HADOOP}.fs.defaultFS", "s3a://emdm/main")
            .config(f"{_HADOOP}.javax.jdo.option.ConnectionDriverName", "org.postgresql.Driver")
            .config(f"{_HADOOP}.javax.jdo.option.ConnectionURL", NDS_get_v("ConnectionURL", "jdbc:postgresql://localhost:5432/emdm_hd"))
            .config(f"{_HADOOP}.javax.jdo.option.ConnectionUserName", NDS_get_v("ConnectionUserName", "test"))
            .config(f"{_HADOOP}.javax.jdo.option.ConnectionPassword", NDS_get_v("ConnectionPassword", "test"))
            .config(f"{_HADOOP}.datanucleus.schema.autoCreateTables", "true")
            .config(f"{_HADOOP}.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .config(f"{_HADOOP}.fs.s3a.endpoint", NDS_get_v("endpoint", "http://localhost:8000"))
            .config(f"{_HADOOP}.fs.s3a.access.key", "AKIAJ42ZO5QXOBRWPUFQ")
            .config(f"{_HADOOP}.fs.s3a.secret.key", "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")
            .config(f"{_HADOOP}.fs.s3a.path.style.access", "true")
            )


def _add_bricks(b):
    return (b
            .config(f"{_BRICKS}.hive.metastore.schema.syncOnWrite", "true")
            .config(f"{_BRICKS}.delta.logRetentionDuration", "interval 1 days")
            .config(f"{_BRICKS}.delta.schema.autoMerge.enabled", "true")
            .config(f"{_BRICKS}.delta.properties.defaults.columnMapping.mode", "name")
            .config(f"{_BRICKS}.delta.optimizeWrite.enabled", "true")
            .config(f"{_BRICKS}.delta.autoCompact.maxFileSize", "134217728")
            .config(f"{_CORES}", NDS_get_v("Cores", 3))
            )
