"""Implementación concreta de la clase Factory de GCS para interactura con el patrón Abstract Factory."""

# Librerías Internas.
from genesis_explorer.clients.factory.base import CloudAbstractFactory

from genesis_explorer.clients.gcp.pub_sub_client import PubSubService
from genesis_explorer.clients.gcp.bigquery_client import BigQueryClient
from genesis_explorer.clients.gcp.functions_client import CloudFunction
from genesis_explorer.clients.gcp.storage_client import GoogleCloudStorageClient


class GCPAbstractFactory(CloudAbstractFactory):
    """Clase que define el contrato para la creación de Factories de GCP."""
    
    @classmethod
    def create_database_service(cls, **kwargs) -> None:
        """Método que define el contrato para la creación de servicios de bases de datos."""

        return BigQueryClient(**kwargs)
    
    @classmethod
    def create_storage_service(cls, **kwargs) -> None:
        """Método que define el contrato para la creación de servicios de almacenamiento."""

        return GoogleCloudStorageClient(**kwargs)
    
    @classmethod
    def create_messaging_service(cls, **kwargs) -> None:
        """Método que define el contrato para la creación de servicios de mensajería."""

        return PubSubService(**kwargs)
    
    @classmethod
    def create_function_service(cls, **kwargs) -> None:
        """Método que define el contrato para la creación de servicios de Cloud Functions."""

        return CloudFunction(**kwargs)
