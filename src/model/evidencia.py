class Evidencia:
    def __init__(self, id_infraccion, url_archivo_s3, hash_seguridad_sha256, id_evidencia=None):
        self.id_evidencia = id_evidencia
        self.id_infraccion = id_infraccion
        self.url_archivo_s3 = url_archivo_s3
        self.hash_seguridad_sha256 = hash_seguridad_sha256
