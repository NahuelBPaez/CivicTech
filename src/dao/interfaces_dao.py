from abc import ABC, abstractmethod
from src.models.usuario import Usuario
from src.models.infraccion import Infraccion
from src.models.evidencia import Evidencia

class UsuarioDAO(ABC):
    @abstractmethod
    def registrar(self, usuario: Usuario) -> bool:
        pass

class InfraccionDAO(ABC):
    @abstractmethod
    def reportar(self, infraccion: Infraccion) -> int:
        # Devuelve el id_infraccion generado para poder asociarle las evidencias después
        pass

class EvidenciaDAO(ABC):
    @abstractmethod
    def guardar(self, evidencia: Evidencia) -> bool:
        pass
