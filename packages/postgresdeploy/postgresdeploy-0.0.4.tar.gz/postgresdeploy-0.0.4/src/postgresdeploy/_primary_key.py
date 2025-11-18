import os
import psycopg2 as pg
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging
import json
import textwrap

from ._helpers import *

def deploy_primary_key(conn: connection, cur: cursor, schema: str, table: dict):
    pkey_defined = "primary_key" in table["constraints"].keys()

    cur.execute(textwrap.dedent(
        """
        select exists (
            select 1
            from information_schema.table_constraints
            where table_schema = %s
            and table_name = %s
            and constraint_type = 'PRIMARY KEY'
        )
        """
        ), [schema, table["name"]]
    )
    pkey_exists = cur.fetchone()["exists"]

    if not pkey_defined:
        if not pkey_exists: return
        drop_primary_key(conn, cur, schema, table)
        return

    new_pkey_cols = [col for col in table["constraints"]["primary_key"]]
    
    if pkey_exists:
        existing_pkey_cols = fetch_pkey_columns(cur, schema, table)
        if set(new_pkey_cols) == set(existing_pkey_cols): return
        drop_primary_key(conn, cur, schema, table)

    cur.execute(sql.SQL(
        """
        alter table {schema}.{table}
        add constraint {pkey_name} primary key ({pkey_cols}) 
        """
    ).format(
        schema=sql.Identifier(schema), 
        table=sql.Identifier(table["name"]), 
        pkey_name=sql.SQL(f"{table['name']}_pkey"),
        pkey_cols=sql.SQL(", ").join(map(sql.Identifier, new_pkey_cols))
    ))

def drop_primary_key(conn: connection, cur: cursor, schema: str, table: dict):
    cur.execute(
        """
        select constraint_name
        from information_schema.table_constraints
        where table_schema = %s
        and table_name = %s
        and constraint_type = 'PRIMARY KEY'
        """, [schema, table["name"]]
    )
    pkey_name = cur.fetchone()["constraint_name"]

    drop_table_constraint(conn, cur, schema, table, pkey_name)

def fetch_pkey_columns(cur: cursor, schema: str, table: dict):
    cur.execute(
        """
        select kcu.column_name
        from information_schema.table_constraints tc
        join information_schema.key_column_usage kcu 
        on kcu.constraint_name = tc.constraint_name
        where kcu.constraint_schema = tc.constraint_schema
        and tc.constraint_type = 'PRIMARY KEY'
        and kcu.table_schema = %s
        and kcu.table_name = %s
        """, [schema, table["name"]]
    )
    return [row["column_name"] for row in cur.fetchall()]