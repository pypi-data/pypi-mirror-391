import os
import psycopg2 as pg
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging
import json
import textwrap
# from jsonschema import validate, ValidationError

from ._helpers import *
from ._tables import *
from ._column import *
from ._primary_key import *
from ._check_constraint import *
from ._unique_constraint import *
from ._indexes import *
from ._triggers import *
from ._functions import *
from ._views import *

# todo: sequences, types?, aggregates?, operators?

# todo: build folder structure and jsons from db
# todo: parse folders/json files for errors before executing?
#! todo: option to drop tables if not exist
#! todo: option to drop schemas if not exist

# logic flow -> deploy table
# 1. create table if doesnt exist
# 1.1 add constraints
# 1.2 add indexes
# 2. alter table if does exist
# 2.1 create new columns
# 2.2 alter column types
# 2.3 apply constraints to table
# 2.5 apply indexes to table
# 2.4 alter column not nulls, defaults
# 2.5 drop any columns

def deploy(base_dir: str, pg_creds: dict):
    try:
        conn = cur = None
        conn = pg.connect(**pg_creds)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        for sub_dir in get_dirs(base_dir):
            deploy_schema(conn, cur, sub_dir)

    except Exception as e:
        logging.error(f"Uncaught exception: {str(e)}")
        raise e
    finally:
        if cur: cur.close()
        if conn: conn.close()

def deploy_schema(conn: connection, cur: cursor, schema_path: str):
    try:
        schema = get_schema_from_path(schema_path)
        cur.execute(textwrap.dedent(
            """
            select exists (
                select 1
                from information_schema.schemata
                where schema_name = %s
            )
            """
            ), [schema]
        )
        if not cur.fetchone()["exists"]:
            create_schema(conn, cur, schema)
            return #! exit until can create schema

        deploy_tables(conn, cur, schema_path)
        deploy_functions(conn, cur, schema_path)
        deploy_triggers(conn, cur, schema_path)
        # deploy_views(conn, cur, schema_path) # todo redo with json?

        conn.commit()

    except CaughtException as e:
        conn.rollback()
        logging.error(str(e))
    except Exception as e:
        conn.rollback()
        logging.error(f"Uncaught exception: {str(e)}")

def create_schema(conn: connection, cur: cursor, schema: str):
    # todo: create new schema (need elevated permissions)
    print(f"need to create schema: {schema}")

##########################################################
### Helpers

tables_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            },
            "columns": {
                "type": "array",
                "items": {
                    
                }
            }
        },
        "required": [
            "name",
            "type",
        ]
    }
}

