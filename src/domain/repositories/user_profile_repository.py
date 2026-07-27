from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.user_profile import UserProfile


class UserProfileRepository(ABC):
    """
    Puerto para construir el UserProfile de un usuario a partir de sus
    datos reales en Supabase (assets, maintenance_logs, posts, comments,
    post_likes, reviews). Este microservicio no posee esas tablas -- las
    consulta directamente con service_role key, ya que Postgres/Supabase
    es compartido entre vault-backend y vault-ai-service.
    """

    @abstractmethod
    def get_profile(self, user_id: UUID) -> UserProfile:
        """Construye el perfil actual de un usuario. Falla si no tiene assets."""
        raise NotImplementedError

    @abstractmethod
    def get_all_profiles(self, updated_since: str | None = None) -> list[UserProfile]:
        """
        Construye el perfil de todos los usuarios con actividad reciente,
        usado en reentrenamiento incremental y por lotes.
        """
        raise NotImplementedError
