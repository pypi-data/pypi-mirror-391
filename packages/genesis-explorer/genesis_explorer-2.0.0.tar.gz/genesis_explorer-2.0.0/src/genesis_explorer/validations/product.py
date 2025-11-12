"""Módulo que, en el patrón builder, define el producto final de la validación."""

# Librerías Externas.
from typing import Dict, Callable

import logging


class Validator:
    """Clase que define un objeto complejo usado para validar modelos de Machine Learning."""

    def __init__(self) -> None:
        """Método de instanciación de clase."""

        self.validations = []

    def add_validation(self, validation_func: Callable[..., bool]) -> None:
        """Método que permite ir creando el objeto complejo.
        
        Args:
        ----------
        validation_func: Callable[..., bool].
            Función que define la validación a realizar."""

        self.validations.append(validation_func)

    def execute_validations(self, *args, **kwargs) -> Dict[str, bool]:
        """Método que ejecuta las validaciones.
        
        Returns:
        ----------
        Dict[str, bool].
            Diccionario con los resultados de las validaciones."""

        results = {}
        for func in self.validations:
            func_name = func.__name__
            try:
                results[func_name] = func(*args, **kwargs)
            except Exception as e:
                results[func_name] = f"Error: {e}"
                logging.error(f"Error al ejecutar la validación {func_name}: {e}")
            finally:
                logging.info(f"✅ Validación {func_name} completada correctamente.")
                if results[func_name]:
                    logging.info(f"✅ Resultado de la validación {func_name} exitosa: {results[func_name]}")
                else:
                    logging.error(f"❌ Resultado de la validación {func_name} fallida: {results[func_name]}")
        return results
