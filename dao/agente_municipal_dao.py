def crear(self, agente_doc):
    required = ["nombre_apellido", "dni", "email", "rol", "municipio_id"]
    for k in required:
        if k not in agente_doc or agente_doc[k] is None or str(agente_doc[k]).strip() == "":
            raise ValueError(f"Falta campo obligatorio: {k}")

    nombre_apellido = str(agente_doc["nombre_apellido"]).strip()
    dni = str(agente_doc["dni"]).strip()
    email = str(agente_doc["email"]).strip().lower()
    rol = str(agente_doc["rol"]).strip()

    # Convertir municipio_id y validar existencia
    try:
        mid = self._to_objectid(agente_doc["municipio_id"])
    except ValueError:
        raise ValueError("municipio_id inválido")
    if not self.mongo.db.municipio.find_one({"_id": mid}):
        raise ValueError("El municipio indicado no existe")

    # Reglas de unicidad
    if self.collection.find_one({"dni": {"$regex": f"^{dni}$", "$options": "i"}}):
        raise ValueError("Ya existe un agente con ese DNI")
    if self.collection.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}}):
        raise ValueError("Ya existe un agente con ese email")

    doc = {
        "nombre_apellido": nombre_apellido,
        "dni": dni,
        "email": email,
        "rol": rol,
        "municipio_id": mid,
        "cargo": agente_doc.get("cargo"),
        "telefono": agente_doc.get("telefono"),
        "activo": bool(agente_doc.get("activo", True)),
        "acciones": agente_doc.get("acciones", []),  # array requerido por validator si existe
        "created_at": agente_doc.get("created_at") or datetime.datetime.now(datetime.timezone.utc),
        "updated_at": agente_doc.get("updated_at") or datetime.datetime.now(datetime.timezone.utc),
        "meta": agente_doc.get("meta", {})
    }

    # Eliminar claves None
    doc = {k: v for k, v in doc.items() if v is not None}

    try:
        res = self.collection.insert_one(doc)
        return res.inserted_id
    except DuplicateKeyError as e:
        raise ValueError("Clave duplicada en la base de datos") from e
    except WriteError as we:
        details = getattr(we, "details", None)
        if details:
            raise ValueError(f"Error de validación en la colección: {details}") from we
        raise

