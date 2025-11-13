import time
from typing import Any, Dict, List, Optional
from rich.progress import Progress
from spotipy import Spotify, SpotifyException
from spotkit.auth import get_authenticated_client
from spotkit.logger import get_logger
from spotkit.exceptions import (
    SpotKitAPIError,
    SpotKitAuthError,
    SpotKitResourceNotFoundError,
)

LOG = get_logger(__name__)


class SpotifyClient:
    def __init__(self, client: Spotify = None):
        try:
            self._client = client or get_authenticated_client()
        except SpotKitAuthError:
            raise
        except Exception as e:
            LOG.error("Failed to initialize SpotifyClient: %s", e)
            raise SpotKitAuthError("Client initialization failed", details=str(e))

    def _retry(self, func, *args, **kwargs):
        """Retry logic with exponential backoff for transient failures."""
        delay = 0.5
        max_retries = 3

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except SpotifyException as e:
                status = e.http_status

                # Rate limiting - always retry
                if status == 429:
                    if attempt < max_retries - 1:
                        LOG.warning(
                            "Rate limited (429). Retry %s/%s in %.1fs",
                            attempt + 1,
                            max_retries,
                            delay,
                        )
                        time.sleep(delay)
                        delay *= 2
                        continue
                    LOG.error("Rate limit exceeded after %s retries", max_retries)
                    raise SpotKitAPIError(
                        "Rate limit exceeded",
                        status,
                        "Too many requests - wait before retrying",
                    )

                # Auth errors - don't retry
                if status in (401, 403):
                    LOG.error("Auth error %s: %s", status, e)
                    raise SpotKitAPIError(
                        f"Authentication error ({status})", status, str(e)
                    )

                # Server errors - retry
                if status >= 500:
                    if attempt < max_retries - 1:
                        LOG.warning(
                            "Server error %s. Retry %s/%s in %.1fs",
                            status,
                            attempt + 1,
                            max_retries,
                            delay,
                        )
                        time.sleep(delay)
                        delay *= 2
                        continue
                    LOG.error("Server error persisted after %s retries", max_retries)
                    raise SpotKitAPIError(
                        f"Spotify server error ({status})", status, str(e)
                    )

                # Other errors - raise immediately
                LOG.error("API error %s: %s", status, e)
                raise SpotKitAPIError(f"Spotify API error ({status})", status, str(e))

            except Exception as e:
                LOG.error("Unexpected error in API call: %s", e)
                raise SpotKitAPIError("Unexpected API error", details=str(e))

    def search_artist(self, name: str) -> Optional[Dict[str, Any]]:
        LOG.info("Searching artist: %s", name)

        try:
            result = self._retry(self._client.search, q=name, type="artist", limit=5)
            items: List[Dict[str, Any]] = result.get("artists", {}).get("items", [])

            if not items:
                LOG.warning("Artist not found: %s", name)
                raise SpotKitResourceNotFoundError("Artist", name)

            artist = items[0]
            LOG.info("Found artist: %s (ID: %s)", artist.get("name"), artist.get("id"))

            return {
                "id": artist.get("id"),
                "name": artist.get("name"),
                "popularity": artist.get("popularity"),
                "genres": artist.get("genres", []),
            }
        except SpotKitResourceNotFoundError:
            # raise
            return None
        except (SpotKitAPIError, SpotKitAuthError):
            raise
        except Exception as e:
            LOG.error("Unexpected error searching artist: %s", e)
            raise SpotKitAPIError("Artist search failed", details=str(e))

    def get_all_tracks(self, artist_id: str):
        LOG.info("Fetching all tracks for artist %s", artist_id)

        albums = []
        limit = 50
        offset = 0

        try:
            # Fetch albums paginated
            while True:
                result = self._retry(
                    self._client.artist_albums,
                    artist_id,
                    album_type="album,single,compilation",
                    limit=limit,
                    offset=offset,
                )
                items = result.get("items", [])
                if not items or not result.get("next"):
                    if items:
                        albums.extend(items)
                    break

                albums.extend(items)
                offset += limit

            LOG.info("Found %d albums/EPs/singles", len(albums))

            track_map = {}

            with Progress() as progress:
                task = progress.add_task("Fetching tracks...", total=len(albums))

                for album in albums:
                    album_id = album.get("id")
                    album_name = album.get("name")

                    progress.update(task, advance=1)

                    try:
                        # Pagination for tracks
                        t_limit = 50
                        t_offset = 0

                        while True:
                            tr = self._retry(
                                self._client.album_tracks,
                                album_id,
                                limit=t_limit,
                                offset=t_offset,
                            )
                            t_items = tr.get("items", [])
                            if not t_items or not tr.get("next"):
                                if t_items:
                                    for t in t_items:
                                        t_id = t.get("id")
                                        if t_id and t_id not in track_map:
                                            track_map[t_id] = {
                                                "uri": t.get("uri"),
                                                "name": t.get("name"),
                                                "artists": [
                                                    a.get("name")
                                                    for a in t.get("artists", [])
                                                ],
                                                "album": album_name,
                                                "duration_ms": t.get("duration_ms"),
                                            }
                                break

                            for t in t_items:
                                t_id = t.get("id")
                                if t_id and t_id not in track_map:
                                    track_map[t_id] = {
                                        "uri": t.get("uri"),
                                        "name": t.get("name"),
                                        "artists": [
                                            a.get("name") for a in t.get("artists", [])
                                        ],
                                        "album": album_name,
                                        "duration_ms": t.get("duration_ms"),
                                    }

                            t_offset += t_limit

                    except SpotKitAPIError as e:
                        LOG.error(
                            "Failed to fetch album %s (%s): %s", album_name, album_id, e
                        )
                        # Continue with other albums
                        continue

            tracks = list(track_map.values())
            LOG.info("Total unique tracks: %d", len(tracks))
            return tracks

        except (SpotKitAPIError, SpotKitAuthError):
            raise
        except Exception as e:
            LOG.error("Unexpected error fetching tracks: %s", e)
            raise SpotKitAPIError("Failed to fetch artist tracks", details=str(e))

    def list_user_playlists(self):
        LOG.info("Listing user playlists")

        playlists = []
        limit = 50
        offset = 0

        try:
            while True:
                result = self._retry(
                    self._client.current_user_playlists, limit=limit, offset=offset
                )
                items = result.get("items", [])
                if not items or not result.get("next"):
                    if items:
                        playlists.extend(items)
                    break

                playlists.extend(items)
                offset += limit

            LOG.info("Found %d playlists", len(playlists))
            return playlists
        except (SpotKitAPIError, SpotKitAuthError):
            raise
        except Exception as e:
            LOG.error("Unexpected error listing playlists: %s", e)
            raise SpotKitAPIError("Failed to list playlists", details=str(e))

    def get_playlist_by_name(self, name: str):
        LOG.info("Searching playlist: %s", name)
        name_lower = name.lower()

        try:
            for pl in self.list_user_playlists():
                if pl.get("name", "").lower() == name_lower:
                    LOG.info(
                        "Found playlist: %s (ID: %s)", pl.get("name"), pl.get("id")
                    )
                    return pl

            LOG.warning("Playlist not found: %s", name)
            raise SpotKitResourceNotFoundError("Playlist", name)
        except SpotKitResourceNotFoundError:
            # raise
            return None
        except (SpotKitAPIError, SpotKitAuthError):
            raise
        except Exception as e:
            LOG.error("Unexpected error finding playlist: %s", e)
            raise SpotKitAPIError("Failed to find playlist", details=str(e))

    def create_playlist(self, name: str, public: bool = False):
        LOG.info("Creating playlist: %s", name)

        try:
            user = self._retry(self._client.current_user)
            user_id = user.get("id")

            playlist = self._retry(
                self._client.user_playlist_create, user_id, name, public=public
            )
            LOG.info("Created playlist %s (ID: %s)", playlist["name"], playlist["id"])
            return playlist
        except (SpotKitAPIError, SpotKitAuthError):
            raise
        except Exception as e:
            LOG.error("Unexpected error creating playlist: %s", e)
            raise SpotKitAPIError("Failed to create playlist", details=str(e))

    def add_tracks_to_playlist(self, playlist_id: str, track_uris):
        LOG.info("Adding %d tracks to playlist %s", len(track_uris), playlist_id)

        try:
            # Spotify limit = 100 URIs per request
            batches = [track_uris[i : i + 100] for i in range(0, len(track_uris), 100)]

            with Progress() as progress:
                task = progress.add_task("Adding tracks...", total=len(batches))

                for batch in batches:
                    self._retry(self._client.playlist_add_items, playlist_id, batch)
                    progress.update(task, advance=1)

            LOG.info("Successfully added tracks to playlist %s", playlist_id)
        except (SpotKitAPIError, SpotKitAuthError):
            raise
        except Exception as e:
            LOG.error("Unexpected error adding tracks: %s", e)
            raise SpotKitAPIError("Failed to add tracks to playlist", details=str(e))

    def get_playlist_tracks(self, playlist_id: str):
        LOG.info("Fetching tracks of playlist %s", playlist_id)

        tracks = []
        limit = 100
        offset = 0

        try:
            with Progress() as progress:
                task = progress.add_task("Fetching playlist tracks...", total=None)

                while True:
                    result = self._retry(
                        self._client.playlist_items,
                        playlist_id,
                        limit=limit,
                        offset=offset,
                    )
                    items = result.get("items", [])
                    if not items or not result.get("next"):
                        if items:
                            for item in items:
                                t = item.get("track") or {}
                                if t.get("uri"):  # Skip null tracks
                                    tracks.append(
                                        {
                                            "uri": t.get("uri"),
                                            "name": t.get("name"),
                                            "artists": [
                                                a.get("name")
                                                for a in t.get("artists", [])
                                            ]
                                            if t.get("artists")
                                            else [],
                                            "album": t.get("album", {}).get("name")
                                            if t.get("album")
                                            else None,
                                            "duration_ms": t.get("duration_ms"),
                                        }
                                    )
                        break

                    for item in items:
                        t = item.get("track") or {}
                        if t.get("uri"):  # Skip null tracks
                            tracks.append(
                                {
                                    "uri": t.get("uri"),
                                    "name": t.get("name"),
                                    "artists": [
                                        a.get("name") for a in t.get("artists", [])
                                    ]
                                    if t.get("artists")
                                    else [],
                                    "album": t.get("album", {}).get("name")
                                    if t.get("album")
                                    else None,
                                    "duration_ms": t.get("duration_ms"),
                                }
                            )

                    offset += limit
                    progress.update(task, advance=1)

            LOG.info("Total playlist tracks: %d", len(tracks))
            return tracks
        except (SpotKitAPIError, SpotKitAuthError):
            raise
        except Exception as e:
            LOG.error("Unexpected error fetching playlist tracks: %s", e)
            raise SpotKitAPIError("Failed to fetch playlist tracks", details=str(e))
