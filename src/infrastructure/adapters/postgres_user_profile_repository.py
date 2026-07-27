from datetime import date, datetime
from uuid import UUID

import psycopg2
import psycopg2.extras

from src.domain.entities.user_profile import UserProfile
from src.domain.repositories.user_profile_repository import UserProfileRepository
from src.infrastructure.config.settings import settings

# Nombres de tabla/columna verificados contra VaultDB.sql (DDL real).
# Notas relevantes para el resto de este archivo:
#   - assets NO tiene updated_at, solo created_at.
#   - maintenance_logs.performed_at es DATE (no timestamp).
#   - users.created_at / posts.created_at / comments.created_at son
#     "timestamp without time zone" -> psycopg2 los devuelve como
#     datetime NAIVE, por eso todo el módulo trabaja en naive UTC.
PROFILE_SQL = """
WITH asset_stats AS (
    SELECT
        user_id,
        COUNT(*) AS total_assets,
        AVG(purchase_value) AS avg_purchase_value,
        MODE() WITHIN GROUP (ORDER BY category) AS most_common_category
    FROM assets
    WHERE user_id = %(user_id)s
    GROUP BY user_id
),
category_counts AS (
    SELECT category, COUNT(*) AS n
    FROM assets
    WHERE user_id = %(user_id)s
    GROUP BY category
),
condition_counts AS (
    SELECT condition, COUNT(*) AS n
    FROM assets
    WHERE user_id = %(user_id)s
    GROUP BY condition
),
maintenance_stats AS (
    SELECT
        COUNT(*) AS n_maintenance,
        MAX(m.performed_at) AS last_maintenance_at,
        MIN(m.performed_at) AS first_maintenance_at
    FROM maintenance_logs m
    JOIN assets a ON a.id = m.asset_id
    WHERE a.user_id = %(user_id)s
),
community_stats AS (
    SELECT
        (SELECT COUNT(*) FROM posts WHERE user_id = %(user_id)s) AS n_posts,
        (SELECT COUNT(*) FROM comments WHERE user_id = %(user_id)s) AS n_comments,
        (SELECT COUNT(*) FROM post_likes WHERE user_id = %(user_id)s) AS n_likes
),
user_account AS (
    SELECT created_at AS user_created_at FROM users WHERE id = %(user_id)s
)
SELECT
    asset_stats.total_assets,
    asset_stats.avg_purchase_value,
    asset_stats.most_common_category,
    maintenance_stats.n_maintenance,
    maintenance_stats.last_maintenance_at,
    maintenance_stats.first_maintenance_at,
    community_stats.n_posts,
    community_stats.n_comments,
    community_stats.n_likes,
    user_account.user_created_at
FROM asset_stats, maintenance_stats, community_stats, user_account
"""

ALL_USER_IDS_WITH_RECENT_ACTIVITY_SQL = """
SELECT DISTINCT user_id FROM (
    SELECT user_id, created_at AS at FROM assets
    UNION ALL
    SELECT user_id, created_at AS at FROM posts
    UNION ALL
    SELECT user_id, created_at AS at FROM comments
    UNION ALL
    SELECT a.user_id, m.created_at AS at
    FROM maintenance_logs m
    JOIN assets a ON a.id = m.asset_id
) activity
WHERE %(updated_since)s IS NULL OR at >= %(updated_since)s
"""


class PostgresUserProfileRepository(UserProfileRepository):
    """
    Implementación de UserProfileRepository que consulta directamente
    Supabase Postgres con service_role key (nunca anon key). Este
    microservicio no posee las tablas de negocio -- son propiedad de
    vault-backend -- pero las lee para construir perfiles de usuario.
    """

    def __init__(self) -> None:
        self._dsn = settings.database_url

    def _connect(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(self._dsn)

    def get_profile(self, user_id: UUID) -> UserProfile:
        with self._connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(PROFILE_SQL, {"user_id": str(user_id)})
                row = cur.fetchone()

                if row is None or row["total_assets"] is None:
                    raise ValueError(f"El usuario {user_id} no tiene assets registrados.")

                cur.execute(
                    "SELECT category, COUNT(*) AS n FROM assets WHERE user_id = %(user_id)s GROUP BY category",
                    {"user_id": str(user_id)},
                )
                categories = {r["category"]: r["n"] for r in cur.fetchall()}

                cur.execute(
                    'SELECT condition, COUNT(*) AS n FROM assets WHERE user_id = %(user_id)s GROUP BY condition',
                    {"user_id": str(user_id)},
                )
                condition_distribution = {r["condition"]: r["n"] for r in cur.fetchall()}

        return self._to_profile(user_id, row, categories, condition_distribution)

    def get_all_profiles(self, updated_since: str | None = None) -> list[UserProfile]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(ALL_USER_IDS_WITH_RECENT_ACTIVITY_SQL, {"updated_since": updated_since})
                user_ids = [row[0] for row in cur.fetchall()]

        profiles = []
        for user_id in user_ids:
            try:
                profiles.append(self.get_profile(UUID(str(user_id))))
            except ValueError:
                continue
        return profiles

    @staticmethod
    def _to_profile(
        user_id: UUID,
        row: dict,
        categories: dict[str, int],
        condition_distribution: dict[str, int],
    ) -> UserProfile:
        # maintenance_logs.performed_at es DATE -> se compara contra date.today().
        today = date.today()
        # users.created_at es timestamp NAIVE (sin tz) -> now naive en UTC.
        now = datetime.utcnow()

        last_maintenance_at = row["last_maintenance_at"]
        days_since_last_maintenance = (
            (today - last_maintenance_at).days if last_maintenance_at else -1
        )

        n_maintenance = row["n_maintenance"] or 0
        first_maintenance_at = row["first_maintenance_at"]
        months_active = (
            max((today - first_maintenance_at).days / 30.0, 1.0) if first_maintenance_at else 1.0
        )
        maintenance_frequency = n_maintenance / months_active

        n_community = (row["n_posts"] or 0) + (row["n_comments"] or 0) + (row["n_likes"] or 0)
        user_created_at = row["user_created_at"]
        days_active = max((now - user_created_at).days, 1) if user_created_at else 1
        community_activity = n_community / days_active

        return UserProfile(
            user_id=user_id,
            total_assets=row["total_assets"],
            categories=categories,
            avg_purchase_value=float(row["avg_purchase_value"] or 0.0),
            maintenance_frequency=maintenance_frequency,
            community_activity=community_activity,
            days_since_last_maintenance=days_since_last_maintenance,
            most_common_category=row["most_common_category"] or "",
            condition_distribution=condition_distribution,
        )
