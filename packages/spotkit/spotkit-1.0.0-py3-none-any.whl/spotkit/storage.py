from __future__ import annotations
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from spotkit.config import CONFIG_DIR
from spotkit.logger import get_logger
from spotkit.exceptions import SpotKitStorageError, SpotKitValidationError

LOG = get_logger(__name__)

DB_PATH = CONFIG_DIR / "metadata.db"
SCHEMA_VERSION = 1

CREATE_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);
"""

CREATE_TRACK_METADATA_TABLE = """
CREATE TABLE IF NOT EXISTS track_metadata (
    track_uri TEXT PRIMARY KEY,
    track_name TEXT NOT NULL,
    artist_name TEXT NOT NULL,
    user_rating INTEGER CHECK(user_rating >= 1 AND user_rating <= 5),
    user_comment TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
"""


class MetadataStorage:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return self
        except sqlite3.Error as e:
            LOG.error("Failed to connect to database: %s", e)
            raise SpotKitStorageError("connect", details=str(e))

    def __exit__(self, exc_type, exc, tb):
        if self.conn:
            try:
                if exc:
                    self.conn.rollback()
                    LOG.debug("Transaction rolled back due to error")
                else:
                    self.conn.commit()
                    LOG.debug("Transaction committed")
            except sqlite3.Error as e:
                LOG.error("Failed to finalize transaction: %s", e)
            finally:
                self.conn.close()

    # --- Schema Management ---

    def init_db(self):
        LOG.info("Initializing metadata DB")

        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            LOG.error("Failed to create config directory: %s", e)
            raise SpotKitStorageError("create directory", details=str(e))

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(CREATE_VERSION_TABLE)
                conn.execute(CREATE_TRACK_METADATA_TABLE)

                cur = conn.execute("SELECT version FROM schema_version")
                row = cur.fetchone()

                if row is None:
                    conn.execute(
                        "INSERT INTO schema_version (version) VALUES (?)",
                        (SCHEMA_VERSION,),
                    )
                    LOG.info("DB initialized with schema version %s", SCHEMA_VERSION)
                else:
                    current_version = row[0]
                    if current_version != SCHEMA_VERSION:
                        LOG.error(
                            "Schema version mismatch: %s != %s",
                            current_version,
                            SCHEMA_VERSION,
                        )
                        raise SpotKitStorageError(
                            "schema version mismatch",
                            details=f"Database version {current_version}, expected {SCHEMA_VERSION}",
                        )
                    LOG.info(
                        "DB already initialized with schema version %s", SCHEMA_VERSION
                    )
        except sqlite3.Error as e:
            LOG.error("Failed to initialize database: %s", e)
            raise SpotKitStorageError("initialize", details=str(e))

    # --- CRUD operations ---

    def upsert_track_metadata(
        self,
        track_uri: str,
        track_name: str,
        artist_name: str,
        user_rating: Optional[int] = None,
        user_comment: Optional[str] = None,
    ):
        if not track_uri:
            raise SpotKitValidationError("track_uri", track_uri, "non-empty string")
        if not track_name:
            raise SpotKitValidationError("track_name", track_name, "non-empty string")
        if not artist_name:
            raise SpotKitValidationError("artist_name", artist_name, "non-empty string")
        if user_rating is not None and not (1 <= user_rating <= 5):
            raise SpotKitValidationError(
                "user_rating", user_rating, "integer between 1 and 5"
            )

        now = datetime.utcnow().isoformat()

        try:
            self.conn.execute(
                """
                INSERT INTO track_metadata (track_uri, track_name, artist_name, user_rating, user_comment, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(track_uri) DO UPDATE SET
                    track_name=excluded.track_name,
                    artist_name=excluded.artist_name,
                    user_rating=excluded.user_rating,
                    user_comment=excluded.user_comment,
                    updated_at=excluded.updated_at
                """,
                (
                    track_uri,
                    track_name,
                    artist_name,
                    user_rating,
                    user_comment,
                    now,
                    now,
                ),
            )
            LOG.debug("Upserted metadata for track: %s", track_uri)
        except sqlite3.Error as e:
            LOG.error("Failed to upsert track metadata: %s", e)
            raise SpotKitStorageError("upsert track", details=str(e))

    def get_track_metadata(self, track_uri: str) -> Optional[Dict[str, Any]]:
        if not track_uri:
            raise SpotKitValidationError("track_uri", track_uri, "non-empty string")

        try:
            cur = self.conn.execute(
                "SELECT * FROM track_metadata WHERE track_uri = ?",
                (track_uri,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            LOG.error("Failed to get track metadata: %s", e)
            raise SpotKitStorageError("get track", details=str(e))

    def list_metadata(self) -> List[Dict[str, Any]]:
        try:
            cur = self.conn.execute("SELECT * FROM track_metadata")
            return [dict(r) for r in cur.fetchall()]
        except sqlite3.Error as e:
            LOG.error("Failed to list metadata: %s", e)
            raise SpotKitStorageError("list metadata", details=str(e))

    # --- Comments & Ratings CRUD ---

    def set_comment(self, track_uri: str, comment: str, track_info: dict):
        """Upsert com comentário."""
        if not track_uri:
            raise SpotKitValidationError("track_uri", track_uri, "non-empty string")

        try:
            self.upsert_track_metadata(
                track_uri=track_uri,
                track_name=track_info["name"],
                artist_name=track_info["artist"],
                user_comment=comment,
                user_rating=self.get_rating(track_uri),  # preserve existing rating
            )
            LOG.info("Comment set for track: %s", track_uri)
        except (SpotKitStorageError, SpotKitValidationError):
            raise
        except Exception as e:
            LOG.error("Unexpected error setting comment: %s", e)
            raise SpotKitStorageError("set comment", details=str(e))

    def get_comment(self, track_uri: str) -> str | None:
        row = self.get_track_metadata(track_uri)
        return row["user_comment"] if row else None

    def set_rating(self, track_uri: str, rating: int, track_info: dict):
        """Upsert com rating validado."""
        if not track_uri:
            raise SpotKitValidationError("track_uri", track_uri, "non-empty string")

        if rating is not None and not (1 <= rating <= 5):
            raise SpotKitValidationError("rating", rating, "integer between 1 and 5")

        try:
            self.upsert_track_metadata(
                track_uri=track_uri,
                track_name=track_info["name"],
                artist_name=track_info["artist"],
                user_rating=rating,
                user_comment=self.get_comment(track_uri),  # preserve existing comment
            )
            LOG.info("Rating set for track: %s", track_uri)
        except (SpotKitStorageError, SpotKitValidationError):
            raise
        except Exception as e:
            LOG.error("Unexpected error setting rating: %s", e)
            raise SpotKitStorageError("set rating", details=str(e))

    def get_rating(self, track_uri: str) -> int | None:
        row = self.get_track_metadata(track_uri)
        return row["user_rating"] if row else None

    def get_metadata(self, track_uri: str) -> dict | None:
        return self.get_track_metadata(track_uri)

    def get_all_metadata(self) -> list[dict]:
        return self.list_metadata()

    def delete_metadata(self, track_uri: str):
        if not track_uri:
            raise SpotKitValidationError("track_uri", track_uri, "non-empty string")

        try:
            self.conn.execute(
                "DELETE FROM track_metadata WHERE track_uri = ?", (track_uri,)
            )
            LOG.info("Deleted metadata for track: %s", track_uri)
        except sqlite3.Error as e:
            LOG.error("Failed to delete metadata: %s", e)
            raise SpotKitStorageError("delete metadata", details=str(e))
