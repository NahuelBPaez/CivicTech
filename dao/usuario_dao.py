# dao/usuario_dao.py
import os
import base64
import hashlib
import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, WriteError
from pymongo import ASCENDING

class UsuarioDAO:
    def __init__(self, mongo_dao):
        """
        mongo_dao: instancia de MongoDAO ya conectada
        La colección tiene un validator que exige:
        - nombre_apellido (string), dni (string), email (string), contrasena (string), municipio_id (objectId)
        """
        self.mongo = mongo_dao
        self.collection = self.mongo.db["usuario"]
        try:
            self._ensure_indexes()
        except Exception:
            # No interrumpir si hay duplicados existentes; revisar manualmente si falla.
            pass

    def _ensure_indexes(self):
        self.collection.create_index("dni", unique=True, name="uq_dni")
        self.collection.create_index("email", unique=True, name="uq_email")
        self.collection.create_index([("municipio_id", ASCENDING)], name="ix_municipio")

    # Helpers
    def _to_objectid(self, value):
        try:
            return ObjectId(value)
        except Exception:
            raise ValueError("ID inválido")

    def _hash_password(self, password, salt=None):
        """
        Devuelve string en formato 'salt$hash' (ambos en base64) para cumplir con validator que pide string.
        """
        if salt is None:
            salt = os.urandom(16)
        elif isinstance(salt, str):
            salt = base64.b64decode(salt)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        salt_b64 = base64.b64encode(salt).decode("utf-8")
        hash_b64 = base64.b64encode(dk).decode("utf-8")
        return f"{salt_b64}${hash_b64}"

    def _split_hashed(self, contrasena_str):
        try:
            salt_b64, hash_b64 = contrasena_str.split("$", 1)
            return salt_b64, hash_b64
        except Exception:
            return None, None

    def verify_password(self, password, contrasena_str):
        salt_b64, hash_b64 = self._split_hashed(contrasena_str)
        if not salt_b64 or not hash_b64:
            return False
        salt = base64.b64decode(salt_b64)
        _, candidate = self._hash_password(password, salt=salt).split("$", 1)
        return candidate == hash_b64

    # CRUD y reglas de negocio
    def create_user(self, user_doc):
        """
        Campos requeridos en la colección: nombre_apellido, dni, email, contrasena, municipio_id
        Reglas aplicadas:
         - dni único global
         - email único global
         - no permitir mismo dni en dos municipios distintos
         - verificar que municipio exista
        """
        required = ["nombre_apellido", "dni", "email", "contrasena", "municipio_id"]
        for k in required:
            if k not in user_doc or user_doc[k] is None or str(user_doc[k]).strip() == "":
                raise ValueError(f"Falta campo obligatorio: {k}")

        nombre_apellido = str(user_doc["nombre_apellido"]).strip()
        dni = str(user_doc["dni"]).strip()
        email = str(user_doc["email"]).strip().lower()
        municipio_id_raw = user_doc["municipio_id"]

        # Convertir municipio_id a ObjectId y validar existencia
        try:
            mid = self._to_objectid(municipio_id_raw)
        except ValueError:
            raise ValueError("municipio_id inválido")
        if not self.mongo.db.municipio.find_one({"_id": mid}):
            raise ValueError("El municipio indicado no existe")

        # Reglas de unicidad
        existing_dni = self.collection.find_one({"dni": {"$regex": f"^{dni}$", "$options": "i"}})
        if existing_dni:
            existing_mid = existing_dni.get("municipio_id")
            if existing_mid and str(existing_mid) != str(mid):
                raise ValueError("Ya existe un usuario con ese DNI en otro municipio")
            else:
                raise ValueError("Ya existe un usuario con ese DNI")

        if self.collection.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}}):
            raise ValueError("Ya existe un usuario con ese email")

        # Hashear la contraseña y guardarla en el campo 'contrasena' (string) para cumplir validator
        hashed = self._hash_password(str(user_doc["contrasena"]))

        # Construir documento conforme al validator
        doc = {
            "nombre_apellido": nombre_apellido,
            "dni": dni,
            "email": email,
            "contrasena": hashed,
            "municipio_id": mid,
            # campos opcionales
            "telefono": user_doc.get("telefono"),
            "reputacion": int(user_doc.get("reputacion")) if user_doc.get("reputacion") is not None else None,
            "rol": user_doc.get("rol", "usuario"),
            "created_at": user_doc.get("created_at") or datetime.datetime.utcnow()
        }

        # Eliminar claves None para no violar validaciones estrictas
        doc = {k: v for k, v in doc.items() if v is not None}

        try:
            res = self.collection.insert_one(doc)
            return res.inserted_id
        except WriteError as we:
            details = getattr(we, "details", None)
            if details:
                raise ValueError(f"Error de validación en la colección: {details}") from we
            raise
        except DuplicateKeyError as e:
            raise ValueError("Clave duplicada en la base de datos") from e

    def find_by_dni(self, dni):
        if not dni:
            return None
        return self.collection.find_one({"dni": {"$regex": f"^{str(dni).strip()}$", "$options": "i"}})

    def find_by_email(self, email):
        if not email:
            return None
        return self.collection.find_one({"email": {"$regex": f"^{str(email).strip().lower()}$", "$options": "i"}})

    def list_users(self, limit=50, skip=0, filtro=None):
        q = filtro or {}
        return list(self.collection.find(q).skip(int(skip)).limit(int(limit)))

    def update_email(self, usuario_id, new_email):
        oid = self._to_objectid(usuario_id)
        new_email_norm = str(new_email).strip().lower()
        existing = self.collection.find_one({"email": {"$regex": f"^{new_email_norm}$", "$options": "i"}, "_id": {"$ne": oid}})
        if existing:
            raise ValueError("Otro usuario ya usa ese email")
        res = self.collection.update_one({"_id": oid}, {"$set": {"email": new_email_norm}})
        return res.modified_count

    def update_password(self, usuario_id, new_password):
        oid = self._to_objectid(usuario_id)
        hashed = self._hash_password(new_password)
        res = self.collection.update_one({"_id": oid}, {"$set": {"contrasena": hashed}})
        return res.modified_count

    def delete(self, usuario_id):
        oid = self._to_objectid(usuario_id)
        res = self.collection.delete_one({"_id": oid})
        return res.deleted_count

    def count_by_municipio(self, municipio_id):
        mid = self._to_objectid(municipio_id)
        return self.collection.count_documents({"municipio_id": mid})
