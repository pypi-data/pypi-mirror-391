import os
from psycopg2.extensions import connection, cursor
from psycopg2 import sql
import textwrap

def get_schema_from_path(path: str):
    return path.split("/")[-1]

def get_dirs(dir: str):
    return [entry.path for entry in os.scandir(dir) if entry.is_dir()]

def bool_to_str(boolean: bool):
    return "true" if boolean else "false"

class CaughtException(Exception):
    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.code = code

def get_val_strict(obj: dict, key: str, default = None):
    value = obj.get(key)
    if value is None: return default
    elif isinstance(value, str) and value.strip() == "": return default
    elif isinstance(value, dict) and value == {}: return default
    elif isinstance(value, list) and value == []: return default 
    return value

def convert_boolean(col_def: dict, key: str, sql: str = None):
    if sql is None: sql = key
    return sql if col_def.get(key, False) else ""

def build_column_string(col_def: dict):
    parts = [
        col_def["name"],
        col_def["type"]
    ]

    parts.append(convert_boolean(col_def, "primary_key", "primary key"))
    parts.append(convert_boolean(col_def, "not_null", "not null"))

    default = get_val_strict(col_def, "default")
    if default is not None:
        parts.append(f"default {default}")

    # parts.append(convert_boolean(col_def, "unique"))

    check = get_val_strict(col_def, "check")
    if check is not None:
        parts.append(f"check ({check})")

    parts.append(get_val_strict(col_def, "identity"))

    parts.append(get_val_strict(col_def, "generated"))
    
    collate = get_val_strict(col_def, "collate")
    if collate is not None:
        parts.append(f"collate {collate}")

    parts = [part for part in parts if part is not None]
    return " ".join(parts)

def drop_table_constraint(conn: connection, cur: cursor, schema: str, table: dict, constraint: str):
    cur.execute(sql.SQL(textwrap.dedent(
        """
        alter table {schema}.{table}
        drop constraint if exists {pkey_name}
        """
    )).format(
        schema=sql.Identifier(schema), 
        table=sql.Identifier(table["name"]), 
        pkey_name=sql.SQL(constraint)
    ))