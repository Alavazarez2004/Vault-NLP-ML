from uuid import UUID

import psycopg2
import psycopg2.extras

from src.domain.repositories.user_collection_repository import UserCollectionRepository
from src.infrastructure.adapters.static_catalog_repository import StaticCatalogRepository
from src.infrastructure.config.settings import settings

# Mapeo entre las categorías reales de la tabla `assets` (definidas en el
# backend Go, ver allowedCategories en CreateAssetRequest.go) y las
# categorías del catálogo fijo de recomendación (StaticCatalogRepository).
# No son 1:1: el backend distingue más categorías de las que el catálogo
# de recomendación cubre todavía.
CATEGORY_MAP: dict[str, str | None] = {
    "sneakers": "sneakers",
    "relojes": "relojes",
    "gorras": "gorras",
    "lentes": "lentes",
    "bolsos": "bolsas",
    "carteras": "bolsas",
    "bisuteria": "accesorios",
    "pulsos": "accesorios",
    "coleccionables": None,  # sin equivalente razonable en el catalogo
    "otros": None,
}

# Umbrales PROVISIONALES (MXN) para mapear purchase_value de un asset real
# a un rango de precio del catálogo (bajo/medio/alto). Ajustar cuando se
# tenga la distribución real de precios de los assets registrados; por
# ahora son un punto de partida razonable, no un valor definitivo.
UMBRAL_BAJO_MEDIO = 1500
UMBRAL_MEDIO_ALTO = 4000


def _price_bucket(purchase_value: float | None) -> str:
    if purchase_value is None:
        return "medio"
    if purchase_value < UMBRAL_BAJO_MEDIO:
        return "bajo"
    if purchase_value < UMBRAL_MEDIO_ALTO:
        return "medio"
    return "alto"


GET_USER_ASSETS_SQL = """
    SELECT category, brand, purchase_value
    FROM assets
    WHERE user_id = %(user_id)s
"""

ALL_USERS_WITH_ASSETS_SQL = "SELECT DISTINCT user_id FROM assets"


class PostgresUserCollectionRepository(UserCollectionRepository):
    """
    Relaciona los assets reales de un usuario (tabla `assets`, propiedad
    de vault-backend) con el item_id de un catálogo fijo, para que
    RecommendCatalogItems pueda funcionar con datos reales.

    La relación es APROXIMADA por diseño: `assets` no tiene columna
    catalog_item_id ni "model" (ver TODO original), así que se infiere
    por category + brand + rango de precio derivado de purchase_value.
    Cuando el equipo agregue una columna catalog_item_id a `assets`, esta
    clase se puede simplificar a un JOIN directo y este matching se
    vuelve innecesario.
    """

    def __init__(
        self,
        catalog_repository: StaticCatalogRepository | None = None,
        segment_user=None,
    ) -> None:
        self._dsn = settings.database_url
        self._catalog_repository = catalog_repository or StaticCatalogRepository()
        # Inyectado desde dependencies.py para evitar import circular
        # (SegmentUser vive en application/, esto es infrastructure/).
        self._segment_user = segment_user

    def _connect(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(self._dsn)

    def _match_item_id(self, category: str, brand: str, purchase_value: float | None) -> str | None:
        catalog_category = CATEGORY_MAP.get((category or "").lower())
        if catalog_category is None:
            return None

        candidates = [
            item
            for item in self._catalog_repository.get_all()
            if item.category == catalog_category
        ]
        if not candidates:
            return None

        brand_matches = [c for c in candidates if c.brand.lower() == (brand or "").lower()]
        pool = brand_matches or candidates

        bucket = _price_bucket(purchase_value)
        bucket_matches = [c for c in pool if c.price_range == bucket]
        pool = bucket_matches or pool

        # Determinístico: si aún hay varios candidatos empatados, se toma
        # el de item_id más chico para que el resultado sea reproducible.
        return sorted(pool, key=lambda c: c.item_id)[0].item_id

    def get_collection(self, user_id: UUID) -> set[str]:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(GET_USER_ASSETS_SQL, {"user_id": str(user_id)})
                rows = cur.fetchall()

        item_ids: set[str] = set()
        for row in rows:
            item_id = self._match_item_id(row["category"], row["brand"], row["purchase_value"])
            if item_id:
                item_ids.add(item_id)
        return item_ids

    def get_collections_by_cluster(self, cluster_id: int) -> dict[UUID, set[str]]:
        if self._segment_user is None:
            # Sin segment_user inyectado no hay forma barata de saber que
            # usuarios pertenecen a este cluster; se degrada a "nadie" en
            # vez de tronar, para que la estrategia "por contenido" en
            # RecommendCatalogItems siga funcionando aunque la de
            # "por cluster" no aporte nada en este caso.
            return {}

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(ALL_USERS_WITH_ASSETS_SQL)
                candidate_ids = [row[0] for row in cur.fetchall()]

        result: dict[UUID, set[str]] = {}
        for raw_id in candidate_ids:
            uid = UUID(str(raw_id))
            try:
                segment = self._segment_user.execute(uid, persist=False)
            except (ValueError, FileNotFoundError):
                # Usuario sin perfil suficiente, o modelo no entrenado:
                # se omite en vez de tronar toda la recomendacion.
                continue
            if segment.cluster_id != cluster_id:
                continue
            result[uid] = self.get_collection(uid)
        return result