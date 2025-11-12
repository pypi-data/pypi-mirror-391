"""Módulo que define la clase para manejar archivos pickle locales."""


# Librerías Externas.
from typing import Any

import pickle
import logging

# Librerías Internas.
from migracion_gcp.lib.io.base import LocalFileBase
from migracion_gcp.lib.io.registry import LocalFileRegistry


@LocalFileRegistry.register_file_handler("pickle")
class PickleFile(LocalFileBase):
    """Clase para manejar archivos pickle locales."""

    def write_file(self,
                   file_path: str,
                   content: Any,
                   **kwargs) -> None:
        """Método para escribir un archivo pickle.
        
        Args:
        ----------
        file_path: str.
            Ruta del archivo que se desea escribir.
        
        content: Any.
            Contenido del archivo."""
        
        logging.info(f"Escribiendo el archivo {file_path} en el directorio temporal...")

        try:
            with open(f"{self.temp_dir}/{file_path}", "wb") as file:
                pickle.dump(content, file, **kwargs)

            logging.info(f"Archivo {file_path} escrito correctamente.")

        except Exception as e:
            logging.error(f"Error al escribir el archivo {file_path}: {e}")
