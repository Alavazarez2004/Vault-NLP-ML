import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.application.use_cases.dataset_generation.generate_synthetic_users import (
    GenerateSyntheticUsers,
)
from src.application.use_cases.training.train_recommendation_model import TrainRecommendationModel
from src.application.use_cases.training.train_segmentation_model import TrainSegmentationModel
from src.infrastructure.adapters.joblib_model_repository import JoblibModelRepository
from src.infrastructure.adapters.parquet_dataset_repository import ParquetDatasetRepository
from src.infrastructure.config.settings import settings


def main() -> None:
    dataset_repo = ParquetDatasetRepository(settings.data_dir)
    model_repo = JoblibModelRepository(settings.models_dir)

    print(f"[1/3] Generando {settings.n_synthetic_users} usuarios sintéticos...")
    generator = GenerateSyntheticUsers(seed=settings.random_seed)
    records = generator.execute(settings.n_synthetic_users)
    dataset_repo.save(records, "synthetic_users.parquet")
    print(f"      {len(records)} filas guardadas en data/generated/synthetic_users.parquet")

    df = dataset_repo.load("synthetic_users.parquet")

    print("[2/3] Entrenando modelo de segmentación (MiniBatchKMeans + DBSCAN diagnóstico)...")
    trainer_segment = TrainSegmentationModel()
    kmeans, scaler, cluster_label_map, metrics = trainer_segment.execute(df)
    model_repo.save(kmeans, "kmeans_segmentation.pkl")
    model_repo.save(scaler, "scaler_segmentation.pkl")
    model_repo.save(cluster_label_map, "cluster_label_map.pkl")
    print(f"      Etiquetas de cluster: {cluster_label_map}")
    print(
        f"      Silhouette: {metrics['silhouette_score']:.4f}  "
        f"DBSCAN noise ratio: {metrics['dbscan_noise_ratio']:.4f}"
    )

    print("[3/3] Derivando umbrales de recomendación...")
    trainer_recommend = TrainRecommendationModel()
    thresholds = trainer_recommend.execute(df)
    model_repo.save(thresholds, "recommendation_thresholds.pkl")
    print(f"      Umbrales: {thresholds}")

    print("\nListo. Modelos guardados en models/:")
    for f in sorted(settings.models_dir.glob("*.pkl")):
        print(f"      {f.name}")


if __name__ == "__main__":
    main()
