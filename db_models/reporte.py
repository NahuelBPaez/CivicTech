from datetime import datetime
from typing import Tuple

class Reporte:
    def __init__(self, id_usuario: int, patente_vehiculo: str, fecha_hora_dispositivo: datetime,
                 ubicacion: Tuple[float, float], descripcion: str = None, hash_evidencia: str = None,
                 estado: str = 'Pendiente', fecha_hora_server: datetime = None, id_reporte: int = None):
        self.id_reporte = id_reporte
        self.id_usuario = id_usuario
        self.patente_vehiculo = patente_vehiculo
        self.fecha_hora_dispositivo = fecha_hora_dispositivo
        self.fecha_hora_server = fecha_hora_server
        self.ubicacion = ubicacion  # Formato tupla: (longitud, latitud)
        self.estado = estado
        self.hash_evidencia = hash_evidencia
        self.descripcion = descripcion

    def __repr__(self):
        return (f"Reporte(id={self.id_reporte}, patente={self.patente_vehiculo}, "
                f"estado={self.estado})")
