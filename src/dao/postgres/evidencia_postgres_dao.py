import psycopg2
from src.dao.interfaces_dao import EvidenciaDAO
from src.models.evidencia import Evidencia

class EvidenciaPostgresDAO(EvidenciaDAO):
    def __init__(self, conexion_db):
        self.db = conexion_db

    def guardar(self, evidencia: Evidencia) -> bool:
        sql = """
            INSERT INTO evidencias (id_infraccion, url_archivo_s3, hash_seguridad_sha256) 
            VALUES (%s, %s, %s);
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(sql, (
                    evidencia.id_infraccion, 
                    evidencia.url_archivo_s3, 
                    evidencia.hash_seguridad_sha256
                ))
                self.db.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error en BD al guardar evidencia: {e}")
            self.db.rollback()
            return False
