"""
dao.py — Capa de Acceso a Datos (DAO) para ExomSystem / CivicTech
Base de datos: PostgreSQL + PostGIS

Clases:
    ConexionDB   → maneja la conexión psycopg2
    UsuarioDAO   → CRUD sobre la tabla 'usuarios'
    ReporteDAO   → CRUD sobre la tabla 'reportes'  (coordenadas via PostGIS)
    EvidenciaDAO → CRUD sobre la tabla 'evidencias'
"""

import psycopg2
from psycopg2.extras import RealDictCursor

import config_vars
from db_models.usuario   import Usuario
from db_models.reporte   import Reporte
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
    CRUD para la tabla 'usuarios'.

    Uso:
        with ConexionDB() as conn:
            dao = UsuarioDAO(conn)
            usuario = dao.crear(Usuario("Ana Pérez", "30123456", "ana@mail.com"))
    """

    def __init__(self, conn):
        self.conn = conn

    # ---- Crear ---------------------------------------------------------------

    def crear(self, usuario: Usuario) -> Usuario:
        """Inserta un nuevo usuario y devuelve el objeto con su id asignado."""
        sql = """
            INSERT INTO usuarios (nombre_completo, dni, email, reputacion_score)
            VALUES (%s, %s, %s, %s)
            RETURNING id_usuario;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (
                usuario.nombre_completo,
                usuario.dni,
                usuario.email,
                usuario.reputacion_score,
            ))
            usuario.id_usuario = cur.fetchone()[0]
        self.conn.commit()
        return usuario

    # ---- Leer ----------------------------------------------------------------

    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        """Devuelve un Usuario por su PK, o None si no existe."""
        sql = """
            SELECT id_usuario, nombre_completo, dni, email, reputacion_score
            FROM usuarios
            WHERE id_usuario = %s;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_usuario,))
            fila = cur.fetchone()
        if fila is None:
            return None
        return Usuario(
            nombre_completo=fila["nombre_completo"],
            dni=fila["dni"],
            email=fila["email"],
            reputacion_score=fila["reputacion_score"],
            id_usuario=fila["id_usuario"],
        )

    def obtener_por_email(self, email: str) -> Usuario | None:
        """Devuelve un Usuario por su email, o None si no existe."""
        sql = """
            SELECT id_usuario, nombre_completo, dni, email, reputacion_score
            FROM usuarios
            WHERE email = %s;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (email,))
            fila = cur.fetchone()
        if fila is None:
            return None
        return Usuario(
            nombre_completo=fila["nombre_completo"],
            dni=fila["dni"],
            email=fila["email"],
            reputacion_score=fila["reputacion_score"],
            id_usuario=fila["id_usuario"],
        )

    def obtener_todos(self) -> list[Usuario]:
        """Devuelve la lista completa de usuarios."""
        sql = """
            SELECT id_usuario, nombre_completo, dni, email, reputacion_score
            FROM usuarios
            ORDER BY id_usuario;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            filas = cur.fetchall()
        return [
            Usuario(
                nombre_completo=f["nombre_completo"],
                dni=f["dni"],
                email=f["email"],
                reputacion_score=f["reputacion_score"],
                id_usuario=f["id_usuario"],
            )
            for f in filas
        ]

    # ---- Actualizar ----------------------------------------------------------

    def actualizar_reputacion(self, id_usuario: int, nuevo_score: int) -> bool:
        """Actualiza el score de reputación. Devuelve True si se modificó algo."""
        sql = """
            UPDATE usuarios
            SET reputacion_score = %s
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
            UPDATE usuarios
            SET nombre_completo = %s,
                dni              = %s,
                email            = %s,
                reputacion_score = %s
            WHERE id_usuario = %s;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (
                usuario.nombre_completo,
                usuario.dni,
                usuario.email,
                usuario.reputacion_score,
                usuario.id_usuario,
            ))
            modificados = cur.rowcount
        self.conn.commit()
        return modificados > 0

    # ---- Eliminar ------------------------------------------------------------

    def eliminar(self, id_usuario: int) -> bool:
        """Elimina un usuario por su PK. Devuelve True si se borró algo."""
        sql = "DELETE FROM usuarios WHERE id_usuario = %s;"
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
    CRUD para la tabla 'reportes'.
    Las coordenadas GPS se almacenan como GEOMETRY(Point, 4326) en PostGIS.
    El campo coordenadas_gps en el modelo es una tupla (longitud, latitud).

    Uso:
        with ConexionDB() as conn:
            dao = ReporteDAO(conn)
            reporte = dao.crear(Reporte(
                id_usuario=1, id_tipo=2,
                patente_vehiculo="AB123CD",
                fecha_hora_dispositivo=datetime.now(),
                fecha_hora_servidor=datetime.now(),
                coordenadas_gps=(-66.8541, -29.4967),   # (lon, lat) Chilecito
            ))
    """

    def __init__(self, conn):
        self.conn = conn

    # ---- Helpers internos ----------------------------------------------------

    @staticmethod
    def _fila_a_reporte(fila: dict) -> Reporte:
        return Reporte(
            id_usuario=fila["id_usuario"],
            id_tipo=fila["id_tipo"],
            patente_vehiculo=fila["patente_vehiculo"],
            fecha_hora_dispositivo=fila["fecha_hora_dispositivo"],
            fecha_hora_servidor=fila["fecha_hora_servidor"],
            coordenadas_gps=(fila["longitud"], fila["latitud"]),
            estado_resolucion=fila["estado_resolucion"],
            id_reporte=fila["id_reporte"],
        )

    # ---- Crear ---------------------------------------------------------------

    def crear(self, reporte: Reporte) -> Reporte:
        """Inserta un nuevo reporte y devuelve el objeto con su id asignado."""
        lon, lat = reporte.coordenadas_gps
        sql = """
            INSERT INTO reportes
                (id_usuario, id_tipo, patente_vehiculo,
                 fecha_hora_dispositivo, fecha_hora_servidor,
                 coordenadas_gps, estado_resolucion)
            VALUES
                (%s, %s, %s, %s, %s,
                 ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                 %s)
            RETURNING id_reporte;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (
                reporte.id_usuario,
                reporte.id_tipo,
                reporte.patente_vehiculo,
                reporte.fecha_hora_dispositivo,
                reporte.fecha_hora_servidor,
                lon, lat,
                reporte.estado_resolucion,
            ))
            reporte.id_reporte = cur.fetchone()[0]
        self.conn.commit()
        return reporte

    # ---- Leer ----------------------------------------------------------------

    def obtener_por_id(self, id_reporte: int) -> Reporte | None:
        """Devuelve un Reporte por su PK, o None si no existe."""
        sql = """
            SELECT id_reporte, id_usuario, id_tipo, patente_vehiculo,
                   fecha_hora_dispositivo, fecha_hora_servidor,
                   ST_X(coordenadas_gps) AS longitud,
                   ST_Y(coordenadas_gps) AS latitud,
                   estado_resolucion
            FROM reportes
            WHERE id_reporte = %s;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_reporte,))
            fila = cur.fetchone()
        return None if fila is None else self._fila_a_reporte(fila)

    def obtener_por_usuario(self, id_usuario: int) -> list[Reporte]:
        """Devuelve todos los reportes de un usuario."""
        sql = """
            SELECT id_reporte, id_usuario, id_tipo, patente_vehiculo,
                   fecha_hora_dispositivo, fecha_hora_servidor,
                   ST_X(coordenadas_gps) AS longitud,
                   ST_Y(coordenadas_gps) AS latitud,
                   estado_resolucion
            FROM reportes
            WHERE id_usuario = %s
            ORDER BY fecha_hora_servidor DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_usuario,))
            filas = cur.fetchall()
        return [self._fila_a_reporte(f) for f in filas]

    def obtener_por_patente(self, patente: str) -> list[Reporte]:
        """Devuelve todos los reportes asociados a una patente."""
        sql = """
            SELECT id_reporte, id_usuario, id_tipo, patente_vehiculo,
                   fecha_hora_dispositivo, fecha_hora_servidor,
                   ST_X(coordenadas_gps) AS longitud,
                   ST_Y(coordenadas_gps) AS latitud,
                   estado_resolucion
            FROM reportes
            WHERE patente_vehiculo = %s
            ORDER BY fecha_hora_servidor DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (patente.upper(),))
            filas = cur.fetchall()
        return [self._fila_a_reporte(f) for f in filas]

    def obtener_por_estado(self, estado: str) -> list[Reporte]:
        """
        Devuelve reportes filtrados por estado.
        Estados válidos: 'Pendiente', 'En revisión', 'Aprobado', 'Rechazado'.
        """
        sql = """
            SELECT id_reporte, id_usuario, id_tipo, patente_vehiculo,
                   fecha_hora_dispositivo, fecha_hora_servidor,
                   ST_X(coordenadas_gps) AS longitud,
                   ST_Y(coordenadas_gps) AS latitud,
                   estado_resolucion
            FROM reportes
            WHERE estado_resolucion = %s
            ORDER BY fecha_hora_servidor DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (estado,))
            filas = cur.fetchall()
        return [self._fila_a_reporte(f) for f in filas]

    def obtener_en_radio(self, lon: float, lat: float, metros: int) -> list[Reporte]:
        """
        Devuelve todos los reportes dentro de un radio (metros) desde un punto.
        Útil para detectar zonas críticas con PostGIS.
        """
        sql = """
            SELECT id_reporte, id_usuario, id_tipo, patente_vehiculo,
                   fecha_hora_dispositivo, fecha_hora_servidor,
                   ST_X(coordenadas_gps) AS longitud,
                   ST_Y(coordenadas_gps) AS latitud,
                   estado_resolucion
            FROM reportes
            WHERE ST_DWithin(
                coordenadas_gps::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
            )
            ORDER BY fecha_hora_servidor DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (lon, lat, metros))
            filas = cur.fetchall()
        return [self._fila_a_reporte(f) for f in filas]

    def obtener_todos(self) -> list[Reporte]:
        """Devuelve todos los reportes."""
        sql = """
            SELECT id_reporte, id_usuario, id_tipo, patente_vehiculo,
                   fecha_hora_dispositivo, fecha_hora_servidor,
                   ST_X(coordenadas_gps) AS longitud,
                   ST_Y(coordenadas_gps) AS latitud,
                   estado_resolucion
            FROM reportes
            ORDER BY fecha_hora_servidor DESC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            filas = cur.fetchall()
        return [self._fila_a_reporte(f) for f in filas]

    # ---- Actualizar ----------------------------------------------------------

    def actualizar_estado(self, id_reporte: int, nuevo_estado: str) -> bool:
        """Cambia el estado de resolución de un reporte. Devuelve True si se modificó."""
        sql = """
            UPDATE reportes
            SET estado_resolucion = %s
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
        sql = "DELETE FROM reportes WHERE id_reporte = %s;"
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
    CRUD para la tabla 'evidencias'.
    Cada evidencia referencia un reporte y apunta al archivo en S3/GCS.

    Uso:
        with ConexionDB() as conn:
            dao = EvidenciaDAO(conn)
            ev = dao.crear(Evidencia(
                id_reporte=1,
                url_archivo_s3="https://bucket.s3.amazonaws.com/foto.jpg",
                hash_seguridad_sha256="a3f5c...",
            ))
    """

    def __init__(self, conn):
        self.conn = conn

    # ---- Helpers internos ----------------------------------------------------

    @staticmethod
    def _fila_a_evidencia(fila: dict) -> Evidencia:
        return Evidencia(
            id_reporte=fila["id_reporte"],
            url_archivo_s3=fila["url_archivo_s3"],
            hash_seguridad_sha256=fila["hash_seguridad_sha256"],
            id_evidencia=fila["id_evidencia"],
        )

    # ---- Crear ---------------------------------------------------------------

    def crear(self, evidencia: Evidencia) -> Evidencia:
        """Inserta una nueva evidencia y devuelve el objeto con su id asignado."""
        sql = """
            INSERT INTO evidencias (id_reporte, url_archivo_s3, hash_seguridad_sha256)
            VALUES (%s, %s, %s)
            RETURNING id_evidencia;
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (
                evidencia.id_reporte,
                evidencia.url_archivo_s3,
                evidencia.hash_seguridad_sha256,
            ))
            evidencia.id_evidencia = cur.fetchone()[0]
        self.conn.commit()
        return evidencia

    # ---- Leer ----------------------------------------------------------------

    def obtener_por_id(self, id_evidencia: int) -> Evidencia | None:
        """Devuelve una Evidencia por su PK, o None si no existe."""
        sql = """
            SELECT id_evidencia, id_reporte, url_archivo_s3, hash_seguridad_sha256
            FROM evidencias
            WHERE id_evidencia = %s;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_evidencia,))
            fila = cur.fetchone()
        return None if fila is None else self._fila_a_evidencia(fila)

    def obtener_por_reporte(self, id_reporte: int) -> list[Evidencia]:
        """Devuelve todas las evidencias asociadas a un reporte."""
        sql = """
            SELECT id_evidencia, id_reporte, url_archivo_s3, hash_seguridad_sha256
            FROM evidencias
            WHERE id_reporte = %s
            ORDER BY id_evidencia;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_reporte,))
            filas = cur.fetchall()
        return [self._fila_a_evidencia(f) for f in filas]

    def obtener_por_hash(self, hash_sha256: str) -> Evidencia | None:
        """
        Busca una evidencia por su hash SHA-256.
        Útil para detectar duplicados o validar integridad.
        """
        sql = """
            SELECT id_evidencia, id_reporte, url_archivo_s3, hash_seguridad_sha256
            FROM evidencias
            WHERE hash_seguridad_sha256 = %s;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (hash_sha256,))
            fila = cur.fetchone()
        return None if fila is None else self._fila_a_evidencia(fila)

    def obtener_todas(self) -> list[Evidencia]:
        """Devuelve todas las evidencias registradas."""
        sql = """
            SELECT id_evidencia, id_reporte, url_archivo_s3, hash_seguridad_sha256
            FROM evidencias
            ORDER BY id_evidencia;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            filas = cur.fetchall()
        return [self._fila_a_evidencia(f) for f in filas]

    # ---- Eliminar ------------------------------------------------------------

    def eliminar(self, id_evidencia: int) -> bool:
        """Elimina una evidencia por su PK. Devuelve True si se borró algo."""
        sql = "DELETE FROM evidencias WHERE id_evidencia = %s;"
        with self.conn.cursor() as cur:
            cur.execute(sql, (id_evidencia,))
            eliminados = cur.rowcount
        self.conn.commit()
        return eliminados > 0

    def eliminar_por_reporte(self, id_reporte: int) -> int:
        """Elimina todas las evidencias de un reporte. Devuelve la cantidad eliminada."""
        sql = "DELETE FROM evidencias WHERE id_reporte = %s;"
        with self.conn.cursor() as cur:
            cur.execute(sql, (id_reporte,))
            eliminados = cur.rowcount
        self.conn.commit()
        return eliminados
