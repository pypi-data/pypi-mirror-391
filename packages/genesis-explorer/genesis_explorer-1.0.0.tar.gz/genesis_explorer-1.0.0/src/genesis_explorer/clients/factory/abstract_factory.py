"""Módulo que define la clase abstracta para las Factories de servicios de nube."""

# Librerías Externas.
from typing import Dict, Type

# Librerías Internas.
from migracion_gcp.lib.clients.base.base_storage import BaseStorage
from migracion_gcp.lib.clients.base.base_database import BaseDatabase
from migracion_gcp.lib.clients.base.base_functions import BaseFunction
from migracion_gcp.lib.clients.base.base_messaging import BaseMessaging

from migracion_gcp.lib.clients.factory.base import CloudAbstractFactory
from migracion_gcp.lib.clients.factory.gcp_factory import GCPAbstractFactory


class CloudFactory:
    """Clase que define el contrato para la creación de Factories de servicios de nube."""

    _registry: Dict[str, Type[CloudAbstractFactory]] = {"gcp": GCPAbstractFactory, 
                                                        "aws": "AWSFactory"}

    @classmethod
    def create_database_service(cls,
                                cloud_provider: str,
                                **kwargs) -> BaseDatabase:
        """Método que retorna la Factory de servicios de nube."""

        if cloud_provider not in cls._registry:
            raise ValueError(f"El proveedor de nube {cloud_provider} no está registrado.")

        factory = cls._registry.get(cloud_provider)
        return factory.create_database_service(**kwargs)
    
    @classmethod
    def create_storage_service(cls,
                               cloud_provider: str,
                               **kwargs) -> BaseStorage:
        """Método que retorna la Factory de servicios de nube."""

        if cloud_provider not in cls._registry:
            raise ValueError(f"El proveedor de nube {cloud_provider} no está registrado.")

        factory = cls._registry.get(cloud_provider)
        return factory.create_storage_service(**kwargs)
    
    @classmethod
    def create_messaging_service(cls,
                                 cloud_provider: str,
                                 **kwargs) -> BaseMessaging:
        """Método que retorna la Factory de servicios de nube."""

        if cloud_provider not in cls._registry:
            raise ValueError(f"El proveedor de nube {cloud_provider} no está registrado.")

        factory = cls._registry.get(cloud_provider)
        return factory.create_messaging_service(**kwargs)
    
    @classmethod
    def create_function_service(cls,
                                cloud_provider: str,
                                **kwargs) -> BaseFunction:
        """Método que retorna la Factory de servicios de nube."""

        if cloud_provider not in cls._registry:
            raise ValueError(f"El proveedor de nube {cloud_provider} no está registrado.")

        factory = cls._registry.get(cloud_provider)
        return factory.create_function_service(**kwargs)
