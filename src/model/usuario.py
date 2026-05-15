class Usuario:
    def __init__(self, nombre_completo, dni, email, reputacion_score=100, id_usuario=None):
        self.id_usuario = id_usuario
        self.nombre_completo = nombre_completo
        self.dni = dni
        self.email = email
        self.reputacion_score = reputacion_score
