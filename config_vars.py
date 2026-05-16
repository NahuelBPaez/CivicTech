import os
from dotenv import load_dotenv

# Cargamos las variables del archivo .env local
load_dotenv()

# Creamos las variables que dao.py está buscando con el punto
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "civictech_db")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
