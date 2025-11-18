"""Módulo que define el cliente para comunicación con BigQuery."""

# Librerías Externas.
from typing import Optional, Dict, List

import logging

import pandas as pd

from google.cloud import bigquery

# Librerías Internas.
from genesis_explorer.clients.base.base_database import BaseDatabase


class BigQueryClient(BaseDatabase):
    """Clase que define un cliente para la comunicación con BigQuery."""

    def __init__(self,
                 project_id: str) -> None:
        """Método de instanciación de la clase.
        
        Args:
        ----------
        project_id: str.
            ID del proyecto de GCP sobre el cual se creará el cliente."""
        
        logging.info("Instanciando el cliente...")
        
        self.project_id = project_id
        self.client = bigquery.Client(project = project_id)

    def create_dataset(self,
                       dataset_name: str,
                       description: Optional[str] = "",
                       labels: Optional[Dict[str, str]] = {}) -> None:
        """Método que nos permite crear un conjunto de tablas.
        
        Args:
        ----------
        dataset_name: str.
            Nombre del conjunto de tablas que se desea crear.

        description: Optional[str].
            Descripción del conjunto de tablas que se desea crear.

        labels: Optional[Dict[str, str]].
            Etiquetas del conjunto de tablas que se desea crear."""

        dataset_id = f"{self.project_id}.{dataset_name}"

        logging.info(f"Creando el conjunto de tablas: {dataset_id}.")
        
        try:
            dataset = bigquery.Dataset(dataset_id)

            dataset.labels = labels
            dataset.description = description

            dataset = self.client.create_dataset(dataset, exists_ok = True)

            logging.info(f"Conjunto de tablas creado correctamente: {dataset_id}.")
        
        except Exception as e:
            logging.error(f"Error al crear el conjunto de tablas: {e}.")

    def create_table(self,
                     table_name: str,
                     dataset_name: str,
                     schema: List[bigquery.SchemaField],
                     description: Optional[str] = "",
                     labels: Optional[Dict[str, str]] = {}) -> bigquery.Table:
        """Método que nos permite crear una tabla.
        
        Args:
        ----------
        table_name: str.
            Nombre de la tabla que se desea crear.

        dataset_name: str.
            Nombre del conjunto de tablas sobre el cual se creará la tabla.

        schema: List[bigquery.SchemaField].
            Esquema de la tabla que se desea crear.

        description: Optional[str].
            Descripción de la tabla que se desea crear.
        
        labels: Optional[Dict[str, str]].
            Etiquetas de la tabla que se desea crear.
            
        Returns:
        ----------
        bigquery.Table.
            Objeto de tipo tabla de BigQuery."""
        
        table_id = f"{self.project_id}.{dataset_name}.{table_name}"

        logging.info(f"Creando la tabla: {table_id}.")

        try:
            table = bigquery.Table(table_id, schema = schema)

            table.labels = labels
            table.description = description
            
            table = self.client.create_table(table, exists_ok = True)

            logging.info(f"Tabla creada correctamente: {table_id}.")

        except Exception as e:
            logging.error(f"Error al crear la tabla: {e}.")

        return table

    def create_table_from_dataframe(self,
                                    table_name: str,
                                    dataset_name: str,
                                    dataframe: pd.DataFrame,
                                    schema: Optional[List[bigquery.SchemaField]] = None,
                                    **kwargs) -> None:
        """Método que nos permite crear una tabla a partir de un DataFrame.
        
        Args:
        ----------
        table_name: str.
            Nombre de la tabla que se desea crear.
        
        dataset_name: str.
            Nombre del conjunto de tablas sobre el cual se creará la tabla.

        dataframe: pd.DataFrame.
            DataFrame que se desea cargar en la tabla.

        schema: Optional[List[bigquery.SchemaField]].
            Esquema de la tabla que se desea crear."""
        
        try:
            table = self.create_table(table_name, dataset_name, schema, **kwargs)

            self.client.load_table_from_dataframe(dataframe, table)

        except Exception as e:
            logging.error(f"Error al crear la tabla: {e}.")

    def get_table(self, table_name: str, dataset_name: str) -> pd.DataFrame:
        """Método que nos permite obtener una tabla.
        
        Args:
        ----------
        table_name: str.
            Nombre de la tabla que se desea obtener."""
        
        table_id = f"{self.project_id}.{dataset_name}.{table_name}"

        logging.info(f"Obteniendo la tabla: {table_id}.")
        
        try:
            table = self.client.get_table(table_id)  
            table_df = self.client.list_rows(table).to_dataframe()
            
            logging.info(f"Tabla obtenida correctamente: {table_id}.")
        
        except Exception as e:
            logging.error(f"Error al obtener la tabla: {e}.")

        return table_df
    
    def query_to_dataframe(self, query: str) -> pd.DataFrame:
        """Método que nos permite ejecutar una consulta y retornar un DataFrame.
        
        Args:
        ----------
        query: str.
            Consulta que se desea ejecutar.
            
        Returns:
        ----------
        pd.DataFrame.
            DataFrame resultante de la consulta."""
        
        logging.info(f"Ejecutando la consulta...")

        try:
            query_job = self.client.query(query)
            dataframe = query_job.to_dataframe()

            logging.info(f"Consulta ejecutada correctamente: {query_job.total_rows} filas.")
        
        except Exception as e:
            logging.error(f"Error al ejecutar la consulta: {e}.")
        
        return dataframe
    
    def export_to_storage(self,
                          table_name: str,
                          dataset_name: str,
                          bucket_name: str,
                          blob_name: str) -> None:
        """Método que nos permite exportar una tabla a un bucket de Google Cloud Storage.
        
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
        
        table_id = f"{self.project_id}.{dataset_name}.{table_name}"
        blob_path = f"gs://{bucket_name}/{blob_name}/{table_name}_*.csv"
        
        logging.info(f"Exportando la tabla: {table_id} a {blob_path}.")
        
        try:
            job = self.client.extract_table(table_id,
                                            f"gs://{bucket_name}/{blob_name}")
            job.result()

            logging.info(f"Tabla exportada correctamente: {table_id} a {bucket_name}.")
        
        except Exception as e:
            logging.error(f"Error al exportar la tabla: {e}.")

    def __str__(self) -> str:
        """Método que retorna una representación en cadena de la clase."""

        return f"BigQueryClient(project_id = {self.project_id})"
