from src.postgresdeploy import deploy
from downerhelper.secrets import get_config_dict
import os
from dotenv import load_dotenv

load_dotenv()

pg_creds = get_config_dict(
    os.environ["DEV_DB_SECRET"], 
    os.environ["GENERAL_KV_DEV"], 
    os.environ["DB_NAME"]
)
deploy("sql", pg_creds)

