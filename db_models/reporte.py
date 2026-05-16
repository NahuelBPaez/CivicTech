class Reporte:
    def __init__(self, id_usuario, id_tipo, patente_vehiculo, fecha_hora_dispositivo,
                 fecha_hora_servidor, coordenadas_gps, estado_resolucion="Pendiente", id_reporte=None):
        self.id_reporte = id_reporte
        self.id_usuario = id_usuario
        self.id_tipo = id_tipo
        self.patente_vehiculo = patente_vehiculo
        self.fecha_hora_dispositivo = fecha_hora_dispositivo
        self.fecha_hora_servidor = fecha_hora_servidor
        # coordenadas_gps: tupla (longitud, latitud) — orden PostGIS: X=lon, Y=lat
        self.coordenadas_gps = coordenadas_gps
        self.estado_resolucion = estado_resolucion

    def __repr__(self):
        return (f"Reporte(id={self.id_reporte}, patente={self.patente_vehiculo}, "
                f"estado={self.estado_resolucion})")
