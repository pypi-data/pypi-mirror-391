from pathlib import Path
from psycopg2.extensions import connection, cursor

def deploy_functions(conn: connection, cur: cursor, schema_path: str):
    for file_path in list(Path(f"{schema_path}/functions").glob("*.sql")):
        with open(file_path, "r") as file:
            function = file.read().strip()

        cur.execute(function)