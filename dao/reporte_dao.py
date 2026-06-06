# dao/reporte_dao.py
from datetime import datetime
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, ReturnDocument

class ReportesDAO:
    """
    DAO para la colección 'reporte' y la colección 'evidencia',
    adaptado a las convenciones del script de base de datos del proyecto.
    Acepta una instancia de MongoDAO (con .db y .client) o una pymongo Database.
    """
    def __init__(self, mongo_or_db):
        if hasattr(mongo_or_db, "db"):
            self.db = mongo_or_db.db
            self.client = getattr(mongo_or_db, "client", None)
        else:
            self.db = mongo_or_db
            self.client = None

        self.reporte_col = self.db.get_collection("reporte")
        self.evidencia_col = self.db.get_collection("evidencia")
        self._ensure_indexes()

    def _now(self):
        return datetime.utcnow()

    def _ensure_indexes(self):
        try:
            # Índices complementarios; el script principal ya crea los índices críticos
            self.reporte_col.create_index([("usuario_id", ASCENDING)])
            self.reporte_col.create_index([("municipio_id", ASCENDING)])
            self.reporte_col.create_index([("fechaHora_server", DESCENDING)])
            self.evidencia_col.create_index([("reporte_id", ASCENDING)])
        except Exception as e:
            # No abortar si no hay permisos para crear índices
            print("Advertencia: no se pudieron crear índices en reporte/evidencia:", e)

    # -------------------------
    # Lectura y listados
    # -------------------------
    def get_reporte_by_id(self, reporte_id):
        """Devuelve el documento de reporte por _id (acepta string o ObjectId)."""
        oid = reporte_id if isinstance(reporte_id, ObjectId) else ObjectId(reporte_id)
        return self.reporte_col.find_one({"_id": oid})

    def list_reportes(self, filter_by=None, limit=50, skip=0, sort=None):
        q = filter_by or {}
        cursor = self.reporte_col.find(q).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        return list(cursor)

    # -------------------------
    # Creación y evidencias
    # -------------------------
    def create_reporte(self, reporte_doc):
        """
        Inserta un reporte simple. Preferible usar insertar_reporte_con_evidencia
        para respetar la regla de negocio de al menos 1 evidencia.
        """
        reporte_doc.setdefault("fechaHora_server", self._now())
        res = self.reporte_col.insert_one(reporte_doc)
        return res.inserted_id

    def add_evidencia(self, evidencia_doc):
        """
        Inserta una evidencia en la colección 'evidencia'.
        Debe contener al menos: reporte_id (ObjectId), url_foto, hash_seguridad_sha.
        """
        evidencia_doc.setdefault("uploaded_at", self._now())
        # Asegurar que reporte_id sea ObjectId si viene como string
        if "reporte_id" in evidencia_doc and not isinstance(evidencia_doc["reporte_id"], ObjectId):
            evidencia_doc["reporte_id"] = ObjectId(evidencia_doc["reporte_id"])
        res = self.evidencia_col.insert_one(evidencia_doc)
        return res.inserted_id

    # -------------------------
    # Inserción atómica: reporte + evidencia
    # -------------------------
    def insertar_reporte_con_evidencia(self, reporte_doc, evidencia_doc):
        """
        Inserta un reporte y al menos una evidencia asociada.
        Reglas aplicadas (copiadas del script):
          - usuario_id y municipio_id deben existir y coincidir
          - evidencia_doc debe incluir url_foto y hash_seguridad_sha
        Usa transacción si self.client está disponible; si no, hace fallback.
        """
        # Validaciones básicas
        if not reporte_doc.get("usuario_id") or not reporte_doc.get("municipio_id"):
            raise ValueError("Faltan usuario_id o municipio_id en el reporte")
        if not evidencia_doc or not evidencia_doc.get("url_foto") or not evidencia_doc.get("hash_seguridad_sha"):
            raise ValueError("La evidencia debe incluir al menos 'url_foto' y 'hash_seguridad_sha'")

        # Convertir ids a ObjectId si vienen como strings
        try:
            if not isinstance(reporte_doc["usuario_id"], ObjectId):
                reporte_doc["usuario_id"] = ObjectId(reporte_doc["usuario_id"])
            if not isinstance(reporte_doc["municipio_id"], ObjectId):
                reporte_doc["municipio_id"] = ObjectId(reporte_doc["municipio_id"])
        except Exception:
            raise ValueError("usuario_id o municipio_id inválidos")

        # Verificar que el usuario existe y pertenece al municipio
        usuario = self.db.usuario.find_one({"_id": reporte_doc["usuario_id"]})
        if not usuario:
            raise ValueError("Usuario no encontrado")
        if not usuario.get("municipio_id") or usuario["municipio_id"] != reporte_doc["municipio_id"]:
            raise ValueError("Regla de negocio: usuario.municipio_id debe coincidir con reporte.municipio_id")

        reporte_doc.setdefault("fechaHora_server", self._now())

        session = None
        try:
            if self.client:
                session = self.client.start_session()
            def txn_ops(sess=None):
                rres = self.reporte_col.insert_one(reporte_doc, session=sess) if sess else self.reporte_col.insert_one(reporte_doc)
                evidencia_doc["reporte_id"] = rres.inserted_id
                self.evidencia_col.insert_one(evidencia_doc, session=sess) if sess else self.evidencia_col.insert_one(evidencia_doc)
                return rres.inserted_id

            if session:
                try:
                    inserted_id = session.with_transaction(lambda s: txn_ops(s))
                except Exception:
                    # fallback sin transacción
                    inserted_id = txn_ops(None)
            else:
                inserted_id = txn_ops(None)

            return inserted_id
        finally:
            if session:
                session.end_session()

    # -------------------------
    # Búsquedas geoespaciales y utilidades
    # -------------------------
    def find_reportes_near(self, longitude, latitude, max_meters=100):
        return list(self.reporte_col.find({
            "ubicacion": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                    "$maxDistance": max_meters
                }
            }
        }))

    def count_by_estado(self):
        pipeline = [
            {"$group": {"_id": "$estado", "count": {"$sum": 1}}}
        ]
        return list(self.reporte_col.aggregate(pipeline))

