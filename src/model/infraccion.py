class Infraccion:
    def __init__(self, id_usuario, id_tipo, patente_vehiculo, fecha_hora_dispositivo, 
                 fecha_hora_servidor, coordenadas_gps, estado_resolucion="Pendiente", id_infraccion=None):
        self.id_infraccion = id_infraccion
        self.id_usuario = id_usuario
        self.id_tipo = id_tipo
        self.patente_vehiculo = patente_vehiculo
        self.fecha_hora_dispositivo = fecha_hora_dispositivo
        self.fecha_hora_servidor = fecha_hora_servidor
        # coordenadas_gps será una tupla (longitud, latitud) para facilitar el uso con PostGIS
        self.coordenadas_gps = coordenadas_gps 
        self.estado_resolucion = estado_resolucion
