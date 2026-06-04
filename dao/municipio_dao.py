# dao/municipio_dao.py
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from pymongo import ASCENDING

class MunicipioDAO:
    def __init__(self, mongo_dao):
        """
        mongo_dao: instancia de MongoDAO ya conectada (mongo = MongoDAO(); db = mongo.connect())
        """
        self.mongo = mongo_dao
        self.collection = self.mongo.db["municipio"]
        # Asegurar índices básicos al inicializar (no fuerza recreación si ya existen)
        try:
            self.ensure_indexes()
        except Exception:
            # No interrumpir la inicialización si la creación de índices falla por permisos;
            # la aplicación puede manejarlo en otro momento.
            pass

    def ensure_indexes(self):
        """
        Crea índices útiles: único por codigo_municipio y compuesto (nombre, provincia).
        Ejecutar una sola vez en un entorno controlado; fallará si hay duplicados existentes.
        """
        # índice único por codigo_municipio
        self.collection.create_index("codigo_municipio", unique=True, name="uq_codigo_municipio")
        # índice compuesto único por (nombre, provincia) para evitar duplicados en la misma provincia
        self.collection.create_index([("nombre", ASCENDING), ("provincia", ASCENDING)],
                                     unique=True, name="uq_nombre_provincia")

    # Listar municipios con paginación simple y filtro opcional
    def listar(self, limit=10, skip=0, filtro=None):
        """
        Retorna una lista de documentos.
        filtro: dict con condiciones Mongo (ej. {"provincia":"La Rioja"})
        """
        q = filtro or {}
        return list(self.collection.find(q).skip(int(skip)).limit(int(limit)))

    # Buscar por id
    def obtener_por_id(self, municipio_id):
        oid = self._to_objectid(municipio_id)
        return self.collection.find_one({"_id": oid})

    # Buscar por código de municipio (case-insensitive)
    def obtener_por_codigo(self, codigo):
        if not codigo:
            return None
        return self.collection.find_one({"codigo_municipio": {"$regex": f"^{codigo.strip()}$", "$options": "i"}})

    # Insertar con validación y chequeo de duplicados por nombre+provincia y codigo_municipio
    def insertar(self, municipio_doc):
        required = ["nombre", "provincia", "pais", "codigo_municipio"]
        for k in required:
            if k not in municipio_doc or municipio_doc[k] is None or str(municipio_doc[k]).strip() == "":
                raise ValueError(f"Falta campo obligatorio: {k}")

        # Normalizar para comparaciones
        nombre_norm = municipio_doc["nombre"].strip()
        provincia_norm = municipio_doc["provincia"].strip()
        codigo_norm = municipio_doc["codigo_municipio"].strip()

        # Verificar existencia por codigo_municipio (case-insensitive)
        if self.collection.find_one({"codigo_municipio": {"$regex": f"^{codigo_norm}$", "$options": "i"}}):
            raise ValueError(f"Ya existe un municipio con codigo_municipio='{municipio_doc['codigo_municipio']}'")

        # Verificar existencia por nombre + provincia (case-insensitive)
        if self.collection.find_one({
            "nombre": {"$regex": f"^{nombre_norm}$", "$options": "i"},
            "provincia": {"$regex": f"^{provincia_norm}$", "$options": "i"}
        }):
            raise ValueError(f"Ya existe un municipio con nombre='{municipio_doc['nombre']}' en la provincia '{municipio_doc['provincia']}'")

        try:
            res = self.collection.insert_one(municipio_doc)
            return res.inserted_id
        except DuplicateKeyError as e:
            # Propagar como ValueError para manejo uniforme en la capa superior
            raise ValueError("Clave duplicada en la base de datos") from e

    # Actualizar campos permitidos
    def actualizar(self, municipio_id, nuevos_campos):
        oid = self._to_objectid(municipio_id)
        # Evitar sobrescribir _id
        if "_id" in nuevos_campos:
            nuevos_campos.pop("_id")
        # Si se actualiza codigo_municipio o nombre/provincia, validar duplicados mínimos
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
            # Si uno de los dos no se provee, obtener del documento actual
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

    # Borrar municipio (retorna deleted_count)
    def borrar(self, municipio_id):
        oid = self._to_objectid(municipio_id)
        res = self.collection.delete_one({"_id": oid})
        return res.deleted_count

    # Conteo de usuarios asociados (útil para checks antes de borrar)
    def contar_usuarios(self, municipio_id):
        oid = self._to_objectid(municipio_id)
        return self.mongo.db.usuario.count_documents({"municipio_id": oid})

    # Buscar municipios por proximidad si tienen campo ubicacion GeoJSON
    def buscar_cercanos(self, longitude, latitude, max_meters=1000, limit=10):
        q = {
            "ubicacion": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [float(longitude), float(latitude)]},
                    "$maxDistance": int(max_meters)
                }
            }
        }
        return list(self.collection.find(q).limit(int(limit)))

    # Helper: convertir a ObjectId o lanzar ValueError
    def _to_objectid(self, value):
        try:
            return ObjectId(value)
        except Exception:
            raise ValueError("municipio_id inválido")
