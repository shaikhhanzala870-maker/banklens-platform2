from pyspark.sql import SparkSession
from pyspark.sql import functions as F


from importlib import import_module

spark = SparkSession.builder.getOrCreate()

config = import_module(
    "00_setup.01_config"
)

audit_utils = import_module(
    "99_utils.audit_utils"
)

metrics_utils = import_module(
    "99_utils.metrics_utils"
)

CATALOG_NAME = config.CATALOG_NAME

BRONZE_SCHEMA = config.BRONZE_SCHEMA
SILVER_SCHEMA = config.SILVER_SCHEMA


def read_bronze_table(
    table_name: str
):

    source_table = (
        f"{CATALOG_NAME}."
        f"{BRONZE_SCHEMA}."
        f"brz_{table_name}"
    )

    print(
        f"Reading {source_table}"
    )

    df = spark.table(
        source_table
    )

    return df

def read_column_mapping(
    table_name: str
):

    metadata_table = (
        f"{CATALOG_NAME}.metadata.column_mapping"
    )

    print(
        f"Reading metadata for {table_name}"
    )

    metadata_df = (
        spark.table(
            metadata_table
        )
        .filter(
            F.col("table_name") == table_name
        )
        .filter(
            F.col("is_active") == True
        )
    )

    metadata_count = metadata_df.count()

    print(
        f"Metadata rows found = "
        f"{metadata_count}"
    )

    return metadata_df

def apply_standardization(
    df,
    table_name: str
):

    metadata_df = read_column_mapping(
        table_name
    )

    metadata_rows = (
        metadata_df.collect()
    )

    print(
        f"Applying standardization for "
        f"{table_name}"
    )

    for row in metadata_rows:

        column_name = row["column_name"]

        target_type = (
            row["target_type"]
            .upper()
        )

        format_string = (
            row["format_string"]
        )

        if column_name not in df.columns:

            print(
                f"Skipping missing column "
                f"{column_name}"
            )

            continue

        print(
            f"Converting "
            f"{column_name} -> "
            f"{target_type}"
        )

        if target_type == "STRING":

            df = df.withColumn(
                column_name,
                F.col(
                    column_name
                ).cast("string")
            )

        elif target_type == "INTEGER":

            df = df.withColumn(
                column_name,
                F.col(
                    column_name
                ).cast("double").cast("int")
            )

        elif target_type == "DECIMAL":

            df = df.withColumn(
                column_name,
                F.col(
                    column_name
                ).cast(
                    "decimal(18,2)"
                )
            )

        elif target_type == "BOOLEAN":

            df = df.withColumn(
                column_name,
                F.col(
                    column_name
                ).cast("boolean")
            )

        elif target_type == "DATE":

            df = df.withColumn(
                column_name,
                F.to_date(
                    F.col(
                        column_name
                    ),
                    format_string
                )
            )

        elif target_type == "TIMESTAMP":

            df = df.withColumn(
                column_name,
                F.to_timestamp(
                    F.col(
                        column_name
                    ),
                    format_string
                )
            )

    return df

def deduplicate_records(
    df
):

    before_count = df.count()

    df = df.dropDuplicates(
        ["_row_hash"]
    )

    after_count = df.count()

    duplicates_removed = (
        before_count - after_count
    )

    print(
        f"Duplicates removed = "
        f"{duplicates_removed}"
    )

    return (
        df,
        before_count,
        after_count,
        duplicates_removed
    )


def write_silver_table(
    df,
    table_name: str
):

    target_table = (
        f"{CATALOG_NAME}."
        f"{SILVER_SCHEMA}."
        f"slv_{table_name}"
    )

    print(
        f"Writing {target_table}"
    )

    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option(
            "overwriteSchema",
            "true"
        )
        .saveAsTable(
            target_table
        )
    )

    print(
        f"Written to {target_table}"
    )


def process_table(
    table_name: str,
    run_id: str
):

    print(
        f"Processing {table_name}"
    )

    started_at = spark.sql(
        "SELECT current_timestamp()"
    ).collect()[0][0]

    try:

        df = read_bronze_table(
            table_name
        )

        audit_utils.write_schema_change_log(
            table_name=table_name,
            day_number=0,
            current_columns=df.columns
        )

        df = apply_standardization(
            df,
            table_name
        )

        (
            df,
            source_count,
            target_count,
            duplicates_removed
        ) = deduplicate_records(
            df
        )

        write_silver_table(
            df,
            table_name
        )

        completed_at = spark.sql(
            "SELECT current_timestamp()"
        ).collect()[0][0]

        audit_utils.write_audit_log(
            run_id=run_id,
            pipeline_layer="SILVER",
            table_name=table_name,
            day_number=0,
            source_path="BRONZE_TABLE",
            started_at=started_at,
            completed_at=completed_at,
            source_record_count=source_count,
            target_record_count=target_count,
            status="SUCCESS",
            error_message=""
        )

        audit_utils.write_control_record(
            table_name=table_name,
            pipeline_layer="SILVER",
            day_number=0
        )

        processing_time_seconds = (
            completed_at - started_at
        ).total_seconds()

        duplicate_percentage = round(
            (
                duplicates_removed
                / source_count
            ) * 100,
            2
        )

        if processing_time_seconds > 0:

            rows_per_second = round(
                target_count
                / processing_time_seconds,
                2
            )

        else:

            rows_per_second = 0

        metrics_utils.write_pipeline_metrics(
            run_id=run_id,
            pipeline_layer="SILVER",
            table_name=table_name,
            status="SUCCESS",
            source_record_count=source_count,
            target_record_count=target_count,
            duplicates_removed=duplicates_removed,
            duplicate_percentage=duplicate_percentage,
            processing_time_seconds=processing_time_seconds,
            rows_per_second=rows_per_second
        )

        print(
            f"Source Rows = "
            f"{source_count}"
        )

        print(
            f"Target Rows = "
            f"{target_count}"
        )

        print(
            f"Duplicates Removed = "
            f"{duplicates_removed}"
        )

        print(
            f"Completed {table_name}"
        )

    except Exception as e:

        completed_at = spark.sql(
            "SELECT current_timestamp()"
        ).collect()[0][0]

        audit_utils.write_audit_log(
            run_id=run_id,
            pipeline_layer="SILVER",
            table_name=table_name,
            day_number=0,
            source_path="BRONZE_TABLE",
            started_at=started_at,
            completed_at=completed_at,
            source_record_count=0,
            target_record_count=0,
            status="FAILED",
            error_message=str(e)
        )

        raise e
