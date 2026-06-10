# dao/municipio_dao.py
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from pymongo import ASCENDING
from typing import Optional, List, Dict

class MunicipioDAO:
    """
    DAO para la colección 'municipio'.
    Encapsula validaciones, índices y operaciones seguras para que la capa de presentación
    (notebook) no contenga lógica de negocio.
    """
    def __init__(self, mongo_dao):
        """
        mongo_dao: instancia de MongoDAO ya conectada (por ejemplo: mongo).
        """
        self.mongo = mongo_dao
        self.collection = self.mongo.db["municipio"]
        try:
            self.ensure_indexes()
        except Exception:
            # No interrumpir la inicialización si la creación de índices falla por permisos.
            pass

    def ensure_indexes(self):
        """
        Crea índices útiles: único por codigo_municipio y compuesto (nombre, provincia).
        """
        self.collection.create_index("codigo_municipio", unique=True, name="uq_codigo_municipio")
        self.collection.create_index([("nombre", ASCENDING), ("provincia", ASCENDING)],
                                     unique=True, name="uq_nombre_provincia")

    # -------------------------
    # Lectura y listados
    # -------------------------
    def listar(self, limit: int = 10, skip: int = 0, filtro: Optional[Dict] = None) -> List[Dict]:
        """
        Retorna una lista de documentos.
        filtro: dict con condiciones Mongo (ej. {"provincia":"La Rioja"})
        """
        q = filtro or {}
        return list(self.collection.find(q).skip(int(skip)).limit(int(limit)))

    def obtener_por_id(self, municipio_id) -> Optional[Dict]:
        oid = self._to_objectid(municipio_id)
        return self.collection.find_one({"_id": oid})

    def obtener_por_codigo(self, codigo: str) -> Optional[Dict]:
        """
        Buscar por código de municipio (case-insensitive).
        """
        if not codigo:
            return None
        return self.collection.find_one({"codigo_municipio": {"$regex": f"^{codigo.strip()}$", "$options": "i"}})

    def obtener_email_contacto(self, municipio_id) -> Optional[str]:
        """
        Devuelve el email de contacto si existe en el subdocumento 'contacto'.
        """
        doc = self.obtener_por_id(municipio_id)
        if not doc:
            return None
        contacto = doc.get("contacto") or {}
        return contacto.get("email")

    # -------------------------
    # Inserción y actualización (con validaciones)
    # -------------------------
    def insertar(self, municipio_doc: Dict) -> ObjectId:
        """
        Insertar un municipio con validaciones:
          - campos obligatorios: nombre, provincia, pais, codigo_municipio
          - evita duplicados por codigo_municipio (case-insensitive)
          - evita duplicados por (nombre, provincia) (case-insensitive)
        Devuelve ObjectId insertado o lanza ValueError en caso de validación.
        """
        required = ["nombre", "provincia", "pais", "codigo_municipio"]
        for k in required:
            if k not in municipio_doc or municipio_doc[k] is None or str(municipio_doc[k]).strip() == "":
                raise ValueError(f"Falta campo obligatorio: {k}")

        nombre_norm = municipio_doc["nombre"].strip()
        provincia_norm = municipio_doc["provincia"].strip()
        codigo_norm = municipio_doc["codigo_municipio"].strip()

        if self.collection.find_one({"codigo_municipio": {"$regex": f"^{codigo_norm}$", "$options": "i"}}):
            raise ValueError(f"Ya existe un municipio con codigo_municipio='{municipio_doc['codigo_municipio']}'")

        if self.collection.find_one({
            "nombre": {"$regex": f"^{nombre_norm}$", "$options": "i"},
            "provincia": {"$regex": f"^{provincia_norm}$", "$options": "i"}
        }):
            raise ValueError(f"Ya existe un municipio con nombre='{municipio_doc['nombre']}' en la provincia '{municipio_doc['provincia']}'")

        try:
            res = self.collection.insert_one(municipio_doc)
            return res.inserted_id
        except DuplicateKeyError as e:
            raise ValueError("Clave duplicada en la base de datos") from e

    def actualizar(self, municipio_id, nuevos_campos: Dict) -> int:
        """
        Actualizar campos permitidos. Valida duplicados si se cambia codigo_municipio o nombre/provincia.
        Retorna modified_count (0 o 1).
        """
        oid = self._to_objectid(municipio_id)
        if "_id" in nuevos_campos:
            nuevos_campos.pop("_id")

        if "codigo_municipio" in nuevos_campos:
            codigo_norm = str(nuevos_campos["codigo_municipio"]).strip()
            existing = self.collection.find_one({
                "codigo_municipio": {"$regex": f"^{codigo_norm}$", "$options": "i"},
                "_id": {"$ne": oid}
            })
            if existing:
                raise ValueError(f"Otro municipio ya usa codigo_municipio='{nuevos_campos['codigo_municipio']}'")

        if "nombre" in nuevos_campos or "provincia" in nuevos_campos:
            nombre = str(nuevos_campos.get("nombre", "")).strip()
            provincia = str(nuevos_campos.get("provincia", "")).strip()
            doc = self.collection.find_one({"_id": oid})
            if not doc:
                raise ValueError("Municipio no encontrado")
            nombre_final = nombre if nombre else doc.get("nombre", "")
            provincia_final = provincia if provincia else doc.get("provincia", "")
            existing = self.collection.find_one({
                "nombre": {"$regex": f"^{nombre_final}$", "$options": "i"},
                "provincia": {"$regex": f"^{provincia_final}$", "$options": "i"},
                "_id": {"$ne": oid}
            })
            if existing:
                raise ValueError(f"Otro municipio ya tiene nombre='{nombre_final}' en la provincia '{provincia_final}'")

        res = self.collection.update_one({"_id": oid}, {"$set": nuevos_campos})
        return res.modified_count

    # -------------------------
    # Borrado seguro y utilidades
    # -------------------------
    def borrar(self, municipio_id) -> int:
        """
        Borra un municipio por id. Retorna deleted_count.
        """
        oid = self._to_objectid(municipio_id)
        res = self.collection.delete_one({"_id": oid})
        return res.deleted_count

    def borrar_si_sin_usuarios(self, municipio_id) -> int:
        """
        Borra el municipio solo si no hay usuarios asociados. Retorna deleted_count.
        Lanza ValueError si hay usuarios asociados.
        """
        oid = self._to_objectid(municipio_id)
        usuarios_count = self.contar_usuarios(oid)
        if usuarios_count > 0:
            raise ValueError(f"No se puede borrar: existen {usuarios_count} usuarios asociados al municipio.")
        return self.borrar(oid)

    def eliminar_por_codigo(self, codigo_municipio: str) -> dict:
        """
        Busca un municipio por codigo_municipio (case-insensitive) y lo elimina si no tiene usuarios asociados.
        Retorna dict con keys:
          - success (bool)
          - action (str): "deleted", "not_found", "delete_failed"
          - municipio_id (str|None)
          - message (str)
        Lanza ValueError para condiciones de negocio (por ejemplo: usuarios asociados).
        """
        if not codigo_municipio or not str(codigo_municipio).strip():
            raise ValueError("codigo_municipio inválido")

        doc = self.obtener_por_codigo(codigo_municipio)
        if not doc:
            return {"success": False, "action": "not_found", "municipio_id": None,
                    "message": f"No se encontró municipio con codigo_municipio='{codigo_municipio}'"}

        mid = doc["_id"]
        usuarios = self.contar_usuarios(mid)
        if usuarios > 0:
            raise ValueError(f"No se puede borrar: existen {usuarios} usuarios asociados al municipio '{codigo_municipio}'")

        deleted = self.borrar(mid)
        if deleted:
            return {"success": True, "action": "deleted", "municipio_id": str(mid),
                    "message": "Municipio eliminado correctamente"}
        else:
            return {"success": False, "action": "delete_failed", "municipio_id": str(mid),
                    "message": "Intento de borrado realizado pero deleted_count = 0"}

    def contar_usuarios(self, municipio_id) -> int:
        """
        Conteo de usuarios asociados (acepta ObjectId o string).
        """
        oid = municipio_id if isinstance(municipio_id, ObjectId) else self._to_objectid(municipio_id)
        return self.mongo.db.usuario.count_documents({"municipio_id": oid})

    def buscar_cercanos(self, longitude: float, latitude: float, max_meters: int = 1000, limit: int = 10) -> List[Dict]:
        """
        Buscar municipios por proximidad si tienen campo ubicacion GeoJSON.
        """
        q = {
            "ubicacion": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [float(longitude), float(latitude)]},
                    "$maxDistance": int(max_meters)
                }
            }
        }
        return list(self.collection.find(q).limit(int(limit)))

    # -------------------------
    # Helpers
    # -------------------------
    def _to_objectid(self, value) -> ObjectId:
        try:
            return ObjectId(value)
        except Exception:
            raise ValueError("municipio_id inválido")

