from uuid import uuid4

import numpy as np

from src.domain.entities.user_profile import UserProfile

CATEGORIES = [
    "sneakers", "gorras", "relojes", "lentes", "carteras",
    "bolsos", "pulsos", "bisutería", "coleccionables", "otros",
]
CONDITIONS = ["nuevo", "seminuevo", "usado"]

# Rangos por arquetipo, calibrados a mano según la sección 9 de
# VAULT_CONTEXT.md. Sirven solo para bootstrap del modelo antes de tener
# usuarios reales -- se reemplazan por retrain_with_real_users.
ARCHETYPES = {
    "casual": {
        "total_assets": (1, 3),
        "avg_purchase_value": (30, 150),
        "maintenance_frequency": (0.0, 0.3),
        "community_activity": (0.0, 0.05),
        "days_since_last_maintenance": (60, 400),
    },
    "coleccionista": {
        "total_assets": (5, 25),
        "avg_purchase_value": (200, 1200),
        "maintenance_frequency": (0.2, 1.0),
        "community_activity": (0.05, 0.3),
        "days_since_last_maintenance": (10, 120),
    },
    "enthusiast_restaurador": {
        "total_assets": (3, 15),
        "avg_purchase_value": (80, 500),
        "maintenance_frequency": (1.0, 4.0),
        "community_activity": (0.2, 0.6),
        "days_since_last_maintenance": (0, 15),
    },
}


class GenerateSyntheticUsers:
    """
    Use case: genera N usuarios sintéticos de VAULT distribuidos en los
    3 arquetipos esperados, para entrenar el modelo de segmentación
    antes de tener suficientes usuarios reales.

    Responsabilidad única: producir registros de entrenamiento. No
    entrena modelos, no hace feature engineering (eso lo hace
    ExtractUserFeatures sobre el UserProfile reconstruido).
    """

    def __init__(self, seed: int = 42) -> None:
        self._rng = np.random.default_rng(seed)

    def execute(self, n: int) -> list[dict]:
        archetypes = list(ARCHETYPES.keys())
        records = []

        for _ in range(n):
            archetype = self._rng.choice(archetypes)
            profile = self._sample_profile(archetype)
            record = profile.to_record()
            record["true_segment"] = archetype
            records.append(record)

        return records

    def _sample_profile(self, archetype: str) -> UserProfile:
        ranges = ARCHETYPES[archetype]
        rng = self._rng

        total_assets = int(rng.integers(*ranges["total_assets"]))
        categories = self._sample_categories(total_assets)
        condition_distribution = self._sample_conditions(total_assets)

        return UserProfile(
            user_id=uuid4(),
            total_assets=total_assets,
            categories=categories,
            avg_purchase_value=float(rng.uniform(*ranges["avg_purchase_value"])),
            maintenance_frequency=float(rng.uniform(*ranges["maintenance_frequency"])),
            community_activity=float(rng.uniform(*ranges["community_activity"])),
            days_since_last_maintenance=int(rng.integers(*ranges["days_since_last_maintenance"])),
            most_common_category=max(categories, key=categories.get),
            condition_distribution=condition_distribution,
        )

    def _sample_categories(self, total_assets: int) -> dict[str, int]:
        n_distinct = min(self._rng.integers(1, 4), total_assets)
        chosen = self._rng.choice(CATEGORIES, size=n_distinct, replace=False)
        counts = self._rng.multinomial(total_assets, np.full(n_distinct, 1 / n_distinct))
        return {cat: int(count) for cat, count in zip(chosen, counts) if count > 0}

    def _sample_conditions(self, total_assets: int) -> dict[str, int]:
        weights = self._rng.dirichlet(np.ones(len(CONDITIONS)))
        counts = self._rng.multinomial(total_assets, weights)
        return {cond: int(count) for cond, count in zip(CONDITIONS, counts) if count > 0}
