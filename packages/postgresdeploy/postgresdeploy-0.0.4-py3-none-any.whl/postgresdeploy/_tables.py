import os
import psycopg2 as pg
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging
import json
import textwrap
from pathlib import Path
# from jsonschema import validate, ValidationError

from ._helpers import *
from ._column import *
from ._primary_key import *
from ._check_constraint import *
from ._unique_constraint import *
from ._indexes import *
from ._triggers import *
from ._functions import *

def deploy_tables(conn: connection, cur: cursor, schema_path: str):
    # todo finish validation
    # try:
    #     validate(instance=table, schema=tables_schema)
    # except Exception as e:
    #     logging.error(f"JSON validation error: {str(e)}")

    for file_path in list(Path(f"{schema_path}/tables").glob("*.json")):
        with open(file_path, "r") as file:
            table = json.loads(file.read())
        table["name"] = file_path.name.replace(".json", "")
        deploy_table(conn, cur, get_schema_from_path(schema_path), table)

def deploy_table(conn: connection, cur: cursor, schema: str, table: dict):
    try:
        cur.execute(textwrap.dedent(
            """
            select exists (
                select 1
                from information_schema.tables
                where table_schema = %s
                and table_name = %s
            )
            """
            ), [schema, table["name"]]
        )
        if not cur.fetchone()["exists"]:
            create_table(conn, cur, schema, table)
        else:
            alter_table(conn, cur, schema, table)

    except Exception as e:
        raise CaughtException(str(e))

def create_table(conn: connection, cur: cursor, schema: str, table: dict):
    try:
        columns = [build_column_string(col_def) for col_def in table["columns"]]
        cur.execute(sql.SQL(textwrap.dedent(
            """
            create table {schema}.{table} (
                {columns}
            )
            """
        )).format(
            schema=sql.Identifier(schema),
            table=sql.Identifier(table["name"]),
            columns=sql.SQL(",\n".join(columns))
        ))

        deploy_table_constraints(conn, cur, schema, table)
        deploy_table_indexes(conn, cur, schema, table)

    except Exception as e:
        raise CaughtException(str(e))

def alter_table(conn: connection, cur: cursor, schema: str, table: dict):
    try:
        cur.execute(textwrap.dedent(
            """
            select *
            from information_schema.columns
            where table_schema = %s
            and table_name = %s
            """
            ), [schema, table["name"]]
        )
        existing_columns = {
            row["column_name"]: row for row in cur.fetchall()
        }

        for col_def in table["columns"]:
            if col_def["name"] not in existing_columns.keys(): 
                create_column(conn, cur, schema, table["name"], col_def)
            else:
                existing_col_schema = fetch_existing_col_schema(conn, cur, schema, table, col_def)
                alter_column_type(conn, cur, schema, table, col_def, existing_col_schema)

        deploy_table_constraints(conn, cur, schema, table)
        deploy_table_indexes(conn, cur, schema, table)

        for col_def in table["columns"]:
            alter_column(conn, cur, schema, table, col_def)

        table_col_names = [e["name"] for e in table["columns"]]
        for existing_col_name in existing_columns.keys():
            if existing_col_name in table_col_names: continue
            drop_column(conn, cur, schema, table, existing_col_name)

    except Exception as e:
        raise CaughtException(str(e))

def deploy_table_constraints(conn: connection, cur: cursor, schema: str, table: dict):
    if "constraints" not in table.keys(): return
    deploy_primary_key(conn, cur, schema, table)
    deploy_table_checks(conn, cur, schema, table)
    deploy_table_uniques(conn, cur, schema, table)