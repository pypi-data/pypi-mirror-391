"""Módulo que define la clase base para los clientes de bases de datos."""

# Librerías Externas.
from typing import Any
from abc import ABC, abstractmethod

import pandas as pd

# Librerías Internas.
from migracion_gcp.lib.clients.base.core.singleton import SingletonMeta


class BaseStorage(ABC, metaclass = SingletonMeta):
    """Clase que implementa el contrato para los clientes de servicios de storage."""
    
    @abstractmethod
    def create_bucket(self,
                      bucket_name: str) -> None:
        """Método que nos permite crear un bucket en Google Cloud Storage.
        
        Args:
        ----------
        bucket_name: str.
            Nombre del bucket que se desea crear."""

        raise NotImplementedError("Si tu clase implementa el contrato BaseStorage, debes implementar el método 'create_bucket'.")
    
    @abstractmethod
    def upload_file(self,
                    bucket_name: str,
                    file_path: str,
                    destination_path: str) -> None:
        """Método que nos permite subir un archivo a Google Cloud Storage.

        Args:
        ----------
        bucket_name: str.
            Nombre del bucket en el cual se subirá el archivo.

        file_path: str.
            Ruta del archivo que se desea subir.

        destination_path: str.
            Ruta en la cual se subirá el archivo. """

        raise NotImplementedError("Si tu clase implementa el contrato BaseStorage, debes implementar el método 'upload_file'.")

    @abstractmethod
    def download_file(self,
                      bucket_name: str,
                      file_path: str,
                      destination_path: str) -> None:
        """Método que nos permite descargar un archivo de Google Cloud Storage.

        Args:
        ----------
        bucket_name: str.
            Nombre del bucket en el cual se encuentra el archivo.

        file_path: str.
            Ruta del archivo que se desea descargar.

        destination_path: str.
            Ruta en la cual se descargará el archivo. """

        raise NotImplementedError("Si tu clase implementa el contrato BaseStorage, debes implementar el método 'download_file'.")
    
    @abstractmethod
    def download_csv(self,
                     bucket_name: str,
                     file_path: str) -> pd.DataFrame:
        """Método que nos permite descargar un archivo CSV de Google Cloud Storage.
        
        Args:
        ----------
        bucket_name: str.
            Nombre del bucket en el cual se encuentra el archivo.
        
        file_path: str.
            Ruta del archivo que se desea descargar.
            
        Returns:
        ----------
        df: pd.DataFrame.
            DataFrame con los datos del archivo CSV. """

        raise NotImplementedError("Si tu clase implementa el contrato BaseStorage, debes implementar el método 'download_csv'.")
    
    @abstractmethod
    def download_pickle(self,
                        bucket_name: str,
                        file_path: str) -> Any:
        """Método que nos permite descargar un archivo pickle de Google Cloud Storage.
        
        Args:
        ----------
        bucket_name: str.
            Nombre del bucket en el cual se encuentra el archivo.
        
        file_path: str.
            Ruta del archivo que se desea descargar.

        Returns:
        ----------
        Any.
            Objeto deserializado desde el archivo pickle."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseStorage, debes implementar el método 'download_pickle'.")
