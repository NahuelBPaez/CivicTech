# dao/mongo_dao.py
from pymongo import MongoClient, ASCENDING, GEOSPHERE
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from config import mongo_uri, MONGO_DB_NAME
from datetime import datetime

class MongoDAO:
    def __init__(self, uri=None, db_name=None):
        self.uri = uri or mongo_uri()
        self.db_name = db_name or MONGO_DB_NAME
        self.client = None
        self.db = None

    def connect(self):
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        return self.db

    def close(self):
        if self.client:
            self.client.close()

    # --- Indexes / setup ---
    def ensure_indexes(self):
        # Usuario: dni y email únicos
        self.db.usuario.create_index([("dni", ASCENDING)], unique=True)
        self.db.usuario.create_index([("email", ASCENDING)], unique=True)
        # Reporte: geoespacial y patente
        self.db.reporte.create_index([("ubicacion", GEOSPHERE)])
        self.db.reporte.create_index([("patente_vehiculo", ASCENDING)])

    # --- Usuario CRUD (ejemplos mínimos) ---
    def create_usuario(self, usuario_doc):
        """
        usuario_doc: dict con keys: nombre_apellido, dni, email, contrasena, municipio_id, reputacion (opcional)
        """
        usuario_doc.setdefault("reputacion", 0)
        try:
            res = self.db.usuario.insert_one(usuario_doc)
            return res.inserted_id
        except DuplicateKeyError as e:
            raise

    def find_usuario_by_dni(self, dni):
        return self.db.usuario.find_one({"dni": dni})

    # --- Reporte: insertar y buscar por proximidad ---
    def create_reporte(self, reporte_doc):
        reporte_doc.setdefault("fechaHora_server", datetime.utcnow())
        try:
            res = self.db.reporte.insert_one(reporte_doc)
            return res.inserted_id
        except Exception as e:
            raise

    def find_reportes_near(self, longitude, latitude, max_meters=100):
        return list(self.db.reporte.find({
            "ubicacion": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                    "$maxDistance": max_meters
                }
            }
        }))

    # --- Evidencia ---
    def add_evidencia(self, evidencia_doc):
        try:
            res = self.db.evidencia.insert_one(evidencia_doc)
            return res.inserted_id
        except Exception as e:
            raise

    # --- Reputación: ajuste atómico ---
    def ajustar_reputacion_usuario(self, usuario_id, delta):
        res = self.db.usuario.find_one_and_update(
            {"_id": ObjectId(usuario_id)},
            {"$inc": {"reputacion": int(delta)}},
            return_document=True
        )
        return res

    # --- Validaciones de negocio (ejemplo) ---
    def usuario_pertenece_municipio(self, usuario_id, municipio_id):
        u = self.db.usuario.find_one({"_id": ObjectId(usuario_id), "municipio_id": ObjectId(municipio_id)})
        return u is not None
