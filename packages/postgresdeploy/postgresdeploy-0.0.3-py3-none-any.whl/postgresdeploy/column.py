import os
import psycopg2 as pg
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging
import json
import textwrap

from .helpers import *

def create_column(conn: connection, cur: cursor, schema: str, table_name: str, col_def: str):
    try:
        column = build_column_string(col_def)

        cur.execute(sql.SQL(textwrap.dedent(
            """
            alter table {schema}.{table}
            add column {column}
            """
        )).format(
            schema=sql.Identifier(schema),
            table=sql.Identifier(table_name),
            column=sql.SQL(column)
        ))
    except Exception as e:
        raise CaughtException(e)
    
def alter_column(conn: connection, cur: cursor, schema: str, table: dict, col_def: str):
    try:
        existing_col_schema = fetch_existing_col_schema(conn, cur, schema, table, col_def)

        alter_column_not_null(conn, cur, schema, table, col_def, existing_col_schema)
        alter_column_default(conn, cur, schema, table, col_def, existing_col_schema)

    except Exception as e:
        raise CaughtException(e)
    
def fetch_existing_col_schema(conn, cur, schema, table, col_def):
    cur.execute(textwrap.dedent(
        """
        select *
        from information_schema.columns
        where table_schema = %s
        and table_name = %s
        and column_name = %s
        """
        ), [schema, table["name"], col_def["name"]]
    )
    return cur.fetchone()

def alter_column_type(conn: connection, cur: cursor, schema: str, table: dict, col_def: dict, existing_col_schema):
    if existing_col_schema["data_type"].lower() == col_def["type"].lower(): return
    query = sql.SQL(textwrap.dedent(
        """
        alter table {schema}.{table}
        alter column {column} type {col_type}
        """
    )).format(
        schema=sql.Identifier(schema), 
        table=sql.Identifier(table["name"]), 
        column=sql.SQL(col_def["name"]), 
        col_type=sql.SQL(col_def["type"])
    )
    
    using_expr = get_val_strict(col_def, "type_convert_using")
    if using_expr != None:
        query += sql.SQL("\nusing {}").format(sql.SQL(using_expr))
    
    cur.execute(query)

def alter_column_not_null(conn: connection, cur: cursor, schema: str, table: dict, col_def: dict, existing_col_schema):
    not_null = get_val_strict(col_def, "not_null", False)
    if existing_col_schema["is_nullable"].lower() == ("no" if not_null else "yes"): return
    
    pkey_columns = table["constraints"].get("primary_key", [])
    if not not_null and col_def["name"] in pkey_columns: return

    cur.execute(sql.SQL(textwrap.dedent(
        """
        alter table {schema}.{table}
        alter column {column} {action} not null;
        """
    )).format(
        schema=sql.Identifier(schema), 
        table=sql.Identifier(table["name"]), 
        column=sql.SQL(col_def["name"]), 
        action=sql.SQL("set" if not_null else "drop")
    ))

def alter_column_default(conn: connection, cur: cursor, schema: str, table: dict, col_def: dict, existing_col_schema):
    default = get_val_strict(col_def, "default")
    if default is None:
        cur.execute(sql.SQL(textwrap.dedent(
            """
            alter table {schema}.{table}
            alter column {column} drop default;
            """
        )).format(
            schema=sql.Identifier(schema), 
            table=sql.Identifier(table["name"]), 
            column=sql.SQL(col_def["name"]), 
        ))
        return

    if existing_col_schema["column_default"] == default: return

    cur.execute(sql.SQL(textwrap.dedent(
        """
        alter table {}.{}
        alter column {} set default {};
        """
    )).format(
        sql.Identifier(schema),
        sql.Identifier(table["name"]),
        sql.SQL(col_def["name"]),
        sql.Literal(default)
    ))

def drop_column(conn, cur, schema, table, column_name):
    cur.execute(sql.SQL(textwrap.dedent(
        """
        alter table {schema}.{table}
        drop column {column};
        """
    )).format(
        schema=sql.Identifier(schema), 
        table=sql.Identifier(table["name"]), 
        column=sql.SQL(column_name), 
    ))