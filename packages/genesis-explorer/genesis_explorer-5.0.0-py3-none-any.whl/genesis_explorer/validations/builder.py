"""Módulo que define un builder en el patrón builder para generar flavours de validaciones."""

# Librerías Externas.
from typing import Optional
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

# Librerías Internas.
from genesis_explorer.validations.product import Validator


class Builder(ABC):
    """Clase que define el contrato estructural para creación de builders."""

    _csi_threshold: Optional[float] = 1.5
    _pvalue_threshold: Optional[float] = 0.05
    _metrics_threshold: Optional[float] = 0.05

    def __init__(self) -> None:
        """Método de instanciación de clase."""

        self._validator = Validator()
    
    @abstractmethod
    def add_scores_validation(self):
        """Método que define el contrato para la validación de scores.
        
        Returns:
        ----------
        Builder.
            Builder para la validación de scores."""
        
        raise NotImplementedError("Método no implementado.")
    
    @abstractmethod
    def add_metrics_validation(self):
        """Método que define el contrato para la validación de métricas.
        
        Returns:
        ----------
        Builder.
            Builder para la validación de métricas."""
        
        raise NotImplementedError("Método no implementado.")
    
    def add_csi_validation(self):
        """Método que, como se usa en ambos productos indiscriminadamente,
        se puede definir en el Builder."""

        def validate_csi(X_train: pd.DataFrame,
                         X_test: pd.DataFrame, **kwargs) -> bool:
            """Función que se encarga de validar el CSI del modelo.
            
            Args:
            ----------
            X_train: pd.DataFrame.
                Conjunto de datos de entrenamiento.

            X_test: pd.DataFrame.
                Conjunto de datos de prueba.
            
            Returns:
            ----------
            bool.
                True si el CSI del modelo es válido, False en caso contrario."""

            try:
                if hasattr(X_train, "values"):
                    X_train = X_train.values
                if hasattr(X_test, "values"):
                    X_test = X_test.values
            except AttributeError as e:
                raise AttributeError(f"Error al validar el CSI del modelo: {e}")
            
            X_train_mean = np.mean(X_train, axis = 0)
            X_test_mean = np.mean(X_test, axis = 0)

            X_train_std = np.std(X_train, axis = 0)
            X_test_std = np.std(X_test, axis = 0)

            X_train_idx = X_train_mean / (X_train_std + 1e-10)
            X_test_idx = X_test_mean / (X_test_std + 1e-10)

            return all(np.abs(X_train_idx - X_test_idx) < self._csi_threshold)

        self._validator.add_validation(validate_csi)
        return self
