"""Módulo que define la clase base para las Factories de servicios de nube."""

# Librerías Externas.
from abc import ABC, abstractmethod


class CloudAbstractFactory(ABC):
    """Clase que define el contrato para la creación de Factories."""

    @abstractmethod
    def create_database_service(self,
                                *args, **kwargs) -> None:
        """Método que define el contrato para la creación de servicios de bases de datos."""

        raise NotImplementedError("Si tu clase implementa el contrato CloudFactory, debes implementar el método 'create_database_service'.")
    
    @abstractmethod
    def create_storage_service(self, *args, **kwargs) -> None:
        """Método que define el contrato para la creación de servicios de almacenamiento."""

        raise NotImplementedError("Si tu clase implementa el contrato CloudFactory, debes implementar el método 'create_storage_service'.")
    
    @abstractmethod
    def create_messaging_service(self, *args, **kwargs) -> None:
        """Método que define el contrato para la creación de servicios de mensajería."""

        raise NotImplementedError("Si tu clase implementa el contrato CloudFactory, debes implementar el método 'create_messaging_service'.")
    
    @abstractmethod
    def create_function_service(self, *args, **kwargs) -> None:
        """Método que define el contrato para la creación de servicios de Cloud Functions."""

        raise NotImplementedError("Si tu clase implementa el contrato CloudFactory, debes implementar el método 'create_function_service'.")
