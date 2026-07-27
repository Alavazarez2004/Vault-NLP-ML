from pydantic import BaseModel


class EntityDTO(BaseModel):
    text: str
    label: str
