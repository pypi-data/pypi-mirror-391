import os
import psycopg2 as pg
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging
import json
import textwrap

from .helpers import *

def deploy_table_indexes(conn: connection, cur: cursor, schema: str, table: dict):
    indexes = table.get("indexes", [])
    for index in indexes:
        deploy_table_index(conn, cur, schema, table, index)

    drop_table_indexes(conn, cur, schema, table, indexes)

def deploy_table_index(conn: connection, cur: cursor, schema: str, table: dict, index: dict):
    index_name = get_index_name(table, index)

    cur.execute(textwrap.dedent(
        """
        select exists (
            select 1
            from pg_indexes
            where schemaname = %s
            and tablename = %s
            and indexname = %s 
        )
        """
        ), [schema, table["name"], index_name]
    )
    if cur.fetchone()["exists"]: 
        cur.execute(textwrap.dedent(
            """
            select a.attname as column_name
            from pg_class t
            inner join pg_index ix on t.oid = ix.indrelid
            inner join pg_class i on i.oid = ix.indexrelid
            inner join pg_attribute a on a.attrelid = t.oid and a.attnum = any(ix.indkey)
            where t.relname = %s
            and i.relname = %s
            """
            ), [table["name"], index_name]
        )
        index_columns = [row["column_name"] for row in cur.fetchall()]

        if set(index["columns"]) == set(index_columns): return
        
        cur.execute(sql.SQL(textwrap.dedent(
            """
            drop {index}
            from {schema}.{table}
            """
        )).format(
            schema=sql.Identifier(schema),
            table=sql.Identifier(table["name"]),
            index=sql.SQL(index_name),
        ))

    cur.execute(sql.SQL(textwrap.dedent(
        """
        create index {index}
        on {schema}.{table} ({columns})
        """
    )).format(
        schema=sql.Identifier(schema),
        table=sql.Identifier(table["name"]),
        index=sql.SQL(index_name),
        columns=sql.SQL(", ").join(map(sql.Identifier, index["columns"]))
    ))

def drop_table_indexes(conn: connection, cur: cursor, schema: str, table: dict, indexes: list):
    cur.execute(textwrap.dedent(
        """
        select i.relname as index_name
        from pg_class t
        inner join pg_index ix on t.oid = ix.indrelid
        inner join pg_class i on i.oid = ix.indexrelid
        inner join pg_namespace n on n.oid = t.relnamespace
        where n.nspname = %s
        and  t.relname = %s
        and ix.indisprimary = false
        and ix.indisunique = false;
        """
        ), [schema, table["name"]]
    )
    db_index_names = [row["index_name"] for row in cur.fetchall()]

    defined_index_names = [get_index_name(table, index) for index in indexes]

    for db_index_name in db_index_names:
        if db_index_name in defined_index_names: continue
        cur.execute(sql.SQL(textwrap.dedent(
            """
            drop index {schema}.{index}
            """
        )).format(
            schema=sql.Identifier(schema),
            index=sql.SQL(db_index_name)
        ))

def get_index_name(table:dict, index: dict):
    return get_val_strict(index, "name", f"idx_{table['name']}_{'_'.join(index['columns'])}")