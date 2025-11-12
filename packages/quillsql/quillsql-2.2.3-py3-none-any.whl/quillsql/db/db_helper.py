from quillsql.db.postgres import (
    format_postgres,
    connect_to_postgres,
    get_schema_column_info_postgres,
    get_tables_by_schema_postgres,
    run_query_postgres,
    disconnect_from_postgres,
)
from quillsql.db.bigquery import (
    format_bigquery_config,
    connect_to_bigquery,
    get_schema_column_info_big_query,
    get_tables_by_schema_big_query,
    run_query_big_query,
)


def get_db_credentials(database_type, connection_string):
    if database_type.lower() == "postgresql":
        return format_postgres(connection_string)
    elif database_type.lower() == "bigquery":
        return format_bigquery_config(connection_string)
    return {}


def connect_to_db(database_type, config, using_connection_string):
    if database_type.lower() == "postgresql":
        return connect_to_postgres(config, using_connection_string)
    elif database_type.lower() == "bigquery":
        return connect_to_bigquery(config, using_connection_string)
    return None


def run_query_by_db(database_type, query, connection):
    if database_type.lower() == "postgresql":
        return run_query_postgres(query, connection)
    elif database_type.lower() == "bigquery":
        return run_query_big_query(query, connection)
    return None


def disconnect_from_db(database_type, connection):
    if database_type.lower() == "postgresql":
        return disconnect_from_postgres(connection)
    return None


def get_schema_tables_by_db(database_type, connection, schema_name):
    if database_type.lower() == "postgresql":
        return get_tables_by_schema_postgres(connection, schema_name)
    elif database_type.lower() == "bigquery":
        return get_tables_by_schema_big_query(connection, schema_name)
    return None


def get_schema_column_info_by_db(database_type, connection, schema_name, table_names):
    if database_type.lower() == "postgresql":
        return get_schema_column_info_postgres(connection, schema_name, table_names)
    elif database_type.lower() == "bigquery":
        return get_schema_column_info_big_query(connection, schema_name, table_names)
    return None
