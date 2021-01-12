import datetime
import logging
import os
import pandas as pd

from pathlib import Path

from whale.utils import paths
from whale.utils.sql import template_query
from whale.task import WhaleTask
from whale.loader.whale_loader import WhaleLoader
from whale.models.connection_config import ConnectionConfigSchema
from whale.utils import copy_manifest, get_table_info_from_path, transfer_manifest
from whale.utils.parsers import (
    find_blocks_and_process,
    sections_from_markdown,
    markdown_from_sections,
    UGC_SECTION,
)
from whale.utils.config import get_connection, read_connections

from whale.utils.extractor_wrappers import (
    configure_bigquery_extractors,
    configure_spanner_extractors,
    configure_glue_extractors,
    configure_hive_metastore_extractors,
    configure_neo4j_extractors,
    configure_postgres_extractors,
    configure_presto_extractors,
    configure_redshift_extractors,
    configure_snowflake_extractors,
    configure_splice_machine_extractors,
    configure_unscoped_sqlalchemy_engine,
    run_build_script,
)

LOGGER = logging.getLogger(__name__)
EXECUTION_FLAG = f"\n--!wh-execute\n"


def execute_markdown_sql_blocks(filepath: str):
    """
    Executes all sql, denoted by ```sql, within the file `filepath`, and
    destructively reinserts the results beneath the definition.

    Note: duplicate queries will be ignored.
    """

    RESULTS_HEADER = f"/* results:{datetime.datetime.now()}"

    database, _, _, _ = get_table_info_from_path(filepath)
    sections = sections_from_markdown(filepath)
    print("SECTIONS:", sections)
    ugc_blob = sections[UGC_SECTION]

    def isolate_sql_from_results(block):
        splits = block.split(EXECUTION_FLAG)
        return "\n".join(splits)

    def execute_and_append(block):
        sql = isolate_sql_from_results(block)
        results = run(sql, warehouse_name=database)
        tabulated_results = results.to_string()
        formatted_block = f"{sql}\n{RESULTS_HEADER}\n{tabulated_results}\n*/"
        return formatted_block

    if EXECUTION_FLAG in ugc_blob:
        ugc_blob = find_blocks_and_process(ugc_blob, execute_and_append)
        sections[UGC_SECTION] = ugc_blob
        new_markdown_blob = markdown_from_sections(sections)

        with open(filepath, "w") as f:
            f.write(new_markdown_blob)
    elif EXECUTION_FLAG.strip() in ugc_blob:
        LOGGER.warning(f"{EXECUTION_FLAG.strip()} must be on its own line.")


def pull():
    """
    Pulls down all metadata & metrics from user-defined warehouse connections in ~/.whale/config/connections.yaml.
    """
    for path in [
        paths.CONFIG_DIR,
        paths.LOGS_DIR,
        paths.MANIFEST_DIR,
        paths.METADATA_PATH,
        paths.METRICS_PATH,
    ]:
        Path(path).mkdir(parents=True, exist_ok=True)

    raw_connection_dicts = read_connections()

    # Create a manifest
    # If another ETL job is running, put the manifest elsewhere
    tmp_manifest_path = paths.TMP_MANIFEST_PATH
    i = 0
    while os.path.exists(tmp_manifest_path):
        tmp_manifest_path = os.path.join(
            paths.BASE_DIR, "manifests/tmp_manifest_" + str(i) + ".txt"
        )
        i += 1

    for raw_connection_dict in raw_connection_dicts:
        connection = ConnectionConfigSchema(**raw_connection_dict)

        metadata_source_dict = {
            "bigquery": configure_bigquery_extractors,
            "spanner": configure_spanner_extractors,
            "glue": configure_glue_extractors,
            "hivemetastore": configure_hive_metastore_extractors,
            "neo4j": configure_neo4j_extractors,
            "postgres": configure_postgres_extractors,
            "presto": configure_presto_extractors,
            "redshift": configure_redshift_extractors,
            "snowflake": configure_snowflake_extractors,
            "splicemachine": configure_splice_machine_extractors,
        }

        if connection.metadata_source == "build_script":
            run_build_script(connection)
            break
        else:
            configurer = metadata_source_dict[connection.metadata_source]
            extractors, conf = configurer(connection)

        manifest_key = "loader.whale.tmp_manifest_path"
        conf.put("loader.whale.database_name", connection.name)
        conf.put(manifest_key, tmp_manifest_path)

        for i, extractor in enumerate(extractors):
            is_metadata_extractor = i == 0
            task = WhaleTask(
                extractor=extractor,
                loader=WhaleLoader(),
            )
            task.init(conf)

            # Enable try except for non-metadata extractors
            # No need to update the manifest for other extractors
            if is_metadata_extractor:
                task.run()
                task.save_stats()
                conf.pop(manifest_key)
                copy_manifest(tmp_manifest_path)
            else:
                try:
                    task.run()
                except Exception as e:
                    LOGGER.warning(e)
                    LOGGER.warning(f"Skipping {type(extractor)}.")

    transfer_manifest(tmp_manifest_path)


def run(sql, warehouse_name=None):
    """
    Runs sql queries against warehouse_name defined in ~/.whale/config/connections.yaml.
    If no warehouse_name is given, the first is used.
    """
    connection_dict = get_connection(warehouse_name=warehouse_name)
    connection = ConnectionConfigSchema(**connection_dict)
    engine, conf = configure_unscoped_sqlalchemy_engine(connection)
    engine.init(conf)
    sql = template_query(sql, connection_name=connection.name)
    LOGGER.info(f"Templated query:\n{sql}")

    result = engine.execute(sql, has_header=True)
    headers = next(result)
    table = list(result)
    df = pd.DataFrame(table, columns=headers)
    return df
