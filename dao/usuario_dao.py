from pymongo import MongoClient
from bson import ObjectId
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UsuarioDAO:
    def __init__(self):
        host = os.getenv("MONGO_HOST", "localhost")
        port = os.getenv("MONGO_PORT", "27017")
        user = os.getenv("MONGO_USER")
        pwd = os.getenv("MONGO_PASSWORD")
        db_name = os.getenv("MONGO_DB_NAME", "civictech")

        def _make_client(uri):
            return MongoClient(uri, serverSelectionTimeoutMS=5000)

        # Construir URIs
        uri_no_auth = f"mongodb://{host}:{port}"
        if user and pwd:
            uri_with_auth = f"mongodb://{user}:{pwd}@{host}:{port}/{db_name}?authSource=admin"
        else:
            uri_with_auth = None

        # Intento preferente: si hay credenciales, probar con ellas
        if uri_with_auth:
            try:
                self.client = _make_client(uri_with_auth)
                # Ping para forzar autenticación ahora
                self.client.admin.command("ping")
                logger.info("Conectado a Mongo con autenticación.")
            except Exception as e:
                logger.warning("Fallo autenticación con credenciales: %s. Reintentando sin auth.", e)
                # Reintentar sin auth
                try:
                    self.client = _make_client(uri_no_auth)
                    self.client.admin.command("ping")
                    logger.info("Conectado a Mongo sin autenticación (fallback).")
                except Exception as e2:
                    logger.error("No se pudo conectar a Mongo (con o sin auth): %s", e2)
                    raise
        else:
            # No hay credenciales: conectar sin auth
            try:
                self.client = _make_client(uri_no_auth)
                self.client.admin.command("ping")
                logger.info("Conectado a Mongo sin autenticación.")
            except Exception as e:
                logger.error("No se pudo conectar a Mongo sin autenticación: %s", e)
                raise

        self.db = self.client[db_name]
        self.collection = self.db["usuario"]

    def create(self, data):
        return self.collection.insert_one(data).inserted_id

    def find_by_dni(self, dni):
        return self.collection.find_one({"dni": dni})

    def update_email(self, usuario_id, new_email):
        return self.collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": {"email": new_email}}
        )

    def delete(self, usuario_id):
        return self.collection.delete_one({"_id": ObjectId(usuario_id)})

    def find_all(self):
        return list(self.collection.find())
