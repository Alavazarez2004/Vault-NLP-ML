from uuid import UUID

from src.application.use_cases.feature_engineering.build_catalog_similarity import (
    BuildCatalogSimilarity,
)
from src.application.use_cases.realtime.segment_user import SegmentUser
from src.domain.dtos.recommended_item_dto import RecommendedItemDTO
from src.domain.entities.catalog_item import CatalogItem
from src.domain.repositories.catalog_repository import CatalogRepository
from src.domain.repositories.user_collection_repository import UserCollectionRepository


class RecommendCatalogItems:
    """
    Use case: recomienda artículos concretos del catálogo (no solo
    "servicios" genéricos) combinando dos estrategias:

      - contenido: artículos similares a los que el usuario ya tiene,
        vía similitud coseno sobre category/brand/price_range.
      - cluster: artículos populares entre usuarios de su mismo
        segmento (K-Means) que el usuario todavía no tiene.

    Responsabilidad única: orquestar ambas estrategias. No entrena, no
    segmenta (delega a SegmentUser), no decide de dónde sale el
    catálogo ni las colecciones (delega a los repositorios).
    """

    def __init__(
        self,
        segment_user: SegmentUser,
        catalog_repository: CatalogRepository,
        user_collection_repository: UserCollectionRepository,
        similarity_builder: BuildCatalogSimilarity | None = None,
    ) -> None:
        self._segment_user = segment_user
        self._catalog_repository = catalog_repository
        self._user_collection_repository = user_collection_repository
        self._similarity_builder = similarity_builder or BuildCatalogSimilarity()

    def execute(self, user_id: UUID, top_n: int = 3) -> list[RecommendedItemDTO]:
        catalog = self._catalog_repository.get_all()
        similarity = self._similarity_builder.execute(catalog)
        user_items = self._user_collection_repository.get_collection(user_id)

        content_limit = max(1, top_n // 2)
        cluster_limit = top_n - content_limit

        content_recommendations = self._by_content(
            catalog,
            similarity,
            user_items,
            content_limit
        )

        segment_result = self._segment_user.execute(user_id, persist=False)
        cluster_collections = self._user_collection_repository.get_collections_by_cluster(
            segment_result.cluster_id
        )
        cluster_recommendations = self._by_cluster(
            catalog,
            user_items,
            cluster_collections,
            cluster_limit
        )

        return content_recommendations + cluster_recommendations

    @staticmethod
    def _by_content(
        catalog: list[CatalogItem],
        similarity,
        user_items: set[str],
        top_n: int,
    ) -> list[RecommendedItemDTO]:
        if not user_items:
            return []

        idx_user = [i for i, item in enumerate(catalog) if item.item_id in user_items]
        avg_similarity = similarity[idx_user].mean(axis=0)

        scored = [
            (item, avg_similarity[i])
            for i, item in enumerate(catalog)
            if item.item_id not in user_items
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)

        return [
            RecommendedItemDTO(
                item_id=item.item_id,
                category=item.category,
                brand=item.brand,
                model=item.model,
                score=round(float(score), 4),
                strategy="content",
            )
            for item, score in scored[:top_n]
        ]

    @staticmethod
    def _by_cluster(
        catalog: list[CatalogItem],
        user_items: set[str],
        cluster_collections: dict[UUID, set[str]],
        top_n: int,
    ) -> list[RecommendedItemDTO]:
        counts: dict[str, int] = {}
        for items in cluster_collections.values():
            for item_id in items:
                counts[item_id] = counts.get(item_id, 0) + 1

        catalog_by_id = {item.item_id: item for item in catalog}
        scored = [
            (catalog_by_id[item_id], count)
            for item_id, count in counts.items()
            if item_id not in user_items and item_id in catalog_by_id
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)

        return [
            RecommendedItemDTO(
                item_id=item.item_id,
                category=item.category,
                brand=item.brand,
                model=item.model,
                score=float(count),
                strategy="cluster",
            )
            for item, count in scored[:top_n]
        ]
