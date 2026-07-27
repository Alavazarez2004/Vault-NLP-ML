from src.domain.entities.catalog_item import CatalogItem
from src.domain.repositories.catalog_repository import CatalogRepository

# (item_id, category, brand, model, price_range)
_CATALOG_DATA = [
    ("I01", "sneakers", "Nike", "Air Jordan 1 Retro High OG", "alto"),
    ("I02", "sneakers", "Nike", "Air Force 1", "medio"),
    ("I03", "sneakers", "Adidas", "Yeezy Boost 350", "alto"),
    ("I04", "sneakers", "New Balance", "550", "medio"),
    ("I05", "sneakers", "Nike", "Dunk Low", "medio"),
    ("I06", "relojes", "Rolex", "Submariner", "alto"),
    ("I07", "relojes", "Seiko", "5 Sports SRPD51K1", "medio"),
    ("I08", "relojes", "Casio", "G-Shock GA-2100", "bajo"),
    ("I09", "relojes", "Omega", "Speedmaster", "alto"),
    ("I10", "relojes", "Tissot", "PRX", "medio"),
    ("I11", "gorras", "New Era", "9FIFTY LA Dodgers", "bajo"),
    ("I12", "gorras", "New Era", "59FIFTY Yankees", "bajo"),
    ("I13", "gorras", "Nike", "Dri-FIT Club", "bajo"),
    ("I14", "lentes", "Ray-Ban", "Wayfarer RB2140", "medio"),
    ("I15", "lentes", "Ray-Ban", "Aviator", "medio"),
    ("I16", "lentes", "Oakley", "Holbrook", "medio"),
    ("I17", "bolsas", "Louis Vuitton", "Keepall", "alto"),
    ("I18", "bolsas", "Coach", "Tabby", "medio"),
    ("I19", "bolsas", "Herschel", "Novel Duffel", "bajo"),
    ("I20", "accesorios", "Pandora", "Pulsera Moments", "bajo"),
    ("I21", "accesorios", "Tiffany & Co.", "Collar T", "alto"),
]


class StaticCatalogRepository(CatalogRepository):
    """
    Implementación temporal del catálogo con datos fijos en memoria
    (los mismos del prototipo original). Cuando el catálogo real viva
    en Postgres, se reemplaza por un PostgresCatalogRepository sin
    tocar RecommendCatalogItems ni BuildCatalogSimilarity.
    """

    def get_all(self) -> list[CatalogItem]:
        return [CatalogItem(*row) for row in _CATALOG_DATA]
