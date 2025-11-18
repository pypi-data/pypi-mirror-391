import os
import psycopg2 as pg
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging
import json
import textwrap

from .helpers import *

def deploy_table_checks(conn: connection, cur: cursor, schema: str, table: dict):
    checks = table["constraints"].get("check", [])
    for check in checks:
        drop_table_constraint(conn, cur, schema, table, check["name"])

        cur.execute(sql.SQL(textwrap.dedent(
            """
            alter table {schema}.{table}
            add constraint {check} check ({condition})
            """
        )).format(
            schema=sql.Identifier(schema), 
            table=sql.Identifier(table["name"]),
            check=sql.SQL(check["name"]),
            condition=sql.SQL(check["condition"])
        ))

    defined_check_names = [check["name"] for check in checks]
    cur.execute(sql.SQL(textwrap.dedent(
        """
        select con.conname as constraint_name
        from pg_constraint con
        join pg_class rel on rel.oid = con.conrelid
        join pg_namespace nsp on nsp.oid = rel.relnamespace
        where con.contype = 'c'
        and nsp.nspname = {schema}
        and rel.relname = {table}
        and con.conrelid is not null         
        and conislocal                 
        and conname not like '%_not_null'
        and conname not like 'partition_%_check'
        """
    )).format(
        schema=sql.Literal(schema), 
        table=sql.Literal(table["name"]),
    ))
    db_check_names = [row["constraint_name"] for row in cur.fetchall()]

    for db_check_name in db_check_names:
        if db_check_name in defined_check_names: continue
        drop_table_constraint(conn, cur, schema, table, db_check_name)