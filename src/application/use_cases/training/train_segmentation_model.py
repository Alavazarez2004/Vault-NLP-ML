import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, MiniBatchKMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.application.use_cases.feature_engineering.extract_user_features import FEATURE_NAMES

N_CLUSTERS = 3


def derive_cluster_labels(centroids_original: np.ndarray) -> dict[int, str]:
    """
    Mapea cluster_id -> segment_label inspeccionando los centroides ya
    des-escalados, según los arquetipos descritos en la sección 9 de
    VAULT_CONTEXT.md. Se reutiliza tanto en el entrenamiento inicial
    como en el reentrenamiento incremental, para que la etiqueta de un
    cluster no dependa de en qué orden K-Means lo haya enumerado.
    """
    idx = {name: i for i, name in enumerate(FEATURE_NAMES)}
    remaining = set(range(len(centroids_original)))

    collector_score = centroids_original[:, idx["total_assets"]] * centroids_original[:, idx["avg_purchase_value"]]
    coleccionista_id = int(np.argmax(collector_score))
    remaining.discard(coleccionista_id)

    enthusiast_score = {
        i: centroids_original[i, idx["maintenance_frequency"]]
        - centroids_original[i, idx["days_since_last_maintenance"]] / 30.0
        for i in remaining
    }
    enthusiast_id = max(enthusiast_score, key=enthusiast_score.get)
    remaining.discard(enthusiast_id)

    labels = {coleccionista_id: "coleccionista", enthusiast_id: "enthusiast_restaurador"}
    for i in remaining:
        labels[i] = "casual"
    return labels


class TrainSegmentationModel:
    """
    Use case: entrena el modelo de segmentación de usuarios con
    MiniBatchKMeans (permite reentrenamiento incremental vía
    partial_fit) y usa DBSCAN solo como diagnóstico de calidad/outliers,
    no como modelo servido.

    Responsabilidad única: entrenamiento completo. No genera datos, no
    hace feature engineering propio (recibe ya el DataFrame de
    registros), no persiste nada.
    """

    def execute(self, df: pd.DataFrame) -> tuple[MiniBatchKMeans, StandardScaler, dict[int, str], dict]:
        X = df[FEATURE_NAMES].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = MiniBatchKMeans(n_clusters=N_CLUSTERS, random_state=42, n_init="auto")
        kmeans.fit(X_scaled)

        centroids_original = scaler.inverse_transform(kmeans.cluster_centers_)
        cluster_label_map = derive_cluster_labels(centroids_original)

        metrics = self._evaluate(X_scaled, kmeans)
        return kmeans, scaler, cluster_label_map, metrics

    @staticmethod
    def _evaluate(X_scaled: np.ndarray, kmeans: MiniBatchKMeans) -> dict:
        labels = kmeans.predict(X_scaled)
        silhouette = float(silhouette_score(X_scaled, labels)) if len(set(labels)) > 1 else 0.0

        dbscan = DBSCAN(eps=1.5, min_samples=5)
        dbscan_labels = dbscan.fit_predict(X_scaled)
        noise_ratio = float(np.mean(dbscan_labels == -1))

        return {"silhouette_score": silhouette, "dbscan_noise_ratio": noise_ratio}
