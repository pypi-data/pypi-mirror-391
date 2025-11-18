"""Módulo que define la clase para manejar archivos JSON locales."""

# Librerías Externas.
from typing import Any

import json
import logging

# Librerías Internas.
from genesis_explorer.io.base import LocalFileBase


class JSONFile(LocalFileBase):
    """Clase para manejar archivos JSON locales."""
    
    def write_file(self, file_path: str, content: Any, **kwargs) -> None:
        """Método para escribir un archivo JSON.
        
        Args:
        ----------
        file_path: str.
            Ruta del archivo que se desea escribir.

        content: Any.
            Contenido del archivo."""
        
        logging.info(f"Escribiendo el archivo {file_path} en el directorio temporal...")

        try:
            with open(f"{self.temp_dir}/{file_path}", "w") as file:
                json.dump(content, file, **kwargs)

            logging.info(f"Archivo {file_path} escrito correctamente.")

        except Exception as e:
            logging.error(f"Error al escribir el archivo {file_path}: {e}")
