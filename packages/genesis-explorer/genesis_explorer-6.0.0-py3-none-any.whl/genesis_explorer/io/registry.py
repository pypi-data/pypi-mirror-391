"""Clase que implementa el patrón Registry para manejar archivos locales."""

# Librerías Externas.
from typing import Type

# Librerías Internas.
from genesis_explorer.io.base import LocalFileBase

from genesis_explorer.io.csv_file import CSVFile
from genesis_explorer.io.json_file import JSONFile


class LocalFileRegistry:
    """Clase que implementa el patrón Registry para manejar archivos locales."""

    _registry: dict[str, Type[LocalFileBase]] = {"csv": CSVFile,
                                                 "json": JSONFile}
    
    @classmethod
    def get_file_handler(cls, file_type: str) -> Type[LocalFileBase]:
        """Método para obtener un archivo local."""

        if file_type not in cls._registry:
            raise ValueError(f"Tipo de archivo no soportado: {file_type}")

        return cls._registry[file_type]
    
    @classmethod
    def register_file_handler(cls, file_type: str) -> None:
        """Método para registrar un archivo local.
        
        Args:
        ----------
        file_type: str.
            Tipo de manejo de archivo que se desea registrar."""

        def wrapper(cls_to_register: type[LocalFileBase]) -> None:
            """Wraper que representa una clase que implementa el contrato LocalFileBase."""

            if file_type in cls._registry:
                raise ValueError(f"Tipo de archivo ya registrado: {file_type}")
            
            cls._registry[file_type] = cls_to_register
        
        return wrapper
