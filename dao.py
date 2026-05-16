"""
dao.py — Capa de Acceso a Datos (DAO) para ExomSystem / CivicTech
Base de datos: PostgreSQL + PostGIS

Clases:
    ConexionDB   → maneja la conexión psycopg2
    UsuarioDAO   → CRUD sobre la tabla 'Usuario'
    ReporteDAO   → CRUD sobre la tabla 'Reporte'  (coordenadas via PostGIS)
    EvidenciaDAO → CRUD sobre la tabla 'Evidencia'
"""

import psycopg2
from psycopg2.extras import RealDictCursor

import config_vars
from db_models.usuario import Usuario
from db_models.reporte import Reporte
from db_models.evidencia import Evidencia


# ---------------------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------------------

class ConexionDB:
    """Abre y cierra la conexión a PostgreSQL."""

    def __init__(self):
        self.conn = None

    def conectar(self):
        self.conn = psycopg2.connect(
            host=config_vars.DB_HOST,
            port=config_vars.DB_PORT,
            dbname=config_vars.DB_NAME,
            user=config_vars.DB_USER,
            password=config_vars.DB_PASSWORD,
        )
        return self.conn

    def cerrar(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

    # Soporte de context manager: with ConexionDB() as conn:
    def __enter__(self):
        return self.conectar()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar()
        return False  # no silencia excepciones


# ---------------------------------------------------------------------------
# UsuarioDAO
# ---------------------------------------------------------------------------

class UsuarioDAO:
    """
    CRUD para la tabla 'Usuario'.
    """

    def __init__(self, conn):
        self.conn = conn

    # ---- Crear ---------------------------------------------------------------

    def crear(self, usuario: Usuario) -> Usuario:
        """Inserta un nuevo usuario y devuelve el objeto con su id asignado."""
        sql = """
            INSERT INTO "usuario" (nombre_apellido, dni, email, contrasena, reputacion)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_usuario;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (
                usuario.nombre_completo,
                usuario.dni,
                usuario.email,
                usuario.contrasena,
                usuario.reputacion_score,
            ))
            usuario.id_usuario = cur.fetchone()[0]
        self.conn.commit()
        return usuario

    # ---- Leer ----------------------------------------------------------------

    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        """Devuelve un Usuario por su PK, o None si no existe."""
        sql = """
            SELECT id_usuario, nombre_apellido, dni, email, contrasena, reputacion
            FROM "usuario"
            WHERE id_usuario = %s;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_usuario,))
            fila = cur.fetchone()
        if fila is None:
            return None
        return Usuario(
            nombre_completo=fila["nombre_apellido"],
            dni=fila["dni"],
            email=fila["email"],
            contrasena=fila["contrasena"],
            reputacion_score=fila["reputacion"],
            id_usuario=fila["id_usuario"],
        )

    def obtener_por_email(self, email: str) -> Usuario | None:
        """Devuelve un Usuario por su email, o None si no existe."""
        sql = """
            SELECT id_usuario, nombre_apellido, dni, email, contrasena, reputacion
            FROM "usuario"
            WHERE email = %s;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (email,))
            fila = cur.fetchone()
        if fila is None:
            return None
        return Usuario(
            nombre_completo=fila["nombre_apellido"],
            dni=fila["dni"],
            email=fila["email"],
            contrasena=fila["contrasena"],
            reputacion_score=fila["reputacion"],
            id_usuario=fila["id_usuario"],
        )

    def obtener_todos(self) -> list[Usuario]:
        """Devuelve la lista completa de usuarios."""
        sql = """
            SELECT id_usuario, nombre_apellido, dni, email, contrasena, reputacion
            FROM "usuario"
            ORDER BY id_usuario;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            filas = cur.fetchall()
        return [
            Usuario(
                nombre_completo=f["nombre_apellido"],
                dni=f["dni"],
                email=f["email"],
                contrasena=f["contrasena"],
                reputacion_score=f["reputacion"],
                id_usuario=f["id_usuario"],
            )
            for f in filas
        ]

    # ---- Actualizar ----------------------------------------------------------

    def actualizar_reputacion(self, id_usuario: int, nuevo_score: int) -> bool:
        """Actualiza el score de reputación. Devuelve True si se modificó algo."""
        sql = """
            UPDATE "usuario"
            SET reputacion = %s
            WHERE id_usuario = %s;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (nuevo_score, id_usuario))
            modificados = cur.rowcount
        self.conn.commit()
        return modificados > 0

    def actualizar(self, usuario: Usuario) -> bool:
        """Actualiza todos los campos de un usuario. Devuelve True si se modificó algo."""
        sql = """
            UPDATE "usuario"
            SET nombre_apellido = %s,
                dni             = %s,
                email           = %s,
                contrasena      = %s,
                reputacion      = %s
            WHERE id_usuario = %s;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (
                usuario.nombre_completo,
                usuario.dni,
                usuario.email,
                usuario.contrasena,
                usuario.reputacion_score,
                usuario.id_usuario,
            ))
            modificados = cur.rowcount
        self.conn.commit()
        return modificados > 0

    # ---- Eliminar ------------------------------------------------------------

    def eliminar(self, id_usuario: int) -> bool:
        """Elimina un usuario por su PK. Devuelve True si se borró algo."""
        sql = 'DELETE FROM "usuario" WHERE id_usuario = %s;'
        with self.conn.cursor() as cur:
            cur.execute(sql, (id_usuario,))
            eliminados = cur.rowcount
        self.conn.commit()
        return eliminados > 0


# ---------------------------------------------------------------------------
# ReporteDAO
# ---------------------------------------------------------------------------

class ReporteDAO:
    """
    CRUD para la tabla 'Reporte'.
    """

    def __init__(self, conn):
        self.conn = conn

    # ---- Helpers internos ----------------------------------------------------

    @staticmethod
    def _fila_a_reporte(fila: dict) -> Reporte:
        # BUGFIX: eliminado id_tipo (no existe en Reporte),
        #         corregidos nombres: ubicacion, estado, fecha_hora_server
        return Reporte(
            id_usuario=fila["id_usuario"],
            patente_vehiculo=fila["patente_vehiculo"],
            fecha_hora_dispositivo=fila["fechahora_dispositivo"],
            fecha_hora_server=fila["fechahora_server"],
            ubicacion=(fila["longitud"], fila["latitud"]),
            estado=fila["estado"],
            id_reporte=fila["id_reporte"],
        )

    # ---- Crear ---------------------------------------------------------------

    def crear(self, reporte: Reporte) -> Reporte:
        """Inserta un nuevo reporte y devuelve el objeto con su id asignado."""
        # BUGFIX: reporte.ubicacion (no coordenadas_gps), reporte.estado (no estado_resolucion)
        lon, lat = reporte.ubicacion
        sql = """
            INSERT INTO "reporte"
                (id_usuario, patente_vehiculo, "fechahora_dispositivo",
                 ubicacion, estado, hash_evidencia, descripcion)
            VALUES
                (%s, %s, %s,
                 ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                 %s, %s, %s)
            RETURNING id_reporte, "fechahora_server";
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (
                reporte.id_usuario,
                reporte.patente_vehiculo,
                reporte.fecha_hora_dispositivo,
                lon, lat,
                reporte.estado,
                reporte.hash_evidencia,
                reporte.descripcion,
            ))
            res = cur.fetchone()
            reporte.id_reporte = res[0]
            reporte.fecha_hora_server = res[1]
        self.conn.commit()
        return reporte

    # ---- Leer ----------------------------------------------------------------

    def obtener_por_id(self, id_reporte: int) -> Reporte | None:
        """Devuelve un Reporte por su PK, o None si no existe."""
        sql = """
            SELECT id_reporte, id_usuario, patente_vehiculo,
                   "fechahora_dispositivo", "fechahora_server",
                   ST_X(ubicacion) AS longitud,
                   ST_Y(ubicacion) AS latitud,
                   estado
            FROM "reporte"
            WHERE id_reporte = %s;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_reporte,))
            fila = cur.fetchone()
        return None if fila is None else self._fila_a_reporte(fila)

    def obtener_por_usuario(self, id_usuario: int) -> list[Reporte]:
        """Devuelve todos los reportes de un usuario."""
        sql = """
            SELECT id_reporte, id_usuario, patente_vehiculo,
                   "fechahora_dispositivo", "fechahora_server",
                   ST_X(ubicacion) AS longitud,
                   ST_Y(ubicacion) AS latitud,
                   estado
            FROM "reporte"
            WHERE id_usuario = %s
            ORDER BY "fechahora_server" DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_usuario,))
            filas = cur.fetchall()
        return [self._fila_a_reporte(f) for f in filas]

    def obtener_por_patente(self, patente: str) -> list[Reporte]:
        """Devuelve todos los reportes asociados a una patente."""
        sql = """
            SELECT id_reporte, id_usuario, patente_vehiculo,
                   "fechahora_dispositivo", "fechahora_server",
                   ST_X(ubicacion) AS longitud,
                   ST_Y(ubicacion) AS latitud,
                   estado
            FROM "reporte"
            WHERE patente_vehiculo = %s
            ORDER BY "fechahora_server" DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (patente.upper(),))
            filas = cur.fetchall()
        return [self._fila_a_reporte(f) for f in filas]

    def obtener_por_estado(self, estado: str) -> list[Reporte]:
        """Devuelve reportes filtrados por estado."""
        sql = """
            SELECT id_reporte, id_usuario, patente_vehiculo,
                   "fechahora_dispositivo", "fechahora_server",
                   ST_X(ubicacion) AS longitud,
                   ST_Y(ubicacion) AS latitud,
                   estado
            FROM "reporte"
            WHERE estado = %s
            ORDER BY "fechahora_server" DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (estado,))
            filas = cur.fetchall()
        return [self._fila_a_reporte(f) for f in filas]

    def obtener_en_radio(self, lon: float, lat: float, metros: int) -> list[Reporte]:
        """Devuelve todos los reportes dentro de un radio (metros) desde un punto."""
        sql = """
            SELECT id_reporte, id_usuario, patente_vehiculo,
                   "fechahora_dispositivo", "fechahora_server",
                   ST_X(ubicacion) AS longitud,
                   ST_Y(ubicacion) AS latitud,
                   estado
            FROM "reporte"
            WHERE ST_DWithin(
                ubicacion::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
            )
            ORDER BY "fechahora_server" DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (lon, lat, metros))
            filas = cur.fetchall()
        return [self._fila_a_reporte(f) for f in filas]

    def obtener_todos(self) -> list[Reporte]:
        """Devuelve todos los reportes."""
        sql = """
            SELECT id_reporte, id_usuario, patente_vehiculo,
                   "fechahora_dispositivo", "fechahora_server",
                   ST_X(ubicacion) AS longitud,
                   ST_Y(ubicacion) AS latitud,
                   estado
            FROM "reporte"
            ORDER BY "fechahora_server" DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            filas = cur.fetchall()
        return [self._fila_a_reporte(f) for f in filas]

    # ---- Actualizar ----------------------------------------------------------

    def actualizar_estado(self, id_reporte: int, nuevo_estado: str) -> bool:
        """Cambia el estado de resolución de un reporte."""
        sql = """
            UPDATE "reporte"
            SET estado = %s
            WHERE id_reporte = %s;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (nuevo_estado, id_reporte))
            modificados = cur.rowcount
        self.conn.commit()
        return modificados > 0

    # ---- Eliminar ------------------------------------------------------------

    def eliminar(self, id_reporte: int) -> bool:
        """Elimina un reporte por su PK. Devuelve True si se borró algo."""
        sql = 'DELETE FROM "reporte" WHERE id_reporte = %s;'
        with self.conn.cursor() as cur:
            cur.execute(sql, (id_reporte,))
            eliminados = cur.rowcount
        self.conn.commit()
        return eliminados > 0


# ---------------------------------------------------------------------------
# EvidenciaDAO
# ---------------------------------------------------------------------------

class EvidenciaDAO:
    """
    CRUD para la tabla 'Evidencia'.
    """

    def __init__(self, conn):
        self.conn = conn

    # ---- Helpers internos ----------------------------------------------------

    @staticmethod
    def _fila_a_evidencia(fila: dict) -> Evidencia:
        # BUGFIX: id_infraccion (no id_reporte), hash_seguridad_sha (no hash_seguridad_sha256)
        return Evidencia(
            id_infraccion=fila["id_infraccion"],
            url_archivo_s3=fila["url_archivo_s3"],
            hash_seguridad_sha=fila["hash_seguridad_sha"],
            id_evidencia=fila["id_evidencia"],
        )

    # ---- Crear ---------------------------------------------------------------

    def crear(self, evidencia: Evidencia) -> Evidencia:
        """Inserta una nueva evidencia y devuelve el objeto con su id asignado."""
        sql = """
            INSERT INTO "evidencia" (id_infraccion, url_foto, url_archivo_s3, hash_seguridad_sha)
            VALUES (%s, %s, %s, %s)
            RETURNING id_evidencia;
        """
        with self.conn.cursor() as cur:
            # BUGFIX: evidencia.id_infraccion (no id_reporte), evidencia.hash_seguridad_sha (no sha256)
            cur.execute(sql, (
                evidencia.id_infraccion,
                evidencia.url_foto,
                evidencia.url_archivo_s3,
                evidencia.hash_seguridad_sha,
            ))
            evidencia.id_evidencia = cur.fetchone()[0]
        self.conn.commit()
        return evidencia

    # ---- Leer ----------------------------------------------------------------

    def obtener_por_id(self, id_evidencia: int) -> Evidencia | None:
        """Devuelve una Evidencia por su PK, o None si no existe."""
        sql = """
            SELECT id_evidencia, id_infraccion, url_foto, url_archivo_s3, hash_seguridad_sha
            FROM "evidencia"
            WHERE id_evidencia = %s;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_evidencia,))
            fila = cur.fetchone()
        return None if fila is None else self._fila_a_evidencia(fila)

    def obtener_por_reporte(self, id_reporte: int) -> list[Evidencia]:
        """Devuelve todas las evidencias asociadas a un reporte."""
        sql = """
            SELECT id_evidencia, id_infraccion, url_foto, url_archivo_s3, hash_seguridad_sha
            FROM "evidencia"
            WHERE id_infraccion = %s
            ORDER BY id_evidencia;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_reporte,))
            filas = cur.fetchall()
        return [self._fila_a_evidencia(f) for f in filas]

    def obtener_por_hash(self, hash_sha256: str) -> Evidencia | None:
        """Busca una evidencia por su checksum hash."""
        sql = """
            SELECT id_evidencia, id_infraccion, url_foto, url_archivo_s3, hash_seguridad_sha
            FROM "evidencia"
            WHERE hash_seguridad_sha = %s;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (hash_sha256,))
            fila = cur.fetchone()
        return None if fila is None else self._fila_a_evidencia(fila)

    def obtener_todas(self) -> list[Evidencia]:
        """Devuelve todas las evidencias registradas."""
        sql = """
            SELECT id_evidencia, id_infraccion, url_foto, url_archivo_s3, hash_seguridad_sha
            FROM "evidencia"
            ORDER BY id_evidencia;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            filas = cur.fetchall()
        return [self._fila_a_evidencia(f) for f in filas]

    # ---- Eliminar ------------------------------------------------------------

    def eliminar(self, id_evidencia: int) -> bool:
        """Elimina una evidencia por su PK."""
        sql = 'DELETE FROM "evidencia" WHERE id_evidencia = %s;'
        with self.conn.cursor() as cur:
            cur.execute(sql, (id_evidencia,))
            eliminados = cur.rowcount
        self.conn.commit()
        return eliminados > 0

    def eliminar_por_reporte(self, id_reporte: int) -> int:
        """Elimina todas las evidencias de un reporte."""
        sql = 'DELETE FROM "evidencia" WHERE id_infraccion = %s;'
        with self.conn.cursor() as cur:
            cur.execute(sql, (id_reporte,))
            eliminados = cur.rowcount
        self.conn.commit()
        return eliminados
