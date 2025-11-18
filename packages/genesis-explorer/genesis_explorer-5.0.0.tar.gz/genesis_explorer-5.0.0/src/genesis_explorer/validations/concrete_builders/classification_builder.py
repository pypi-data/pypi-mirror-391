"""Módulo que define un builder para la validación de modelos de clasificación."""

# Librerías Externas.
from typing import Callable

import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator
from scipy.stats import chi2_contingency

# Librerías Internas.
from genesis_explorer.validations.builder import Builder


class ValidateClassificationBuilder(Builder):
    """Clase que implementa un builder para la validación de
    modelos de clasificación."""
    
    def add_metrics_validation(self) -> "ValidateClassificationBuilder":
        """Método que define el contrato para la validación de métricas.
        
        Returns:
        ----------
        ValidateClassificationBuilder.
            Builder para la validación de métricas."""
        
        def validate_metrics(modelo: BaseEstimator,
                             metric_fn: Callable[[np.ndarray, np.ndarray], float],
                             X_train: pd.DataFrame,
                             X_test: pd.DataFrame,
                             y_train: pd.Series,
                             y_test: pd.Series, **kwargs) -> bool:
            """Función que se encarga de validar las métricas del modelo.
            
            Args:
            ----------
            modelo: BaseEstimator.
                Modelo de clasificación.
            
            metric_fn: Callable[[np.ndarray, np.ndarray], float].
                Función que define la métrica a validar.
            
            X_train: pd.DataFrame.
                Conjunto de datos de entrenamiento.
            
            X_test: pd.DataFrame.
                Conjunto de datos de prueba.
            
            y_train: pd.Series.
                Conjunto de datos de entrenamiento.
            
            y_test: pd.Series.
                Conjunto de datos de prueba.
            
            Returns:
            ----------
            bool.
                True si las métricas del modelo son válidas, False en caso contrario."""
            
            try:
                train_scores = modelo.predict_proba(X_train)
                test_scores = modelo.predict_proba(X_test)

                train_metric = metric_fn(train_scores, y_train)
                test_metric = metric_fn(test_scores, y_test)
            
            except Exception as e:
                raise Exception(f"Error al validar las métricas del modelo: {e}")
            
            val1 = train_metric > test_metric
            val2 = abs(train_metric - test_metric) < self._metrics_threshold
            return val1 and val2
        
        self._validator.add_validation(validate_metrics)
        return self
    
    def add_scores_validation(self) -> "ValidateClassificationBuilder":
        """Método que define el contrato para la validación de scores.
        
        Returns:
        ----------
        ValidateClassificationBuilder.
            Builder para la validación de scores."""
        
        def validate_scores(y_train: pd.Series,
                            y_test: pd.Series, **kwargs) -> bool:
            """Función que se encarga de validar los scores del modelo.
            
            Args:
            ----------
            y_train: pd.Series.
                Conjunto de datos de entrenamiento.
            
            y_test: pd.Series.
                Conjunto de datos de prueba.
            
            Returns:
            ----------
            bool.
                True si los scores del modelo son válidos, False en caso contrario."""
            
            try:
                train_freq = y_train.value_counts()
                test_freq = y_test.value_counts()

                contigency_table = pd.concat([train_freq, test_freq], axis = 1).fillna(0)
                                
                _, chi_pvalue, _, _ = chi2_contingency(contigency_table.values)
            except Exception as e:
                raise Exception(f"Error al validar los scores del modelo: {e}")
            
            return float(chi_pvalue) < self._pvalue_threshold
        
        self._validator.add_validation(validate_scores)
        return self
