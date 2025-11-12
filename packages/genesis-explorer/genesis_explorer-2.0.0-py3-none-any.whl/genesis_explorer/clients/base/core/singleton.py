"""Módulo que define la metaclase Singleton para nuestros clientes de GCP."""

# Librerías Externas.
from typing import Any
from abc import ABCMeta

import logging


logging.basicConfig(level = logging.INFO,
                    format = "%(asctime)s - %(levelname)s - %(message)s")


class Singleton(type):
    """Metaclase que implementa el patrón Singleton para nuestros clientes de GCP."""

    __instance = None

    def __call__(cls, *args, **kwargs) -> Any:
        """Método que intercepta el constructor e instanciador de clases
        para asegurarnos que solo se cree una instancia de la clase."""

        if cls.__instance is None:
            logging.info("Instanciando la primera instancia de la clase...")
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)

        logging.info("Esta clase implementa el patrón Singleton, por ende, se retorna la instancia existente.")
        return cls.__instance
    

class SingletonMeta(Singleton, ABCMeta):
    """Metaclase que implementa el patrón Singleton para nuestros clientes de bases de datos."""

    ...
