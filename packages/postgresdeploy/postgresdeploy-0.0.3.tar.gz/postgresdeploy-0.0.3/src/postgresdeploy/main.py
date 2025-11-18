import os
import psycopg2 as pg
from psycopg2.extensions import connection, cursor
import logging
import json

# todo: build folder structure and jsons from db
# todo: add delete mode (delete objects that do not exist here)
# todo: default is stop on fail, could add fail pass option

def deploy(base_dir: str, pg_creds: dict):
    try:
        conn = cur = None
        conn = pg.connect(**pg_creds)

        for sub_dir in get_dirs(base_dir):
            deploy_schema(conn, sub_dir)
            
    except Exception as e:
        logging.error(f"Uncaught exception: {str(e)}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def deploy_schema(conn: connection, schema_path: str):
    try:
        cur = conn.cursor()

        schema = schema_path.split("/")[-1]
        cur.execute(
            """
            select exists (
                select 1
                from information_schema.schemata
                where schema_name = %s
            )
            """, [schema]
        )
        if not cur.fetchone()[0]:
            # todo: create new schema (need elevated permissions)
            print("schema not found")
            return

    except Exception as e:
        raise e
    finally:
        if cur: cur.close()

    deploy_tables(conn, schema, schema_path)

def deploy_tables(conn: connection, schema: str, schema_path: str):
    with open(f"{schema_path}/tables.json", "r") as file:
        tables = json.loads(file.read())

    for table in tables:
        deploy_table(conn, schema, table)

def deploy_table(conn: connection, schema: str, table: dict):
    try:
        cur = conn.cursor()

        cur.execute(
            """
            select exists (
                select 1
                from information_schema.tables
                where table_schema = %s
                and table_name = %s
            )
            """, [schema, table["name"]]
        )
        if not cur.fetchone()[0]:
            create_table()
        else:
            update_table()

    except Exception as e:
        raise e
    finally:
        if cur: cur.close()

def create_table():
    print("create table")

def update_table():
    print("update table")

def get_dirs(dir: str):
    return [entry.path for entry in os.scandir(dir) if entry.is_dir()]