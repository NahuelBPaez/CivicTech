import psycopg2
from src.dao.interfaces_dao import UsuarioDAO
from src.models.usuario import Usuario

class UsuarioPostgresDAO(UsuarioDAO):
    def __init__(self, conexion_db):
        self.db = conexion_db

    def registrar(self, usuario: Usuario) -> bool:
        sql = """
            INSERT INTO usuarios (nombre_completo, dni, email, reputacion_score) 
            VALUES (%s, %s, %s, %s);
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(sql, (usuario.nombre_completo, usuario.dni, usuario.email, usuario.reputacion_score))
                self.db.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error en BD: {e}")
            self.db.rollback()
            return False
