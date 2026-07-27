import json
from uuid import UUID

import psycopg2
import psycopg2.extras

from src.domain.entities.recommendation_result import RecommendationResult
from src.domain.repositories.recommendation_repository import RecommendationRepository
from src.infrastructure.config.settings import settings

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS recommendation_results (
    id                UUID PRIMARY KEY,
    user_id           UUID NOT NULL,
    cluster_id        INTEGER NOT NULL,
    segment_label     TEXT NOT NULL,
    cluster_distance  DOUBLE PRECISION NOT NULL,
    model_version     TEXT NOT NULL,
    recommendations   JSONB NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_recommendation_results_user_id ON recommendation_results(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_results_created_at ON recommendation_results(created_at);
"""

INSERT_SQL = """
INSERT INTO recommendation_results (
    id, user_id, cluster_id, segment_label, cluster_distance,
    model_version, recommendations, created_at
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


class PostgresRecommendationRepository(RecommendationRepository):
    def __init__(self) -> None:
        self._dsn = settings.database_url
        self._initialize()

    def _connect(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(self._dsn)

    def _initialize(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_SQL)

    def save(self, result: RecommendationResult) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_SQL, (
                    str(result.id),
                    str(result.user_id),
                    result.cluster_id,
                    result.segment_label,
                    result.cluster_distance,
                    result.model_version,
                    json.dumps(result.recommendations),
                    result.created_at,
                ))

    def get_all(self, limit: int = 100) -> list[RecommendationResult]:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM recommendation_results ORDER BY created_at DESC LIMIT %s",
                    (limit,),
                )
                return [self._to_entity(row) for row in cur.fetchall()]

    def get_by_user(self, user_id: UUID, limit: int = 100) -> list[RecommendationResult]:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM recommendation_results WHERE user_id = %s "
                    "ORDER BY created_at DESC LIMIT %s",
                    (str(user_id), limit),
                )
                return [self._to_entity(row) for row in cur.fetchall()]

    @staticmethod
    def _to_entity(row: psycopg2.extras.RealDictRow) -> RecommendationResult:
        return RecommendationResult(
            id=UUID(str(row["id"])),
            user_id=UUID(str(row["user_id"])),
            cluster_id=row["cluster_id"],
            segment_label=row["segment_label"],
            cluster_distance=row["cluster_distance"],
            model_version=row["model_version"],
            recommendations=row["recommendations"],
            created_at=row["created_at"],
        )
