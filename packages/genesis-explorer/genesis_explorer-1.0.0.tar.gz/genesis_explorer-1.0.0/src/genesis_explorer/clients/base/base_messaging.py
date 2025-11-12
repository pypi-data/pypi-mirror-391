"""Módulo que define la clase base para los clientes de mensajería."""

# Librerías Externas.
from typing import Callable, Optional, List, Dict, Any
from abc import ABC, abstractmethod

# Librerías Internas.
from migracion_gcp.lib.clients.base.core.singleton import SingletonMeta


class BaseMessaging(ABC, metaclass = SingletonMeta):
    """Clase que implementa el contrato de servicios de mensajería."""

    @abstractmethod
    def create_topic(self, topic_name: str) -> None:
        """Método para crear un tópico.
        
        Args:
        ----------
        topic_name: str
            Nombre del tópico."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseMessaging, debes implementar el método 'create_topic'.")

    @abstractmethod
    def publish(self, topic_name: str, message: str) -> None:
        """Método para publicar un mensaje en un tópico.
        
        Args:
        ----------
        topic_name: str
            Nombre del tópico.

        message: str
            Mensaje a publicar."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseMessaging, debes implementar el método 'publish'.")

    @abstractmethod
    def batch_pull(self, sub_name: str, max_messages: Optional[int] = 10) -> List[Dict[str, Any]]:
        """Método para obtener mensajes de un tópico.
        
        Args:
        ----------
        sub_name: str
            Nombre de la suscripción.

        max_messages: Optional[int]
            Número máximo de mensajes a obtener.

        Returns:
        ----------
        List[Dict[str, Any]].
            Lista de mensajes obtenidos."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseMessaging, debes implementar el método 'pull'.")

    @abstractmethod
    def subscribe(self, sub_name: str, topic_name: str) -> None:
        """Método para suscribirse a un tópico.
        
        Args:
        ----------
        sub_name: str
            Nombre de la suscripción.

        topic_name: str
            Nombre del tópico."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseMessaging, debes implementar el método 'subscribe'.")
    
    @abstractmethod
    def stream_pull(self, sub_name: str, callback: Callable) -> Any:
        """Método para suscribirse a un tópico en streaming.
        
        Args:
        ----------
        sub_name: str
            Nombre de la suscripción.
            
        callback: Callable
            Función de callback para procesar los mensajes.

        Returns:
        ----------
        Any.
            Cliente de suscripción."""
        
        raise NotImplementedError("Si tu clase implementa el contrato BaseMessaging, debes implementar el método 'stream_pull'.")
