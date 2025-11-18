import os
import psycopg2 as pg
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging
import json
import textwrap

from ._helpers import *

def deploy_table_uniques(conn: connection, cur: cursor, schema: str, table: dict):
    uniques = table["constraints"].get("unique", [])
    for unique in uniques:
        cur.execute(textwrap.dedent(
            """
            select a.attname as column_name
            from pg_constraint con
            inner join pg_class rel 
                on rel.oid = con.conrelid
            inner join pg_attribute a 
                on a.attrelid = rel.oid 
                and a.attnum = any(con.conkey)
            inner join pg_namespace nsp 
                on nsp.oid = rel.relnamespace
            where con.contype = 'u'                    
            and nsp.nspname = %s
            and rel.relname = %s
            and con.conname = %s
            """
            ), [schema, table["name"], unique["name"]]
        )
        existing_unique_cols = [row["column_name"] for row in cur.fetchall() or []]
        if set(unique["columns"]) == set(existing_unique_cols): continue

        drop_table_constraint(conn, cur, schema, table, unique["name"])

        cur.execute(sql.SQL(textwrap.dedent(
            """
            alter table {schema}.{table}
            add constraint {unique} unique ({columns})
            """
        )).format(
            schema=sql.Identifier(schema), 
            table=sql.Identifier(table["name"]),
            unique=sql.SQL(unique["name"]),
            columns=sql.SQL(", ").join(map(sql.Identifier, unique["columns"]))
        ))

    defined_unique_names = [unique["name"] for unique in uniques]

    cur.execute(textwrap.dedent(
        """
        select constraint_name
        from information_schema.table_constraints
        where table_schema = %s
        and table_name = %s
        and constraint_type = 'UNIQUE'
        """
        ), [schema, table["name"]]
    )
    db_unique_names = [row["constraint_name"] for row in cur.fetchall()]

    for db_unique_name in db_unique_names:
        if db_unique_name in defined_unique_names: continue
        drop_table_constraint(conn, cur, schema, table, db_unique_name)