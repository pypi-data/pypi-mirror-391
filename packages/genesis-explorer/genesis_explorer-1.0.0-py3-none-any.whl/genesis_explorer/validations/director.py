"""Módulo que define un director en el patrón builder para generar flavours de validaciones."""

# Librerías Internas.
from migracion_gcp.lib.validations.builder import Builder
from migracion_gcp.lib.validations.product import Validator


class Director:
    """Clase que define la coordinación entre el cliente y el builder 
    para la creación de validadores."""
    
    def __init__(self, builder: Builder) -> None:
        """Método de instanciación de clase."""

        self._builder = builder
    
    def add_score_validation(self) -> None:
        """Método que define el contrato para la validación de scores."""

        self._builder.add_scores_validation()
    
    def add_metric_validation(self) -> None:
        """Método que define el contrato para la validación de métricas."""

        self._builder.add_metrics_validation()

    def add_csi_validation(self) -> None:
        """Método que define el contrato para la validación del CSI."""

        self._builder.add_csi_validation()
    
    def get_validator(self) -> Validator:
        """Método que retorna el validator."""

        return self._builder._validator