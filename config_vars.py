import os
import psycopg2
from dotenv import load_dotenv

# Cargamos las variables del archivo .env local
load_dotenv()

def obtener_conexion():
    try:
        conexion = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "civictech_db"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conexion
    except psycopg2.Error as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        return None
