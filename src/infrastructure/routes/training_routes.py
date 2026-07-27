from fastapi import APIRouter, Depends, HTTPException, Query

from src.infrastructure.controllers.training_controller import TrainingController
from src.infrastructure.dependencies import get_training_controller

router = APIRouter(prefix="/training", tags=["Entrenamiento"])


@router.post("/retrain")
def retrain(
    updated_since: str | None = Query(default=None),
    controller: TrainingController = Depends(get_training_controller),
) -> dict:
    """Trigger manual (admin) del reentrenamiento incremental de segmentación."""
    try:
        return controller.handle_retrain(updated_since=updated_since)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
