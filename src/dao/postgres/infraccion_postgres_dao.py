import psycopg2
from src.dao.interfaces_dao import InfraccionDAO
from src.models.infraccion import Infraccion

class InfraccionPostgresDAO(InfraccionDAO):
    def __init__(self, conexion_db):
        self.db = conexion_db

    def reportar(self, infraccion: Infraccion) -> int:
        # ST_SetSRID y ST_MakePoint convierten la tupla (lon, lat) en un punto geográfico real para PostGIS
        sql = """
            INSERT INTO infracciones 
            (id_usuario, id_tipo, patente_vehiculo, fecha_hora_dispositivo, fecha_hora_servidor, coordenadas_gps, estado_resolucion) 
            VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
            RETURNING id_infraccion;
        """
        try:
            with self.db.cursor() as cursor:
                # Separamos la tupla en longitud y latitud para inyectarla en la consulta SQL
                lon, lat = infraccion.coordenadas_gps 
                
                cursor.execute(sql, (
                    infraccion.id_usuario, 
                    infraccion.id_tipo, 
                    infraccion.patente_vehiculo, 
                    infraccion.fecha_hora_dispositivo, 
                    infraccion.fecha_hora_servidor, 
                    lon, lat,  # Van separados para la función ST_MakePoint
                    infraccion.estado_resolucion
                ))
                
                # Capturamos el ID que la base de datos generó automáticamente
                nuevo_id = cursor.fetchone()[0]
                self.db.commit()
                return nuevo_id
                
        except psycopg2.Error as e:
            print(f"Error en BD al registrar infracción: {e}")
            self.db.rollback()
            return None
