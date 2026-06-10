# dao/reporte_dao.py
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, ReturnDocument

class ReportesDAO:
    """
    DAO para la colección 'reporte' y la colección 'evidencia'.
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
    def create_reporte(self, reporte_doc, evidencia_doc=None):
        """
        Inserta un reporte simple. Ahora exige evidencia asociada.
        - Si no se provee evidencia_doc, se lanza ValueError indicando usar insert_report_with_evidence.
        - Si se provee evidencia_doc, se delega a insertar_reporte_con_evidencia para mantener atomicidad.
        """
        if evidencia_doc is None:
            raise ValueError("No se permite insertar un reporte sin evidencia. Usá insert_report_with_evidence(reporte_doc, evidencia_doc).")

        # Si se pasó evidencia, delegar a la inserción atómica
        return self.insertar_reporte_con_evidencia(reporte_doc, evidencia_doc)

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
        Reglas aplicadas:
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
    # Wrapper amigable para notebooks/scripts
    # -------------------------
    def insert_report_with_evidence(self, reporte_doc: dict, evidencia_doc: dict):
        """
        Wrapper amigable para notebooks:
        - Normaliza ids (acepta str u ObjectId).
        - Valida campos mínimos.
        - Reusa insertar_reporte_con_evidencia y devuelve (reporte_id, evidencia_id, error_msg).
        """
        # Normalizar ids
        try:
            if "usuario_id" in reporte_doc and not isinstance(reporte_doc["usuario_id"], ObjectId):
                reporte_doc["usuario_id"] = ObjectId(reporte_doc["usuario_id"])
            if "municipio_id" in reporte_doc and not isinstance(reporte_doc["municipio_id"], ObjectId):
                reporte_doc["municipio_id"] = ObjectId(reporte_doc["municipio_id"])
        except Exception as e:
            return None, None, f"IDs inválidos: {type(e).__name__} {e}"

        # Validaciones rápidas
        if not reporte_doc.get("usuario_id") or not reporte_doc.get("municipio_id"):
            return None, None, "Faltan usuario_id o municipio_id en el reporte"
        if not evidencia_doc or not evidencia_doc.get("url_foto") or not evidencia_doc.get("hash_seguridad_sha"):
            return None, None, "La evidencia debe incluir 'url_foto' y 'hash_seguridad_sha'"

        # Delegar a la implementación que maneja transacciones/fallback
        try:
            reporte_id = self.insertar_reporte_con_evidencia(reporte_doc, evidencia_doc)
            if not reporte_id:
                return None, None, "No se insertó el reporte (sin error explícito)"
            ev = self.evidencia_col.find_one({"reporte_id": reporte_id}, sort=[("uploaded_at", DESCENDING)])
            evidencia_id = ev["_id"] if ev else None
            return reporte_id, evidencia_id, None
        except Exception as e:
            return None, None, f"Error al insertar reporte+evidencia: {type(e).__name__} {e}"

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

    # -------------------------
    # Listado agrupado por municipio (método añadido)
    # -------------------------
    def list_recent_grouped_by_municipio(self, limit=200):
        """
        Devuelve una lista de tuplas (municipio_nombre, [reportes]) ordenadas por nombre de municipio.
        Cada reporte contiene los campos proyectados por el pipeline.
        """
        pipeline = [
            {"$sort": {"fechaHora_server": -1}},
            {"$limit": limit},
            {"$lookup": {
                "from": "municipio",
                "localField": "municipio_id",
                "foreignField": "_id",
                "as": "mun"
            }},
            {"$unwind": {"path": "$mun", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 1,
                "patente_vehiculo": 1,
                "estado": 1,
                "fechaHora_server": 1,
                "usuario_id": 1,
                "municipio_id": 1,
                "municipio_nombre": "$mun.nombre",
                "descripcion": 1
            }}
        ]
        rows = list(self.reporte_col.aggregate(pipeline))
        grouped = {}
        for r in rows:
            mun = r.get("municipio_nombre") or "SIN_NOMBRE"
            grouped.setdefault(mun, []).append(r)
        return [(mun, grouped[mun]) for mun in sorted(grouped.keys())]

