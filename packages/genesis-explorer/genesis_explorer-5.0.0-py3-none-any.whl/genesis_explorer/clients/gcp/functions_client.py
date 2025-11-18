"""Módulo que define un cliente para la comunicación con Cloud Functions."""

# Librerías Externas.
from typing import Tuple, Optional

from google.cloud import functions_v2

# Librerías Internas.
from genesis_explorer.clients.base.base_functions import BaseFunction


class CloudFunction(BaseFunction):
    """Clase que define un cliente para la comunicación con Cloud Functions."""

    def __init__(self, project_id: str,
                 location: Optional[str] = "us-east1") -> None:
        """Método de instanciación de clase.
        
        Args:
        ----------
        project_id: str.
            ID del proyecto de GCP sobre el cual se creará el cliente.

        location: str.
            Región de GCP donde se creará la función."""

        self.project_id = project_id
        self.parent = f"projects/{project_id}/locations/{location}"

        self.functions_client = functions_v2.FunctionServiceClient()

    def create_function(self,
                        fn_name: str,
                        trigger_type: str,
                        entry_point: str,
                        source_archive_url: str,
                        runtime: Optional[str] = "python312",
                        trigger_topic_name: Optional[str] = None,
                        trigger_bucket_name: Optional[str] = None,
                        environment_variables: Optional[dict] = None) -> None:
        """Método que, dada la ruta a su archivo zip (que contiene el script de la función
        y sus requirements) en GCS, crea una Cloud Function en GCP.
        
        Args:
        ----------
        fn_name: str.
            Nombre de la función.
            
        trigger_type: str.
            Tipo de trigger de la función.
            
        entry_point: str.
            Nombre de la función en el script que la define.
            
        source_archive_url: str.
            URL del archivo zip que contiene el script de la función y sus requirements.
            
        bucket_name: str.
            Nombre del bucket de GCS donde se encuentra el archivo zip.
            
        runtime: str.
            Runtime de la función.
            
        topic_name: str.
            Nombre del topic de PubSub. Se usa si su trigger es de tipo PubSub.
            
        bucket_name: str.
            Nombre del bucket de GCS donde se encuentra el archivo zip. Se usa si su trigger es de tipo Storage.
            
        environment_variables: dict.
            Variables de entorno de la función."""

        function_name = f"{self.parent}/functions/{fn_name}"

        bucket_name, object_name = CloudFunction.__split_source_archive_url(source_archive_url)

        build_config = functions_v2.BuildConfig(runtime = runtime,
                                                entry_point = entry_point,
                                                environment_variables = environment_variables or {},
                                                source = functions_v2.Source(storage_source = functions_v2.StorageSource(bucket = bucket_name,
                                                                                                                         object_ = object_name)))

        if trigger_type == "http":
            event_trigger = None

        elif trigger_type == "pubsub":
            if trigger_topic_name is None:
                raise ValueError("El nombre del topic es obligatorio.")
            
            event_trigger = functions_v2.EventTrigger(event_type = "google.cloud.pubsub.topic.v1.messagePublished",
                                                      pubsub_topic = f"projects/{self.project_id}/topics/{trigger_topic_name}")
            
        elif trigger_type == "storage":
            if trigger_bucket_name is None:
                raise ValueError("El nombre del bucket es obligatorio.")
            
            event_trigger = functions_v2.EventTrigger(event_type = "google.storage.object.finalize",
                                                      event_filters = [functions_v2.EventFilter(attribute = "bucket",
                                                                                                value = trigger_bucket_name)])

        else:
            raise ValueError(f"El tipo de trigger {trigger_type} no es válido.")

        function = functions_v2.Function(name = function_name,
                                         description = "Trigger de entrenamiento del modelo.",
                                         build_config = build_config,
                                         event_trigger = event_trigger)

        operation = functions_v2.CreateFunctionRequest(parent = self.parent,
                                                       function = function,
                                                       function_id = fn_name)

        operation = self.functions_client.create_function(request = operation)
        operation.result()
    
    @staticmethod
    def __split_source_archive_url(source_archive_url: str) -> Tuple[str, str]:
        """Método estático y privado que, dado el URL de un archivo zip en GCS,
        devuelve el nombre del bucket y el nombre del objeto.
        
        Args:
        ----------
        source_archive_url: str.
            URL del archivo zip que contiene el script de la función y sus requirements.

        Returns:
        ----------
        bucket_name: str.
            Nombre del bucket de GCS donde se encuentra el archivo zip.
            
        object_name: str.
            Nombre del objeto en el bucket de GCS donde se encuentra el archivo zip."""

        bucket_name, object_name = source_archive_url.replace("gs://", "").split("/", 1)
        return bucket_name, object_name
