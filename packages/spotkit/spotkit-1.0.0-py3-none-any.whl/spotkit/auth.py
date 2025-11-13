from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler
from spotipy.exceptions import SpotifyException

from spotkit.config import CONFIG_DIR, load_config
from spotkit.logger import get_logger
from spotkit.exceptions import SpotKitAuthError, SpotKitConfigError

LOG = get_logger(__name__)

DEFAULT_SCOPES = [
    "playlist-modify-public",
    "playlist-modify-private",
    "playlist-read-private",
    "user-library-read",
]

TOKEN_PATH = CONFIG_DIR / "token.json"


def _get_auth(scopes=None):
    scopes = scopes or DEFAULT_SCOPES

    try:
        config = load_config()
    except Exception as e:
        LOG.error("Failed to load config: %s", e)
        raise SpotKitConfigError(details=str(e))

    client_id = config.get("spotify_client_id")
    if not client_id:
        LOG.error("Missing spotify_client_id in config")
        raise SpotKitConfigError("spotify_client_id")

    client_secret = config.get("spotify_client_secret")
    if not client_secret:
        LOG.error("Missing spotify_client_secret in config")
        raise SpotKitConfigError("spotify_client_secret")

    redirect_uri = config.get("spotify_redirect_uri")
    if not redirect_uri:
        LOG.error("Missing spotify_redirect_uri in config")
        raise SpotKitConfigError("spotify_redirect_uri")

    try:
        return SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scopes,
            cache_handler=CacheFileHandler(cache_path=TOKEN_PATH),
            open_browser=True,
            show_dialog=True,
        )
    except Exception as e:
        LOG.error("Failed to create SpotifyOAuth: %s", e)
        raise SpotKitAuthError("Failed to initialize OAuth", details=str(e))


def authenticate():
    LOG.info("Starting OAuth flow with Spotify")

    try:
        auth = _get_auth()
        token = auth.get_access_token(as_dict=True)

        if not token or "access_token" not in token:
            LOG.error("OAuth flow completed but no valid token received")
            raise SpotKitAuthError(
                "Token acquisition failed",
                details="OAuth flow completed but no access token returned",
            )

        LOG.info("Token obtained and saved in %s", TOKEN_PATH)
        return token

    except SpotifyException as e:
        LOG.error("Spotify OAuth error: %s", e)
        raise SpotKitAuthError("Spotify authentication failed", details=str(e))
    except SpotKitAuthError:
        raise
    except Exception as e:
        LOG.error("Unexpected error during authentication: %s", e)
        raise SpotKitAuthError("Unexpected authentication error", details=str(e))


def get_authenticated_client():
    try:
        auth = _get_auth()
        token = auth.get_access_token(as_dict=True)

        if not token or "access_token" not in token:
            LOG.error("Failed to obtain valid token")
            raise SpotKitAuthError("No valid token available")

        LOG.info("Token loaded/renewed - client ready")
        return Spotify(auth_manager=auth)

    except SpotifyException as e:
        LOG.error("Failed to create authenticated client: %s", e)
        raise SpotKitAuthError("Failed to create Spotify client", details=str(e))
    except SpotKitAuthError:
        raise
    except Exception as e:
        LOG.error("Unexpected error creating client: %s", e)
        raise SpotKitAuthError("Unexpected client creation error", details=str(e))
