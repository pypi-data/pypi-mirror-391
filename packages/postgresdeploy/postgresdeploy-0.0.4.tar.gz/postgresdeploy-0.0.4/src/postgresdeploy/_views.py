from pathlib import Path
from psycopg2.extensions import connection, cursor
import re
from psycopg2 import sql

# todo: assign permissions after drop view

def deploy_views(conn: connection, cur: cursor, schema_path: str):
    deploy_regular_views(conn, cur, schema_path)
    deploy_materialized_views(conn, cur, schema_path)

def deploy_regular_views(conn: connection, cur: cursor, schema_path: str):
    for file_path in list(Path(f"{schema_path}/views").glob("*.sql")):
        with open(file_path, "r") as file:
            view = file.read().strip()

        try:
            view = re.sub(
                r'(?is)^.*?\bview\b',
                'create or replace view',
                view
            )
            cur.execute(view)
        except Exception as e:
            print(f"Could not replace view: {str(e)}")
            view_name = re.search(
                r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+([^\s(]+)',
                view,
                re.IGNORECASE
            ).group(1) 
            cur.execute(sql.SQL(
                """
                drop view if exists {view}
                """
            ).format(
                view=sql.SQL(view_name)
            ))
            cur.execute(view)
            cur.execute(sql.SQL(
                """
                grant select 
                on {view}
                to public
                """
            ).format(
                view=view_name
            ))

def deploy_materialized_views(conn: connection, cur: cursor, schema_path: str):
    for file_path in list(Path(f"{schema_path}/materialized_views").glob("*.sql")):
        with open(file_path, "r") as file:
            materialized_view = file.read().strip()
        materialized_view_name = re.search(
            r'CREATE\s+(?:MATERIALIZED\s+)?VIEW\s+([^\s(]+)',
            materialized_view,
            re.IGNORECASE
        ).group(1)
        cur.execute(sql.SQL(
            """
            drop materialized view if exists {view_name}
            """
        ).format(
            view_name=sql.SQL(materialized_view_name)
        ))
        cur.execute(materialized_view)
        cur.execute(sql.SQL(
            """
            grant select 
            on materialized view {view}
            to public
            """
        ).format(
            view=materialized_view_name
        ))
        