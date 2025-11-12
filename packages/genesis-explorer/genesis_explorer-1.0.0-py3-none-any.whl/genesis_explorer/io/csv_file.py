"""Módulo que define la clase para manejar archivos CSV locales."""

# Librerías Externas.
from typing import Any

import logging
import pandas as pd

# Librerías Internas.
from migracion_gcp.lib.io.base import LocalFileBase


logging.basicConfig(level = logging.INFO, 
                    format = "%(asctime)s - %(levelname)s - %(message)s")


class CSVFile(LocalFileBase):
    """Clase para manejar archivos CSV locales."""
    
    def write_file(self, file_path: str, content: pd.DataFrame, **kwargs) -> None:
        """Método para escribir un archivo CSV."""

        logging.info(f"Escribiendo el archivo {file_path} en el directorio temporal...")

        try:
            content.to_csv(f"{self.temp_dir}/{file_path}", **kwargs)

            logging.info(f"Archivo {file_path} escrito correctamente.")

        except Exception as e:
            logging.error(f"Error al escribir el archivo {file_path}: {e}")
