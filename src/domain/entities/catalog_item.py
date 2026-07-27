from dataclasses import dataclass


@dataclass
class CatalogItem:
    """
    Artículo disponible en el catálogo de VAULT (ej. sneakers, relojes,
    gorras) que puede ser recomendado a un usuario. No confundir con
    AssetFeatures: esto describe el catálogo general, no un asset ya
    en posesión de un usuario.
    """

    item_id: str
    category: str
    brand: str
    model: str
    price_range: str  # "bajo" | "medio" | "alto"

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "category": self.category,
            "brand": self.brand,
            "model": self.model,
            "price_range": self.price_range,
        }
