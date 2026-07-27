from pydantic import BaseModel


class RecommendedItemDTO(BaseModel):
    item_id: str
    category: str
    brand: str
    model: str
    score: float
    strategy: str  # "content" | "cluster"
