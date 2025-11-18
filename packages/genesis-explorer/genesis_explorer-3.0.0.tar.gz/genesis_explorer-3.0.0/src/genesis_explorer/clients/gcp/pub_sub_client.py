"""Módulo que define el cliente para comunicación con Pub/Sub."""

# Librerías Externas.
from typing import Callable, Optional, List, Dict, Any

import logging

from google.cloud import pubsub_v1
from google.api_core.exceptions import AlreadyExists


# Librerías Internas.
from genesis_explorer.clients.base.base_messaging import BaseMessaging


logging.basicConfig(level = logging.INFO,
                    format = "%(asctime)s - %(levelname)s - %(message)s")


class PubSubService(BaseMessaging):
    """Clase que implementa el contrato de servicios de mensajería."""

    def __init__(self, project_id: str) -> None:
        """Método de instanciación de clase.
        
        Args:
        ----------
        project_id: str
            Identificador del proyecto de Google Cloud Platform."""
        
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()

    def create_topic(self, topic_name: str) -> None:
        """Método para crear un tópico de Pub/Sub.
        
        Args:
        ----------
        topic_name: str
            Nombre del tópico de Pub/Sub."""
        
        logging.info(f"Creando el tópico: {topic_name}.")
        topic_path = self.publisher.topic_path(project = self.project_id, topic = topic_name)

        try:
            self.publisher.create_topic(request = {"name": topic_path})
            logging.info(f"Tópico creado correctamente: {topic_path}.")
        except AlreadyExists:
            logging.info(f"El tópico {topic_name} ya existe.")
        except Exception as e:
            raise Exception(f"Error al crear el tópico de Pub/Sub: {e}")
        
    def subscribe(self, sub_name: str, topic_name: str) -> None:
        """Método para suscribirse a un tópico de Pub/Sub.
        
        Args:
        ----------
        sub_name: str
            Nombre de la suscripción de Pub/Sub.

        topic_name: str
            Nombre del tópico de Pub/Sub."""
        
        logging.info(f"Suscribiéndose al tópico: {topic_name}.")
        topic_path = self.publisher.topic_path(project = self.project_id, topic = topic_name)
        subscription_path = self.subscriber.subscription_path(project = self.project_id, subscription = sub_name)

        try:
            self.subscriber.create_subscription(request = {"name": subscription_path, "topic": topic_path})
            logging.info(f"Suscripción creada correctamente: {subscription_path}.")
        except AlreadyExists:
            logging.info(f"La suscripción {sub_name} ya existe.")
        except Exception as e:
            raise Exception(f"Error al crear la suscripción de Pub/Sub: {e}")
            
    def publish(self, topic_name: str, message: str) -> None:
        """Método para publicar un mensaje en un tópico de Pub/Sub.
        
        Args:
        ----------
        topic_name: str
            Nombre del tópico de Pub/Sub.

        message: str
            Mensaje a publicar."""
        
        logging.info(f"Publicando el mensaje en el tópico: {topic_name}.")
        topic_path = self.publisher.topic_path(project = self.project_id, topic = topic_name)

        try:
            encoded_message = str(message).encode("utf-8")
            future = self.publisher.publish(topic = topic_path, data = encoded_message)

            future.result()
            logging.info(f"Mensaje publicado correctamente en {topic_path}.")
        except Exception as e:
            logging.error(f"Error al publicar el mensaje en {topic_path}: {e}")

    def batch_pull(self, sub_name: str, max_messages: Optional[int] = 10) -> List[Dict[str, Any]]:
        """Método para obtener mensajes de un tópico de Pub/Sub en lotes.
        
        Args:
        ----------
        sub_name: str
            Nombre de la suscripción de Pub/Sub.

        max_messages: Optional[int]
            Número máximo de mensajes a obtener.

        Returns:
        ----------
        List[Dict[str, Any]].
            Lista de mensajes obtenidos."""
        
        logging.info(f"Obteniendo mensajes de la suscripción: {sub_name}.")

        subscription_path = self.subscriber.subscription_path(project = self.project_id,
                                                              subscription = sub_name)

        response = self.subscriber.pull(request = {"subscription": subscription_path,
                                                   "max_messages": max_messages})
        
        messages = []
        for msg in response.received_messages:
            messages.append({"ack_id": msg.ack_id,
                             "data": msg.message.data.decode("utf-8"),
                             "publish_time": msg.message.publish_time})
            
            logging.info(f"Marcando como leído el mensaje: {msg.ack_id}")
            self.subscriber.acknowledge(request = {"subscription": subscription_path,
                                                   "ack_ids": [msg.ack_id]})
            logging.info(f"Mensaje marcado como leído.")

        return messages
        
    def stream_pull(self, sub_name: str, callback: Callable) -> pubsub_v1.subscriber.futures.StreamingPullFuture:
        """Método para suscribirse a un tópico de Pub/Sub en streaming.
        
        Args:
        ----------
        sub_name: str
            Nombre de la suscripción de Pub/Sub.

        callback: Callable
            Función de callback para procesar los mensajes.

        Returns:
        ----------
        pubsub_v1.subscriber.futures.StreamingPullFuture.
            Cliente de suscripción de Pub/Sub."""

        subscription_path = self.subscriber.subscription_path(project = self.project_id, subscription = sub_name)
        streaming_pull_future = self.subscriber.subscribe(subscription = subscription_path, callback = callback)
        return streaming_pull_future

    def __str__(self) -> str:
        """Método para obtener la representación en cadena de caracteres de la clase.
        
        Returns:
        ----------
        str: Representación en cadena de caracteres de la clase."""

        self.publisher.list_topics(name = "mlops-credits-vertex-poc",)

        return f"PubSubService(project_id = {self.project_id})"
