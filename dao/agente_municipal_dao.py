# agente_municipal_dao.py
"""
DAO para agente municipal
- Contiene la lógica de persistencia y la regla de negocio:
  el agente solo puede ver reportes de su municipio y solo puede
  modificar el campo 'estado' de esos reportes.
- Diseñado para importarse desde un notebook .ipynb sin cambios adicionales.
"""

from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime, timezone
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, OperationFailure
from bson import ObjectId

class AgenteMunicipalDAO:
    """
    DAO para operaciones del agente municipal.

    Reglas principales:
    - El agente solo puede ver reportes de su propio municipio.
    - El agente solo puede modificar el campo 'estado' de un reporte.
    - Para inserciones, se exige evidencia asociada y que el reporte pertenezca
      al municipio del agente.
    """

    VALID_ESTADOS = ("Pendiente", "Validada", "Rechazada", "En Proceso", "Resuelta")

    def __init__(self, mongo, agente_municipio_id: ObjectId):
        """
        mongo: wrapper que expone .db (p. ej. mongo.db = client.mi_base)
               y opcionalmente .client para transacciones.
        agente_municipio_id: ObjectId del municipio del agente (permiso).
        """
        if not isinstance(agente_municipio_id, ObjectId):
            raise ValueError("agente_municipio_id debe ser ObjectId")
        self.mongo = mongo
        self.db = mongo.db
        self.agente_municipio_id = agente_municipio_id

    # -----------------------
    # Índices y utilidades
    # -----------------------
    def ensure_indexes(self) -> None:
        """Crear índices recomendados para consultas frecuentes.
        Si la conexión no tiene permisos para crear índices, capturamos el error
        y emitimos un aviso en lugar de interrumpir la ejecución del notebook.
        """
        try:
            self.db.reporte.create_index([("municipio_id", ASCENDING)])
            self.db.reporte.create_index([("fechaHora_server", DESCENDING)])
            self.db.evidencia.create_index([("reporte_id", ASCENDING)])
            self.db.evidencia.create_index([("uploaded_by", ASCENDING)])
        except OperationFailure as ofe:
            # No interrumpir el notebook por falta de permisos
            print("AVISO: no se pudieron crear índices (permiso denegado).")
            try:
                details = getattr(ofe, "details", None)
                if details:
                    print("Detalle:", details)
                else:
                    print("Detalle:", str(ofe))
            except Exception:
                print("AVISO: error al obtener detalles del OperationFailure.")
        except PyMongoError as e:
            print("AVISO: error al crear índices:", type(e).__name__, str(e))

    def _now_utc(self) -> datetime:
        return datetime.now(timezone.utc)

    def _municipio_match_filter(self) -> Dict[str, Any]:
        """
        Devuelve un filtro que coincide con el municipio del agente tanto si
        los documentos tienen municipio_id como ObjectId como si lo tienen como string.
        """
        return {
            "$or": [
                {"municipio_id": self.agente_municipio_id},
                {"municipio_id": str(self.agente_municipio_id)}
            ]
        }

    # -----------------------
    # Lecturas (respetando permiso)
    # -----------------------
    def list_reports_by_municipio(self, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Lista reportes que pertenecen al municipio del agente.
        Devuelve documentos con 'municipio_nombre' embebido.
        Acepta que en la colección 'reporte' el campo municipio_id sea ObjectId o string.
        """
        match_filter = self._municipio_match_filter()
        pipeline = [
            {"$match": match_filter},
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
        return list(self.db.reporte.aggregate(pipeline))

    def get_report_with_evidences(self, reporte_id: ObjectId) -> Optional[Dict[str, Any]]:
        """
        Devuelve el reporte con sus evidencias solo si pertenece al municipio del agente.
        Si el reporte no existe o no pertenece al municipio, devuelve None.
        """
        rpt = self.db.reporte.find_one({"_id": reporte_id})
        if not rpt:
            return None

        # comparar aceptando string u ObjectId en el documento
        rpt_mid = rpt.get("municipio_id")
        if rpt_mid != self.agente_municipio_id and str(rpt_mid) != str(self.agente_municipio_id):
            return None

        evidencias = list(self.db.evidencia.find({"reporte_id": reporte_id}))
        rpt["evidencias"] = evidencias
        mun = self.db.municipio.find_one({"_id": rpt.get("municipio_id")}, {"nombre": 1})
        # si lookup por ObjectId falló (porque municipio_id es string), intentar buscar por string->ObjectId
        if not mun:
            try:
                mun = self.db.municipio.find_one({"_id": ObjectId(str(rpt.get("municipio_id")))}, {"nombre": 1})
            except Exception:
                mun = None
        rpt["municipio_nombre"] = mun.get("nombre") if mun else None
        return rpt

    # -----------------------
    # Validaciones internas
    # -----------------------
    def _validate_reporte_minimo(self, r: Dict[str, Any]) -> Optional[str]:
        if not isinstance(r.get("usuario_id"), ObjectId):
            return "usuario_id debe ser ObjectId"
        if not isinstance(r.get("municipio_id"), (ObjectId, str)):
            return "municipio_id debe ser ObjectId o string con ObjectId"
        if "ubicacion" not in r or not isinstance(r["ubicacion"], dict):
            return "ubicacion debe ser GeoJSON Point"
        if r.get("estado") not in self.VALID_ESTADOS:
            return "estado inválido"
        return None

    def _validate_evidencia_minima(self, e: Dict[str, Any]) -> Optional[str]:
        if not e:
            return "EVIDENCIA AUSENTE"
        if "url_foto" not in e or not isinstance(e["url_foto"], str) or not e["url_foto"].strip():
            return "url_foto inválida"
        if "hash_seguridad_sha" not in e or not isinstance(e["hash_seguridad_sha"], str) or not e["hash_seguridad_sha"].strip():
            return "hash_seguridad_sha inválido"
        return None

    # -----------------------
    # Inserciones (aplica regla de negocio)
    # -----------------------
    def insert_report_with_evidence(self, reporte_doc: Dict[str, Any], evidencia_doc: Dict[str, Any],
                                    use_transaction: bool = True) -> Tuple[Optional[ObjectId], Optional[ObjectId], Optional[str]]:
        """
        Inserta un reporte y su evidencia asociada solo si:
        - el reporte pertenece al municipio del agente, y
        - la evidencia es válida.
        Retorna (reporte_id, evidencia_id, error_msg). error_msg es None en éxito.
        """
        # Validaciones locales
        err = self._validate_reporte_minimo(reporte_doc)
        if err:
            return None, None, f"Validación reporte: {err}"
        err_ev = self._validate_evidencia_minima(evidencia_doc)
        if err_ev:
            return None, None, f"Validación evidencia: {err_ev}"

        # Regla de negocio: el agente solo puede crear reportes en su municipio
        rpt_mid = reporte_doc.get("municipio_id")
        # aceptar si rpt_mid es ObjectId o string que coincide con agente_municipio_id
        if isinstance(rpt_mid, ObjectId):
            ok = (rpt_mid == self.agente_municipio_id)
        else:
            ok = (str(rpt_mid) == str(self.agente_municipio_id))
        if not ok:
            return None, None, "Permiso denegado: el agente solo puede crear reportes en su municipio"

        client = getattr(self.mongo, "client", None)
        # Intentar transacción si está disponible y solicitado
        if use_transaction and client is not None:
            try:
                with client.start_session() as session:
                    with session.start_transaction():
                        rres = self.db.reporte.insert_one(reporte_doc, session=session)
                        evidencia_doc["reporte_id"] = rres.inserted_id
                        eres = self.db.evidencia.insert_one(evidencia_doc, session=session)
                        return rres.inserted_id, eres.inserted_id, None
            except (PyMongoError, Exception) as e:
                return None, None, f"Error en transacción: {type(e).__name__} {e}"

        # Inserción secuencial con rollback simple
        try:
            rres = self.db.reporte.insert_one(reporte_doc)
            evidencia_doc["reporte_id"] = rres.inserted_id
            eres = self.db.evidencia.insert_one(evidencia_doc)
            return rres.inserted_id, eres.inserted_id, None
        except PyMongoError as e:
            # rollback simple: borrar reporte si fue creado
            try:
                if 'rres' in locals() and rres.inserted_id:
                    self.db.reporte.delete_one({"_id": rres.inserted_id})
            except Exception:
                pass
            return None, None, f"Error al insertar: {type(e).__name__} {e}"

    # -----------------------
    # Actualizaciones permitidas (solo 'estado')
    # -----------------------
    def _validate_estado(self, estado: str) -> Optional[str]:
        if estado not in self.VALID_ESTADOS:
            return f"estado inválido. Valores permitidos: {', '.join(self.VALID_ESTADOS)}"
        return None

    def update_estado(self, reporte_id: ObjectId, nuevo_estado: str) -> Tuple[bool, Optional[str]]:
        """
        Actualiza únicamente el campo 'estado' de un reporte si pertenece al municipio del agente.
        Retorna (True, None) en éxito o (False, mensaje_error) en fallo.
        """
        err = self._validate_estado(nuevo_estado)
        if err:
            return False, err

        rpt = self.db.reporte.find_one({"_id": reporte_id})
        if not rpt:
            return False, "Reporte no encontrado"

        rpt_mid = rpt.get("municipio_id")
        if rpt_mid != self.agente_municipio_id and str(rpt_mid) != str(self.agente_municipio_id):
            return False, "Permiso denegado: reporte de otro municipio"

        try:
            res = self.db.reporte.update_one(
                {"_id": reporte_id},
                {"$set": {"estado": nuevo_estado, "fechaHora_server": self._now_utc()}}
            )
            if res.matched_count:
                return True, None
            return False, "No se actualizó el reporte"
        except PyMongoError as e:
            return False, f"Error al actualizar: {type(e).__name__} {e}"

    # -----------------------
    # Consistencia y auditoría
    # -----------------------
    def find_orphan_reports(self) -> List[ObjectId]:
        """
        Devuelve lista de reportes que no tienen evidencia asociada.
        Útil para auditoría.
        """
        reporte_ids_with_evidence = set(self.db.evidencia.distinct("reporte_id") or [])
        all_report_ids = self.db.reporte.distinct("_id") or []
        orphans = [rid for rid in all_report_ids if rid not in reporte_ids_with_evidence]
        return orphans

    def evidences_without_report(self) -> List[ObjectId]:
        """
        Devuelve evidencias cuyo reporte_id no existe en la colección reporte.
        """
        report_ids = set(self.db.reporte.distinct("_id") or [])
        evidencias = list(self.db.evidencia.find({}, {"_id": 1, "reporte_id": 1}))
        bad = [e["_id"] for e in evidencias if e.get("reporte_id") not in report_ids]
        return bad

# -----------------------
# Ejemplo de uso (para copiar en el notebook)
# -----------------------
if __name__ == "__main__":
    # En el notebook no se ejecuta este bloque; sirve como referencia.
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    class Wrapper: pass
    mongo = Wrapper(); mongo.db = client.mi_base; mongo.client = client

    agente_municipio_id = ObjectId("6a21d09b4076ce51229df8a4")  # reemplazar
    dao = AgenteMunicipalDAO(mongo, agente_municipio_id=agente_municipio_id)
    dao.ensure_indexes()

