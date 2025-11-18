import sqlite3
import os
from appdirs import user_data_dir

APP_NAME = "devguide"
APP_AUTHOR = "devguide"

# Define o diretório de dados do aplicativo
DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
# Garante que o diretório de dados exista
os.makedirs(DATA_DIR, exist_ok=True)

# Define o caminho completo para o banco de dados
DB_PATH = os.path.join(DATA_DIR, "devguide.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def db_exists():
    return os.path.exists(DB_PATH)

def init_db():
    with get_conn() as conn:
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
