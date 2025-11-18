"""Módulo que contiene la clase AIPlatform para manejar el tracking de experimentos y runs en Vertex AI."""

# Librerías Externas.
from typing import Any, TypeVar, List, Optional

import os
import json
import pickle
import logging

from google.cloud import aiplatform
from google.api_core.exceptions import AlreadyExists, NotFound

# Librerías Internas.
from genesis_explorer.clients.base.base_aiplatform import BaseAIPlatform


logging.basicConfig(level = logging.INFO,
                    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")


Model = TypeVar("Model")
Experiment = TypeVar("Experiment")
ExperimentRun = TypeVar("ExperimentRun")


class AIPlatform(BaseAIPlatform):
    """Clase que se encarga de manejar el tracking de experimentos y runs en Vertex AI."""

    def __init__(self, project_id: str,
                 location: Optional[str] = "us-east1",
                 staging_bucket: Optional[str] = None) -> None:
        """Método de instanciación de clase.
        
        Args:
        ----------
        project_id: str.
            ID del proyecto de GCP.
        
        location: Optional[str].
            Región de GCP donde guardará registros.
        
        staging_bucket: Optional[str].
            Bucket de GCS donde se guardarán los archivos temporales."""
        
        aiplatform.init(project = project_id,
                        location = location,
                        staging_bucket = staging_bucket)
        
    def create_experiment(self, experiment_name: str) -> Experiment:
        """Método que permite crear u obtener (si ya existe) un experimento.
        
        Args:
        ----------
        experiment_name: str.
            Nombre del experimento.
        
        Returns:
        ----------
        Experiment.
            Experimento a usar para registrar ExperimentRuns."""

        logging.info(f"Creando experimento: {experiment_name}")

        try:
            experiment = aiplatform.Experiment.create(experiment_name = experiment_name)

            logging.info(f"Experimento creado: {experiment_name}")
            return experiment
        except AlreadyExists as e:
            logging.info(f"Experimento ya existe: {experiment_name}")
            experiment = aiplatform.Experiment.get(experiment_name = experiment_name)
            return experiment
        except Exception as e:
            logging.error(f"Error al crear experimento: {e}")
            raise e
        
    def get_experiment(self, experiment_name: str) -> Experiment:
        """Método que permite obtener un experimento ya registrado para
        actualizarlo o, simplemente, leerlo.
        
        Args:
        ----------
        experiment_name: str.
            Nombre del experimento."""
        
        logging.info(f"Obteniendo experimento: {experiment_name}")

        try:
            experiment = aiplatform.Experiment.get(experiment_name = experiment_name)
            logging.info(f"Experimento obtenido: {experiment_name}")
            return experiment
        except Exception as e:
            logging.error(f"Error al obtener experimento: {e}")
            raise e
        
    def delete_experiment(self, experiment_name: str) -> None:
        """Método que permite eliminar un experimento.
        
        Args:
        ----------
        experiment_name: str.
            Nombre del experimento."""
        
        logging.info(f"Eliminando experimento: {experiment_name}")

        experiment = self.create_experiment(experiment_name = experiment_name)
        try:
            experiment.delete()
            logging.info(f"Experimento eliminado: {experiment_name}")
        except Exception as e:
            logging.error(f"Error al eliminar experimento: {e}")
            raise e
        
    def list_experiments(self) -> List[Experiment]:
        """Método que permite obtener todos los experimentos en la ubicación de su AIPlatform.

        (Este método también lo podríamos aplicar como df = experiment.get_data_frame()
        para tener descripciones sin necesidad de recorrer Experiments).
        
        Returns:
        ----------
        experiments: List[Experiment].
            Lista de experimentos."""
        
        logging.info("Obteniendo experimentos...")
        try:
            experiments = aiplatform.Experiment.list()
            logging.info(f"Experimentos obtenidos: {experiments}")
            return experiments
        except Exception as e:
            logging.error(f"Error al obtener experimentos: {e}")
            raise e
        
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
        
        logging.info(f"Creando ExperimentRun: {run_name}")

        try:
            run = aiplatform.ExperimentRun.create(run_name = run_name, experiment = experiment)
            logging.info(f"ExperimentRun creado: {run_name}")
            return run
        except Exception as e:
            logging.error(f"Error al crear ExperimentRun: {e}")
            raise e
        
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
        
        logging.info(f"Obteniendo ExperimentRun: {run_name}")
        
        try:
            run = aiplatform.ExperimentRun.get(run_name = run_name, experiment = experiment)
            logging.info(f"ExperimentRun obtenido: {run_name}")
            return run
        except Exception as e:
            logging.error(f"Error al obtener ExperimentRun: {e}")
            raise e

    def delete_run(self, experiment_run: ExperimentRun) -> None:
        """Método que permite eliminar un ExperimentRun.
        
        Args:
        ----------
        experiment_run: ExperimentRun.
            Instancia del ExperimentRun a eliminar."""
        
        logging.info(f"Eliminando ExperimentRun: {experiment_run.name}")

        try:
            experiment_run.delete()
            logging.info(f"ExperimentRun eliminado: {experiment_run.name}")
        except Exception as e:
            logging.error(f"Error al eliminar ExperimentRun: {e}")
            raise e
        
    def end_run(self, experiment_run: ExperimentRun) -> None:
        """Método que permite cerrar un ExperimentRun.
        
        Args:
        ----------
        experiment_run: ExperimentRun.
            Instancia del ExperimentRun a cerrar."""
        
        logging.info(f"Cerrando ExperimentRun: {experiment_run.name}")

        try:
            experiment_run.end_run()
            logging.info(f"ExperimentRun cerrado: {experiment_run.name}")
        except Exception as e:
            logging.error(f"Error al cerrar ExperimentRun: {e}")
            raise e
    
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

        logging.info(f"Obteniendo ExperimentRuns asociados al Experiment: {experiment.name}")

        try:
            experiment_runs = aiplatform.ExperimentRun.list(experiment = experiment)
            logging.info(f"ExperimentRuns obtenidos: {experiment_runs}")
            return experiment_runs
        except Exception as e:
            logging.error(f"Error al obtener ExperimentRuns: {e}")
            raise e
        
    def create_tabular_dataset(self, name: str,
                               gcs_source: Optional[str] = None, bq_source: Optional[str] = None) -> aiplatform.TabularDataset:
        """Método que permite crear un Dataset dentro de Vertex AI
        para dar un punto de inicio a la experimentación.

        Esto se guarda en las pestañas Dataset de Vertex AI.
        
        Args:
        ----------
        name: str.
            Nombre del TabularDataset.
        
        gcs_source: Optional[str].
            URI de GCS donde se encuentra el dataset para referencia. (Ya debe estar creado en GCS).
        
        bq_source: Optional[str].
            URI de BigQuery donde se encuentra el dataset para referencia. (Ya debe estar creado en BigQuery).
        
        Returns:
        ----------
        dataset: aiplatform.TabularDataset.
            Dataset creado para dar un punto de inicio a la experimentación."""

        logging.info(f"Creando TabularDataset: {name}")

        try:
            dataset = aiplatform.TabularDataset.create(display_name = name,
                                                       gcs_source = gcs_source,
                                                       bq_source = bq_source)
            logging.info(f"TabularDataset creado: {name}")
            return dataset
        except Exception as e:
            logging.error(f"Error al crear TabularDataset: {e}")
            raise e
        
    def upload_trained_model(self, name: str, gcs_source: str, serving_container_image_uri: str) -> aiplatform.Model:
        """Método para cargar un modelo entrenado en GCS a Vertex AI.
        
        Args:
        ----------
        name: str.
            Nombre del modelo.
        
        gcs_source: str.
            URI de GCS donde se encuentra el modelo entrenado.
            (Ya debe estar creado en GCS y debe tener formato "gs://my-bucket/models/mlb/v1/", es importante que lo guarde como "model.pkl").
        
        serving_container_image_uri: str.
            URI del contenedor de Vertex AI que contiene referencia al modelo entrenado.
            Usualmente se usa "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest".
        
        Returns:
        ----------
        model: aiplatform.Model.
            Modelo cargado en Vertex AI."""

        logging.info(f"Cargando modelo entrenado en Vertex AI: {name}")
        try:
            models = aiplatform.Model.list(filter = f'display_name="{name}"')
            if not models:
                logging.error(f"No se halló el modelo {name} en Vertex AI.")

                model = aiplatform.Model.upload(display_name = name,
                                                artifact_uri = gcs_source,
                                                serving_container_image_uri = serving_container_image_uri)
                logging.info(f"Modelo cargado: {name}")
                return model
            else:
                logging.error(f"Parent Model encontrado: {name}. Creando versión nueva versión.")

                model = aiplatform.Model.upload(display_name = name,
                                                parent_model = models[0].resource_name,
                                                artifact_uri = gcs_source,
                                                serving_container_image_uri = serving_container_image_uri)
                logging.info(f"Modelo cargado: {name}")
                return model
        except Exception as e:
            logging.error(f"Error al cargar modelo: {e}")
            raise e

    def get_trained_model(self, name: str) -> aiplatform.Model:
        """Método para obtener un modelo entrenado en Vertex AI.
        
        Args:
        ----------
        name: str.
            Nombre del modelo."""
        
        logging.info(f"Obteniendo modelo entrenado en Vertex AI: {name}")

        try:
            model = aiplatform.Model(model_name = name)
            logging.info(f"Modelo obtenido: {name}")
            return model
        except Exception as e:
            logging.error(f"Error al obtener modelo: {e}")
            raise e
        
    @staticmethod
    def save_ephemeral_file(vertex_object: Any, content: Any, file_name: str) -> None:
        """Método estático para comunicación entre componentes de KubeFlow.
        
        Args:
        ----------
        vertex_object: Any.
            Objeto de comunicación entre Components.
            
        content: Any.
            Contenido del archivo.
        
        file_name: str.
            Nombre del archivo."""

        name, extension = file_name.split(".")

        os.makedirs(vertex_object.path, exist_ok = True)
        path = os.path.join(vertex_object.path, file_name)

        if extension == "csv":
            content.to_csv(path, index = False)
        elif extension == "parquet":
            content.to_parquet(path, index = False)
        elif extension == "json":
            with open(path, "w") as f:
                json.dump(content, f)
        elif extension == "pickle":
            with open(path, "wb") as f:
                pickle.dump(content, f)
        else:
            raise ValueError(f"Extensión {extension} no soportada.")
            
