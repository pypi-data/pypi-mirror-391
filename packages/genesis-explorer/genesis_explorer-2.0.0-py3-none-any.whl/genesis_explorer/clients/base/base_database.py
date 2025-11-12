"""Módulo que define la clase base para los clientes de bases de datos."""

# Librerías Externas.
from abc import ABC, abstractmethod

import pandas as pd

# Librerías Internas.
from genesis_explorer.clients.base.core.singleton import SingletonMeta


class BaseDatabase(ABC, metaclass = SingletonMeta):
    """Clase que implementa el contrato para los clientes de bases de datos."""

    @abstractmethod
    def create_dataset(self,
                       dataset_name: str,
                       *args, **kwargs) -> None:
        """Método que nos permite crear un conjunto de tablas.
        
        Args:
        ----------
        dataset_name: str.
            Nombre del conjunto de tablas que se desea crear."""

        raise NotImplementedError("Si tu clase implementa el contrato BaseDatabase, debes implementar el método 'create_dataset'.")

    @abstractmethod
    def create_table(self,
                     table_name: str,
                     dataset_name: str,
                     *args, **kwargs) -> None:
        """Método que nos permite crear una tabla.
        
        Args:
        ----------
        table_name: str.
            Nombre de la tabla que se desea crear.

        dataset_name: str.
            Nombre del conjunto de tablas sobre el cual se creará la tabla."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseDatabase, debes implementar el método 'create_table'.")

    @abstractmethod
    def create_table_from_dataframe(self,
                                    table_name: str,
                                    dataset_name: str,
                                    dataframe: pd.DataFrame,
                                    *args, **kwargs) -> None:
        """Método que nos permite crear una tabla a partir de un DataFrame.
        
        Args:
        ----------
        table_name: str.
            Nombre de la tabla que se desea crear.
        
        dataset_name: str.
            Nombre del conjunto de tablas sobre el cual se creará la tabla.

        dataframe: pd.DataFrame.
            DataFrame que se desea cargar en la tabla.."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseDatabase, debes implementar el método 'create_table_from_dataframe'.")

    @abstractmethod
    def get_table(self,
                  table_name: str,
                  dataset_name: str,
                  *args, **kwargs) -> None:
        """Método que nos permite obtener una tabla.
        
        Args:
        ----------
        table_name: str.
            Nombre de la tabla que se desea obtener."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseDatabase, debes implementar el método 'get_table'.")
    
    @abstractmethod
    def query_to_dataframe(self,
                           query: str,
                           *args, **kwargs) -> None:
        """Método que nos permite ejecutar una consulta y retornar un DataFrame.
        
        Args:
        ----------
        query: str.
            Consulta que se desea ejecutar.
            
        Returns:
        ----------
        pd.DataFrame.
            DataFrame resultante de la consulta."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseDatabase, debes implementar el método 'query_to_dataframe'.")
    
    @abstractmethod
    def export_to_storage(self,
                          table_name: str,
                          dataset_name: str,
                          bucket_name: str,
                          blob_name: str) -> None:
        """Método que nos permite exportar una tabla a un servicio de storage.
        
        Args:
        ----------
        table_name: str.
            Nombre de la tabla que se desea exportar.

        dataset_name: str.
            Nombre del conjunto de tablas sobre el cual se encuentra la tabla.

        bucket_name: str.
            Nombre del bucket de Google Cloud Storage donde se desea exportar la tabla.

        blob_name: str.
            Nombre del blob de Google Cloud Storage donde se desea exportar la tabla."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseDatabase, debes implementar el método 'export_to_storage'.")
    