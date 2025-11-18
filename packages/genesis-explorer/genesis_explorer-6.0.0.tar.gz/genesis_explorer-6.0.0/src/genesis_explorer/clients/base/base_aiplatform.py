"""Módulo que contiene la clase AIPlatform para manejar el tracking de experimentos y runs en Vertex AI."""

# Librerías Externas.
from typing import TypeVar, List, Optional
from abc import ABC, abstractmethod

# Librerías Internas.
from genesis_explorer.clients.base.core.singleton import SingletonMeta


Model = TypeVar("Model")
Experiment = TypeVar("Experiment")
ExperimentRun = TypeVar("ExperimentRun")
TabularDataset = TypeVar("TabularDataset")


class BaseAIPlatform(ABC, metaclass = SingletonMeta):
    """Clase que se encarga de manejar el tracking de experimentos y runs en Vertex AI."""

    @abstractmethod
    def create_experiment(self, experiment_name: str) -> Experiment:
        """Método abstractoque permite crear u obtener (si ya existe) un experimento.
        
        Args:
        ----------
        experiment_name: str.
            Nombre del experimento.
        
        Returns:
        ----------
        Experiment.
            Experimento a usar para registrar ExperimentRuns."""

        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'create_experiment'.")
    
    def delete_experiment(self, experiment_name: str) -> None:
        """Método que permite eliminar un experimento.
        
        Args:
        ----------
        experiment_name: str.
            Nombre del experimento."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'delete_experiment'.")
        
    def list_experiments(self) -> List[Experiment]:
        """Método que permite obtener todos los experimentos en la ubicación de su AIPlatform.

        (Este método también lo podríamos aplicar como df = experiment.get_data_frame()
        para tener descripciones sin necesidad de recorrer Experiments).
        
        Returns:
        ----------
        experiments: List[Experiment].
            Lista de experimentos."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'list_experiments'.")
        
    def create_run(self, run_name: str, experiment: Experiment) -> ExperimentRun:
        """Método que permite crear un ExperimentRun.
        
        Args:
        ----------
        run_name: str.
            Nombre del ExperimentRun.
        
        experiment: Experiment.
            Experimento al que se asociará el ExperimentRun.
        
        Returns:
        ----------
        ExperimentRun.
            ExperimentRun creado para registrar su experimento particular."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'create_run'.")
        
    def get_run(self, run_name: str, experiment: Experiment) -> ExperimentRun:
        """Método que permite obtener un ExperimentRun ya registrado para
        actualizarlo o, simplemente, leerlo.
        
        Args:
        ----------
        run_name: str.
            Nombre del ExperimentRun.
        
        experiment: aiplatform.metadata.experiment_resources.Experiment.
            Experimento al que se asoció el ExperimentRun.
        
        Returns:
        ----------
        run: aiplatform.metadata.experiment_resources.ExperimentRun.
            ExperimentRun obtenido para actualizar o leer."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'get_run'.")
    
    def delete_run(self, experiment_run: ExperimentRun) -> None:
        """Método que permite eliminar un ExperimentRun.
        
        Args:
        ----------
        experiment_run: ExperimentRun.
            Instancia del ExperimentRun a eliminar."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'delete_run'.")
        
    def end_run(self, experiment_run: ExperimentRun) -> None:
        """Método que permite cerrar un ExperimentRun.
        
        Args:
        ----------
        experiment_run: ExperimentRun.
            Instancia del ExperimentRun a cerrar."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'end_run'.")
    
    def list_runs(self, experiment: Experiment) -> List[ExperimentRun]:
        """Método que permite obtener todos los ExperimentRuns asociados a un Experiment.
        
        Args:
        ----------
        experiment: Experiment.
            Experimento al que se asociaron los ExperimentRuns.
        
        Returns:
        ----------
        experiment_runs: List[ExperimentRun].
            Lista de ExperimentRuns asociados al Experiment."""

        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'list_runs'.")
        
    def create_tabular_dataset(self, name: str,
                               gcs_source: Optional[str] = None, bq_source: Optional[str] = None) -> TabularDataset:
        """Método que permite crear un Dataset dentro de Vertex AI
        para dar un punto de inicio a la experimentación.

        Esto se guarda en las pestañas Dataset de Vertex AI.
        
        Args:
        ----------
        name: str.
            Nombre del TabularDataset.
        
        gcs_source: Optional[str].
            URI de storage donde se encuentra el dataset para referencia. (Ya debe estar creado, por ejemplo en GCS).
        
        bq_source: Optional[str].
            URI de database donde se encuentra el dataset para referencia. (Ya debe estar creado, por ejemplo en BigQuery).
        
        Returns:
        ----------
        dataset: aiplatform.TabularDataset.
            Dataset creado para dar un punto de inicio a la experimentación."""

        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'create_tabular_dataset'.")
        
    def upload_trained_model(self, name: str, gcs_source: str, serving_container_image_uri: str) -> Model:
        """Método para cargar un modelo entrenado la plataforma.
        
        Args:
        ----------
        name: str.
            Nombre del modelo.
        
        gcs_source: str.
            URI de storage donde se encuentra el modelo entrenado.
        
        serving_container_image_uri: str.
            URI del contenedor de que contiene referencia al modelo entrenado.
        
        Returns:
        ----------
        model: aiplatform.Model.
            Modelo cargado en Vertex AI."""

        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'upload_trained_model'.")

    def get_trained_model(self, name: str) -> Model:
        """Método para obtener un modelo entrenado en Vertex AI.
        
        Args:
        ----------
        name: str.
            Nombre del modelo."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseAIPlatform, debes implementar el método 'get_trained_model'.")
