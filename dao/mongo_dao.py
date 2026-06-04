# dao/mongo_dao.py
from pymongo import MongoClient, ASCENDING, GEOSPHERE, ReturnDocument
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson import ObjectId
from config import mongo_uri, MONGO_DB_NAME
from datetime import datetime

class MongoDAO:
    def __init__(self, uri: str = None, db_name: str = None):
        self.uri = uri or mongo_uri()
        self.db_name = db_name or MONGO_DB_NAME
        self.client = None
        self.db = None

    def connect(self):
        """
        Conecta al servidor Mongo usando la URI (con auth).
        Llama a ensure_indexes() una vez conectada la DB.
        """
        # Crear cliente con timeout razonable
        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
        # Forzar una llamada para validar credenciales / conectividad
        try:
            # ping para validar conexión y autenticación
            self.client.admin.command("ping")
        except Exception as e:
            # Re-raise con contexto
            raise ConnectionError(f"No se pudo conectar a MongoDB: {e}")

        self.db = self.client[self.db_name]
        # Asegurar índices al conectar
        try:
            self.ensure_indexes()
        except Exception as e:
            # No abortamos la conexión por un fallo de índices, pero lo logueamos
            print("Warning: fallo al crear índices:", e)
        return self.db

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    # --- Indexes / setup ---
    def ensure_indexes(self):
        # Usuario: dni y email únicos
        self.db.usuario.create_index([("dni", ASCENDING)], unique=True)
        self.db.usuario.create_index([("email", ASCENDING)], unique=True)
        # Reporte: geoespacial y patente
        try:
            self.db.reporte.create_index([("ubicacion", GEOSPHERE)])
        except Exception:
            # Algunas versiones/entornos pueden fallar si no hay datos geoespaciales
            pass
        self.db.reporte.create_index([("patente_vehiculo", ASCENDING)])

    # --- Usuario CRUD (ejemplos mínimos) ---
    def create_usuario(self, usuario_doc):
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
        """
        Inserción simple de reporte (sin evidencia). Preferible usar
        insertar_reporte_con_evidencia para garantizar la regla de negocio.
        """
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
        oid = ObjectId(usuario_id)
        res = self.db.usuario.find_one_and_update(
            {"_id": oid},
            {"$inc": {"reputacion": int(delta)}},
            return_document=ReturnDocument.AFTER
        )
        return res

    # --- Validaciones de negocio ---
    def usuario_pertenece_municipio(self, usuario_id, municipio_id):
        try:
            u = self.db.usuario.find_one({
                "_id": ObjectId(usuario_id),
                "municipio_id": ObjectId(municipio_id)
            })
            return u is not None
        except Exception:
            return False

    # --- Inserción atómica: reporte + evidencia ---
    def insertar_reporte_con_evidencia(self, reporte_doc, evidencia_doc):
        """
        Inserta un reporte y al menos una evidencia asociada de forma atómica.
        Reglas aplicadas:
          - usuario_id y municipio_id deben existir y coincidir
          - evidencia_doc debe estar presente y contener url_foto y hash_seguridad_sha
        Usa transacción si el servidor lo soporta (replica set / MongoDB >= 4.0).
        """
        # Validaciones básicas
        if not reporte_doc.get("usuario_id") or not reporte_doc.get("municipio_id"):
            raise ValueError("Faltan usuario_id o municipio_id en el reporte")

        if not evidencia_doc or not evidencia_doc.get("url_foto") or not evidencia_doc.get("hash_seguridad_sha"):
            raise ValueError("La evidencia debe incluir al menos 'url_foto' y 'hash_seguridad_sha'")

        # Convertir ids a ObjectId si vienen como strings
        try:
            reporte_doc["usuario_id"] = ObjectId(reporte_doc["usuario_id"]) if not isinstance(reporte_doc["usuario_id"], ObjectId) else reporte_doc["usuario_id"]
            reporte_doc["municipio_id"] = ObjectId(reporte_doc["municipio_id"]) if not isinstance(reporte_doc["municipio_id"], ObjectId) else reporte_doc["municipio_id"]
        except Exception:
            raise ValueError("usuario_id o municipio_id inválidos")

        # Verificar que el usuario existe y pertenece al municipio
        usuario = self.db.usuario.find_one({"_id": reporte_doc["usuario_id"]})
        if not usuario:
            raise ValueError("Usuario no encontrado")
        if not usuario.get("municipio_id") or not usuario["municipio_id"] == reporte_doc["municipio_id"]:
            raise ValueError("Regla de negocio: usuario.municipio_id debe coincidir con reporte.municipio_id")

        # Preparar campos por defecto
        reporte_doc.setdefault("fechaHora_server", datetime.utcnow())

        # Intentar usar transacción si está disponible
        session = None
        try:
            session = self.client.start_session()
            # Si el servidor no soporta transacciones, with_transaction lanzará OperationFailure
            def txn_ops(sess):
                rres = self.db.reporte.insert_one(reporte_doc, session=sess)
                evidencia_doc["reporte_id"] = rres.inserted_id
                eres = self.db.evidencia.insert_one(evidencia_doc, session=sess)
                return rres.inserted_id

            try:
                inserted_id = session.with_transaction(txn_ops)
            except (OperationFailure, NotImplementedError):
                # Fallback: insertar sin transacción (mejor que nada)
                rres = self.db.reporte.insert_one(reporte_doc)
                evidencia_doc["reporte_id"] = rres.inserted_id
                self.db.evidencia.insert_one(evidencia_doc)
                inserted_id = rres.inserted_id

            return inserted_id
        finally:
            if session:
                session.end_session()
