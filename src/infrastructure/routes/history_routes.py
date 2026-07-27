from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.infrastructure.controllers.history_controller import HistoryController
from src.infrastructure.dependencies import get_history_controller

router = APIRouter(prefix="/history", tags=["Historial"])


@router.get("/", summary="Consultar historial de segmentación/recomendaciones")
def get_all(
    limit: int = Query(default=100, ge=1, le=1000),
    controller: HistoryController = Depends(get_history_controller),
) -> list[dict]:
    return controller.get_all(limit=limit)


@router.get("/user/{user_id}", summary="Consultar historial de un usuario específico")
def get_by_user(
    user_id: UUID,
    limit: int = Query(default=100, ge=1, le=1000),
    controller: HistoryController = Depends(get_history_controller),
) -> list[dict]:
    return controller.get_by_user(user_id, limit=limit)
