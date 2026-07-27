from uuid import UUID

from src.domain.repositories.user_collection_repository import UserCollectionRepository

# TODO(equipo): la tabla `assets` real (ver PROFILE_SQL en
# postgres_user_profile_repository.py) guarda category/condition/
# purchase_value por asset, pero NO referencia un catálogo fijo de
# artículos con marca/modelo (I01, I02...) como el usado en
# StaticCatalogRepository. Antes de implementar este repositorio hay
# que decidir en equipo cómo se relaciona un asset real con un
# item_id del catálogo (¿se agrega una columna catalog_item_id a
# `assets`? ¿se matchea por category+brand+model?). Mientras tanto,
# usar un adaptador en memoria (ver tests) para poder desarrollar y
# probar RecommendCatalogItems sin bloquear por este punto.


class PostgresUserCollectionRepository(UserCollectionRepository):
    """
    Implementación real pendiente: requiere definir junto con el
    equipo cómo se relacionan los assets de un usuario con el
    item_id del catálogo (ver TODO arriba).
    """

    def get_collection(self, user_id: UUID) -> set[str]:
        raise NotImplementedError(
            "Falta definir la relación assets <-> catálogo antes de implementar esto."
        )

    def get_collections_by_cluster(self, cluster_id: int) -> dict[UUID, set[str]]:
        raise NotImplementedError(
            "Falta definir la relación assets <-> catálogo antes de implementar esto."
        )
