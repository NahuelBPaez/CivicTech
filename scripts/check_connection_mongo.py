# check_connection.py
from dotenv import load_dotenv
import os
import sys
from pymongo import MongoClient, errors

load_dotenv()

def build_uri():
    host = os.getenv("MONGO_HOST", "localhost")
    port = os.getenv("MONGO_PORT", "27017")
    user = os.getenv("MONGO_USER")
    pwd = os.getenv("MONGO_PASSWORD")
    if user and pwd:
        return f"mongodb://{user}:{pwd}@{host}:{port}/?authSource=admin"
    return f"mongodb://{host}:{port}"

def main():
    uri = build_uri()
    db_name = os.getenv("MONGO_DB_NAME", "civictech")
    print(f"Usando URI: {uri}")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # fuerza la conexión
        client.server_info()
        dbs = client.list_database_names()
        print("Conexión OK. Bases disponibles:", dbs)
        exists = db_name in dbs
        print(f"Base objetivo '{db_name}':", "Existe" if exists else "No existe (se creará al insertar)")
        client.close()
        return 0
    except errors.ServerSelectionTimeoutError as e:
        print("ERROR: no se pudo conectar al servidor MongoDB.", e)
        return 2
    except errors.OperationFailure as e:
        print("ERROR de autenticación o permisos.", e)
        return 3
    except Exception as e:
        print("ERROR inesperado:", e)
        return 1

if __name__ == "__main__":
    sys.exit(main())
