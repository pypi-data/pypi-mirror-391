"""Módulo que define un cliente para la comunicación con Google Cloud Storage."""

# Librerías Externas.
from typing import Any

import pickle
import logging
from io import StringIO

import pandas as pd

from google.cloud import storage

# Librerías Internas.
from migracion_gcp.lib.clients.base.base_storage import BaseStorage


logging.basicConfig(level = logging.INFO,
                    format = "%(asctime)s - %(levelname)s - %(message)s")


class GoogleCloudStorageClient(BaseStorage):
    """Clase que define un cliente para la comunicación con Google Cloud Storage."""

    def __init__(self,
                 project_id: str) -> None:
        """Método de instanciación de la clase.
        
        Args:
        ----------
        project_id: str.
            ID del proyecto de GCP sobre el cual se creará el cliente."""
        
        self.project_id = project_id
        self.client = storage.Client(project = project_id)

    def create_bucket(self,
                      bucket_name: str) -> None:
        """Método que nos permite crear un bucket en Google Cloud Storage.
        
        Args:
        ----------
        bucket_name: str.
            Nombre del bucket que se desea crear."""

        logging.info(f"Creando el bucket {bucket_name} en el proyecto {self.project_id}...")
        
        try:
            bucket = self.client.create_bucket(bucket_name)
            logging.info(f"Bucket {bucket_name} creado correctamente.")
        except Exception as e:
            logging.error(f"Error al crear el bucket {bucket_name}: {e}")

        return bucket
        
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

        logging.info(f"Subiendo el archivo {file_path} al bucket {bucket_name} en el proyecto {self.project_id}...")

        try:
            bucket = self.client.lookup_bucket(bucket_name)
            if not bucket:
                bucket = self.create_bucket(bucket_name)
            
            blob = bucket.blob(destination_path)
            blob.upload_from_filename(file_path)
            logging.info(f"Archivo {file_path} subido correctamente.")

        except Exception as e:
            logging.error(f"Error al subir el archivo {file_path}: {e}")

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

        logging.info(f"Descargando el archivo {file_path} del bucket {bucket_name} en el proyecto {self.project_id}...")

        try:
            bucket = self.client.lookup_bucket(bucket_name)
            if not bucket:
                bucket = self.create_bucket(bucket_name)

            blob = bucket.blob(file_path)
            blob.download_to_filename(destination_path)
            logging.info(f"Archivo {file_path} descargado correctamente.")

        except Exception as e:
            logging.error(f"Error al descargar el archivo {file_path}: {e}")

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
        
        logging.info(f"Descargando dataset del bucket {bucket_name} en el proyecto {self.project_id}...")
        
        try:
            bucket = self.client.lookup_bucket(bucket_name)
            if not bucket:
                bucket = self.create_bucket(bucket_name)

            blob = bucket.blob(file_path)

            data = blob.download_as_text()
            df = pd.read_csv(StringIO(data))
            logging.info(f"Archivo {file_path} descargado correctamente.")

        except Exception as e:
            logging.error(f"Error al descargar el archivo {file_path}: {e}")

        return df
    
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
        
        logging.info(f"Descargando archivo pickle del bucket {bucket_name} en el proyecto {self.project_id}...")
        
        try:
            bucket = self.client.lookup_bucket(bucket_name)
            if not bucket:
                bucket = self.create_bucket(bucket_name)
                
            blob = bucket.blob(file_path)
            data = blob.download_as_bytes()
            modelo = pickle.loads(data)

            logging.info(f"Archivo {file_path} descargado correctamente.")

        except Exception as e:
            logging.error(f"Error al descargar el archivo {file_path}: {e}")

        return modelo

    def __str__(self) -> str:
        return f"GoogleCloudStorageClient(project_id = {self.project_id})"
