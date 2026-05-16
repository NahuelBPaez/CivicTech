class Evidencia:
    def __init__(self, id_reporte, url_archivo_s3, hash_seguridad_sha256, id_evidencia=None):
        self.id_evidencia = id_evidencia
        self.id_reporte = id_reporte
        self.url_archivo_s3 = url_archivo_s3
        self.hash_seguridad_sha256 = hash_seguridad_sha256

    def __repr__(self):
        return (f"Evidencia(id={self.id_evidencia}, reporte={self.id_reporte}, "
                f"hash={self.hash_seguridad_sha256[:12]}...)")
