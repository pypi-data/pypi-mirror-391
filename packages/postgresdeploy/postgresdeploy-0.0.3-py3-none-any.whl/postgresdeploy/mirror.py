import os
import psycopg2 as pg
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging
import json
import shutil

from .primary_key import fetch_pkey_columns

def mirror(build_dir: str, pg_creds: dict, schemas: list | None = None):
    try:
        conn = cur = None
        conn = pg.connect(**pg_creds)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if schemas is None:
            cur.execute(
                """
                select nspname
                from pg_namespace
                where nspname not in ('pg_catalog', 'information_schema', 'pg_toast')
                and nspname not like 'pg_temp_%'
                and nspname not like 'pg_toast_temp_%'
                and nspname not like 'pg_%ext%'
                """
            )
            schemas = [row["nspname"] for row in cur.fetchall()]

        schema_json = {}
        for schema in schemas:
            schema_json[schema] = {
                "tables": mirror_tables_list(conn, cur, schema),
                "functions": mirror_functions(conn, cur, schema),
                "triggers": mirror_triggers(conn, cur, schema),
                "views": mirror_views(conn, cur, schema),
                "materialized_views": mirror_materialized_views(conn, cur, schema),
            }

        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        os.mkdir(build_dir)

        for schema, schema_data in schema_json.items():
            schema_path = f"{build_dir}/{schema}"
            os.mkdir(schema_path)
            
            for sub_dir in ["tables","functions","triggers","views","materialized_views"]:
                dir_path = f"{schema_path}/{sub_dir}"
                os.mkdir(dir_path)
            
            for table in schema_data["tables"]:
                table_name = table.pop("name")
                with open(f"{schema_path}/tables/{table_name}.json", "w") as file:
                    json.dump(table, file, indent=2)

            for sql_type in ["functions", "triggers", "views", "materialized_views"]:
                for temp_name, temp_code in schema_data[sql_type].items():
                    with open(f"{schema_path}/{sql_type}/{temp_name}.sql", "w") as file:
                        file.write(temp_code)

    except Exception as e:
        logging.error(f"Uncaught exception: {str(e)}")
        raise e
    finally:
        if cur: cur.close()
        if conn: conn.close()

def mirror_tables_list(conn: connection, cur: cursor, schema: str) -> list:
    cur.execute(
        """
        select table_name
        from information_schema.tables
        where table_schema = %s
        and table_type = 'BASE TABLE'
        """, [schema]
    )
    tables = [row["table_name"] for row in cur.fetchall()]

    tables_list = []
    for table in tables:
        tables_list.append(mirror_table_json(conn, cur, schema, table))

    return tables_list

def mirror_table_json(conn: connection, cur: cursor, schema: str, table: str) -> dict:
    return {
        "name": table,
        "columns": mirror_columns_list(conn, cur, schema, table),
        "constraints": mirror_constraints_json(conn, cur, schema, table),
        "indexes": []
    }

def mirror_columns_list(conn: connection, cur: cursor, schema: str, table: str) -> list:
    cur.execute(
        """
        select *
        from information_schema.columns
        where table_schema = %s
        and table_name = %s
        """, [schema, table]
    )
    rows = cur.fetchall()

    columns = []
    for row in rows:
        columns.append({
            "name": row["column_name"],
            "type": row["data_type"],
            "not_null": True if row["is_nullable"] == "NO" else False,
            "default": row["column_default"]
        })
    return columns

def mirror_constraints_json(conn: connection, cur: cursor, schema: str, table: str) -> dict:
    return {
        "primary_key": fetch_pkey_columns(cur, schema, {"name": table}),
        "foreign_key": [],
        "check": mirror_check_constraint_list(conn, cur, schema, table),
        "unique": mirror_unique_constraint_list(conn, cur, schema, table),
    }

def mirror_check_constraint_list(conn: connection, cur: cursor, schema: str, table: str) -> dict:
    cur.execute(
        """
        select
            con.conname as constraint_name,
            pg_get_constraintdef(con.oid) as condition
        from pg_constraint con
        inner join pg_class rel on rel.oid = con.conrelid
        inner join pg_namespace nsp on nsp.oid = rel.relnamespace
        where con.contype = 'c'  
        and nsp.nspname = %s 
        and rel.relname = %s;
        """, [schema, table]
    )
    rows = cur.fetchall()

    checks = []
    for row in rows:
        checks.append({
            "name": row["constraint_name"],
            "condition": row["condition"].replace("CHECK", "").strip()
        })
    return checks

def mirror_unique_constraint_list(conn: connection, cur: cursor, schema: str, table: str) -> dict:
    cur.execute(
        """
        select
            con.conname as constraint_name,
            array_agg(att.attname order by att.attnum) as columns
        from pg_constraint con
        inner join pg_class rel on rel.oid = con.conrelid
        inner join pg_namespace nsp on nsp.oid = rel.relnamespace
        inner join unnest(con.conkey) as cols(attnum)
            on true
        inner join pg_attribute att 
            on att.attrelid = rel.oid and att.attnum = cols.attnum
        where con.contype = 'u'
        and nsp.nspname = %s
        and rel.relname = %s
        group by con.conname
        """, [schema, table]
    )
    rows = cur.fetchall()

    uniques = []
    for row in rows:
        uniques.append({
            "name": row["constraint_name"],
            "columns": row["columns"]
        })
    return uniques

def mirror_functions(conn: connection, cur: cursor, schema: str):
    cur.execute(
        """
        select
            p.proname as function_name,
            pg_get_functiondef(p.oid) as code
        from pg_proc p
        join pg_namespace n on n.oid = p.pronamespace
        join pg_language l on l.oid = p.prolang
        where n.nspname = %s
        and l.lanname = 'plpgsql'
        order by function_name;
        """, [schema]
    )
    rows = cur.fetchall()

    functions = {}
    for row in rows:
        functions[row["function_name"]] = row["code"]
    return functions

def mirror_triggers(conn: connection, cur: cursor, schema: str):
    cur.execute(
        """
        select
            t.tgname as trigger_name,
            pg_get_triggerdef(t.oid, true) as trigger_definition
        from pg_trigger t
        join pg_class c     on c.oid = t.tgrelid
        join pg_namespace n on n.oid = c.relnamespace
        where n.nspname = %s
        and not t.tgisinternal
        """, [schema]
    )
    rows = cur.fetchall()

    triggers = {}
    for row in rows:
        triggers[row["trigger_name"]] = row['trigger_definition']
    return triggers

def mirror_views(conn: connection, cur: cursor, schema: str):
    cur.execute(
        """
        select viewname view_name, definition
        from pg_views
        where schemaname = %s;
        """, [schema]
    )
    rows = cur.fetchall()

    views = {}
    for row in rows:
        definition = f"create or replace view {row['view_name']} as\n{row['definition']}"
        views[row["view_name"]] = definition
    return views

def mirror_materialized_views(conn: connection, cur: cursor, schema: str):
    cur.execute(
        """
        select matviewname mat_view_name, definition
        from pg_matviews
        where schemaname = %s;
        """, [schema]
    )
    rows = cur.fetchall()

    materialized_views = {}
    for row in rows:
        definition = f"create materialized view {row['mat_view_name']} as\n{row['definition']}"
        materialized_views[row["mat_view_name"]] = definition
    return materialized_views