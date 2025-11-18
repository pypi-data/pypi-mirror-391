import os
import psycopg2 as pg
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging
import json
import textwrap
from pathlib import Path
import re

from ._helpers import *

def deploy_triggers(conn: connection, cur: cursor, schema_path: str):
    schema = get_schema_from_path(schema_path)
    defined_triggers = {}
    for file_path in list(Path(f"{schema_path}/triggers").glob("*.sql")):
        with open(file_path, "r") as file:
            trigger = file.read().strip()

            pattern = re.compile(
                r"CREATE\s+TRIGGER\s+(\S+)\s+.*?ON\s+(\S+)",
                re.IGNORECASE | re.DOTALL
            )
            trigger_name, table_name = pattern.search(trigger).groups() 
            drop_trigger(cur, schema, table_name, trigger_name)
            cur.execute(trigger)

            if table_name not in defined_triggers:
                defined_triggers[table_name] = []
            defined_triggers[table_name].append(trigger_name)

    schema = get_schema_from_path(schema_path)
    cur.execute(
        """
        select trigger_name, event_object_table table_name
        from information_schema.triggers
        where event_object_schema = %s
        """, [schema]
    )
    db_triggers = {}
    for row in cur.fetchall():
        if row["table_name"] not in db_triggers:
            db_triggers[row["table_name"]] = []
        db_triggers[row["table_name"]].append(row["trigger_name"])
    
    for db_table, db_trigs in db_triggers.items():
        if db_table not in defined_triggers: continue
        for db_trig in db_trigs:
            if db_trig in defined_triggers[db_table]: continue
            drop_trigger(cur, schema, db_table, db_trig)

def drop_trigger(cur, schema, table_name, trigger_name):
    cur.execute(sql.SQL(
        """
        drop trigger if exists {trigger} on {schema}.{table}
        """
    ).format(
        schema=sql.SQL(schema),
        trigger=sql.SQL(trigger_name), 
        table=sql.SQL(table_name)
    ))

def deploy_trigger(conn: connection, cur: cursor, schema: str, trigger: str):
    cur.execute()