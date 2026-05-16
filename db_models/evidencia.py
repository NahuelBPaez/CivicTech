class Evidencia:
    def __init__(self, id_infraccion: int, url_foto: str = None, url_archivo_s3: str = None,
                 hash_seguridad_sha: str = None, id_evidencia: int = None):
        self.id_evidencia = id_evidencia
        self.id_infraccion = id_infraccion  # Se conecta con id_reporte de la tabla Reporte
        self.url_foto = url_foto
        self.url_archivo_s3 = url_archivo_s3
        self.hash_seguridad_sha = hash_seguridad_sha

    def __repr__(self):
        hash_preview = self.hash_seguridad_sha[:12] if self.hash_seguridad_sha else "None"
        return (f"Evidencia(id={self.id_evidencia}, reporte={self.id_infraccion}, "
                f"hash={hash_preview}...)")
