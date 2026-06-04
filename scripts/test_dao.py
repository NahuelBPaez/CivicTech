# scripts/test_dao.py

import sys, os
# Agrega la raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dao.mongo_dao import MongoDAO

"""
Prueba mínima de la capa DAO para:
- conectar a MongoDB
- crear índices
- insertar municipio, usuario, reporte y evidencia
- ajustar reputación y verificar reglas básicas
Diseñado para ejecutarse localmente con la .env ya configurada.
"""

from dao.mongo_dao import MongoDAO
from bson import ObjectId
from datetime import datetime
import traceback

def main():
    dao = MongoDAO()
    try:
        db = dao.connect()
        print("Conectado a DB:", dao.db_name)

        # Asegurar índices
        dao.ensure_indexes()
        print("Índices creados/asegurados.")

        # 1) Insertar un municipio de prueba (si no existe)
        municipio = {
            "nombre": "Chilecito",
            "provincia": "La Rioja",
            "pais": "Argentina",
            "codigo_municipio": "CHL001",
            "contacto": {"email": "transito@chilecito.gob.ar", "telefono": "+54 3825 123456"}
        }
        existing = db.municipio.find_one({"codigo_municipio": municipio["codigo_municipio"]})
        if existing:
            municipio_id = existing["_id"]
            print("Municipio existente:", municipio_id)
        else:
            municipio_id = db.municipio.insert_one(municipio).inserted_id
            print("Municipio insertado:", municipio_id)

        # 2) Insertar un usuario de prueba (si no existe)
        usuario = {
            "nombre_apellido": "Test Usuario",
            "dni": "99999999",
            "reputacion": 50,
            "email": "test.usuario@example.com",
            "contrasena": "hash_demo",
            "municipio_id": municipio_id
        }
        existing_u = dao.find_usuario_by_dni(usuario["dni"])
        if existing_u:
            usuario_id = existing_u["_id"]
            print("Usuario existente:", usuario_id)
        else:
            usuario_id = dao.create_usuario(usuario)
            print("Usuario insertado:", usuario_id)

        # 3) Crear un reporte asociado al usuario y municipio
        reporte = {
            "usuario_id": usuario_id,
            "municipio_id": municipio_id,
            "patente_vehiculo": "ABC123",
            "fechaHora_dispositivo": datetime.utcnow(),
            "ubicacion": {"type": "Point", "coordinates": [-66.85, -29.42]},
            "estado": "Pendiente",
            "hash_evidencia": "sha256_demo",
            "descripcion": "Vehículo bloqueando rampa"
        }
        reporte_id = dao.create_reporte(reporte)
        print("Reporte insertado:", reporte_id)

        # 4) Añadir evidencia vinculada al reporte
        evidencia = {
            "reporte_id": reporte_id,
            "url_foto": "http://example.com/foto.jpg",
            "url_archivo_s3": "s3://bucket/foto.jpg",
            "hash_seguridad_sha": "sha256_ejemplo"
        }
        evidencia_id = dao.add_evidencia(evidencia)
        print("Evidencia insertada:", evidencia_id)

        # 5) Buscar reportes cercanos (ejemplo)
        cercanos = dao.find_reportes_near(-66.85, -29.42, max_meters=50)
        print(f"Reportes cercanos encontrados: {len(cercanos)}")
        for r in cercanos[:3]:
            print("-", r.get("_id"), r.get("patente_vehiculo"), r.get("estado"))

        # 6) Ajustar reputación del usuario (ejemplo atómico)
        updated_user = dao.ajustar_reputacion_usuario(usuario_id, -5)
        print("Reputación actualizada. Nuevo valor:", updated_user.get("reputacion"))

        # 7) Validación de negocio: usuario pertenece al municipio
        pertenece = dao.usuario_pertenece_municipio(usuario_id, municipio_id)
        print("Usuario pertenece al municipio:", pertenece)

        print("Prueba completada correctamente.")

    except Exception as e:
        print("Error durante la prueba:")
        traceback.print_exc()
    finally:
        dao.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    main()
