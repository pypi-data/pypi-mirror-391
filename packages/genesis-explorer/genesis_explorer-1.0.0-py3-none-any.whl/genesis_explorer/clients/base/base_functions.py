"""Módulo que define el contrato para los clientes de servicios de Cloud Functions."""

# Librerías Externas.
from abc import ABC, abstractmethod

# Librerías Internas.
from migracion_gcp.lib.clients.base.core.singleton import SingletonMeta


class BaseFunction(ABC, metaclass = SingletonMeta):
    """Clase que define un cliente para la comunicación con Cloud Functions."""
    
    @abstractmethod
    def create_function(self, **kwargs) -> None:
        """Método que, dada la ruta a su archivo zip (que contiene el script de la función
        y sus requirements) en GCS, crea una Cloud Function en GCP."""

        raise NotImplementedError("Si tu clase implementa el contrato BaseFunction, debes implementar el método 'create_function'.")
