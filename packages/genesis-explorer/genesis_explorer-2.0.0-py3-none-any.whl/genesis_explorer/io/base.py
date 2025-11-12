"""Módulo que define la interfaz para manejar archivos locales."""

# Librerías Externas.
from typing import Any, Optional
from abc import ABC, abstractmethod

import os
import shutil
import logging


class LocalFileBase(ABC):
    """Clase para manejar contratos de archivos locales."""

    def __init__(self, temp_dir: Optional[str] = "temp_dir") -> None:
        """Método para inicializar un archivo local.
        
        Args:
        ----------
        file_paths: List[str].
            Ruta del archivo que se desea manejar."""
        
        self.temp_dir = temp_dir

    def __enter__(self) -> "LocalFileBase":
        """Método para entrar en el contexto de un archivo local."""

        logging.info("Entrando en el contexto de un archivo local para hacerlo temporal.")

        os.makedirs(self.temp_dir, exist_ok = True)

        logging.info(f"Directorio temporal creado: {self.temp_dir}")

        return self
    
    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Método para salir del contexto de un archivo local."""

        shutil.rmtree(self.temp_dir)

        logging.info("Saliendo del contexto de un archivo local temporal.")
    
    @abstractmethod
    def write_file(self, file_path: str, content: Any) -> None:
        """Método para escribir un archivo.
        
        Args:
        ----------
        file_path: str.
            Ruta del archivo que se desea escribir.

        content: Any.
            Contenido del archivo."""

        raise NotImplementedError("Si tu clase implementa el contrato LocalFileBase, debes implementar el método 'write_file'.")
