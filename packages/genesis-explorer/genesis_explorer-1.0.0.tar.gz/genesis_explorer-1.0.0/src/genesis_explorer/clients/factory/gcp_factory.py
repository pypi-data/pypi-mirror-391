"""Implementación concreta de la clase Factory de GCS para interactura con el patrón Abstract Factory."""

# Librerías Internas.
from migracion_gcp.lib.clients.factory.base import CloudAbstractFactory

from migracion_gcp.lib.clients.gcp.pub_sub_client import PubSubService
from migracion_gcp.lib.clients.gcp.bigquery_client import BigQueryClient
from migracion_gcp.lib.clients.gcp.functions_client import CloudFunction
from migracion_gcp.lib.clients.gcp.storage_client import GoogleCloudStorageClient


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
