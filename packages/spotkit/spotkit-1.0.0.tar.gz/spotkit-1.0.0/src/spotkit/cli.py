import logging
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional
from typing_extensions import Annotated
from typer import Argument, Exit, Option, Typer, confirm
from rich.console import Console
from rich.table import Table

from spotkit import __version__
from spotkit.config import load_config
from spotkit.exporter import PlaylistExporter
from spotkit.logger import get_logger, console_handler
from spotkit.spotify_client import SpotifyClient
from spotkit.storage import MetadataStorage
from spotkit.exceptions import (
    SpotKitError,
    SpotKitAuthError,
    SpotKitAPIError,
    SpotKitConfigError,
    SpotKitStorageError,
    SpotKitValidationError,
    SpotKitResourceNotFoundError,
)

app = Typer(help="SpotKit – CLI toolbox for Spotify")
console = Console()

# Exit codes
EXIT_SUCCESS = 0
EXIT_AUTH_ERROR = 1
EXIT_API_ERROR = 2
EXIT_CONFIG_ERROR = 3
EXIT_STORAGE_ERROR = 4
EXIT_VALIDATION_ERROR = 5
EXIT_NOT_FOUND = 6
EXIT_UNEXPECTED = 99


def handle_error(e: Exception) -> int:
    """Centralizado error handling com exit codes apropriados."""
    if isinstance(e, SpotKitAuthError):
        console.print(f"[bold red]Authentication Error:[/bold red] {e}", style="red")
        return EXIT_AUTH_ERROR
    elif isinstance(e, SpotKitAPIError):
        console.print(f"[bold red]API Error:[/bold red] {e}", style="red")
        return EXIT_API_ERROR
    elif isinstance(e, SpotKitConfigError):
        console.print(f"[bold red]Configuration Error:[/bold red] {e}", style="red")
        return EXIT_CONFIG_ERROR
    elif isinstance(e, SpotKitStorageError):
        console.print(f"[bold red]Storage Error:[/bold red] {e}", style="red")
        return EXIT_STORAGE_ERROR
    elif isinstance(e, SpotKitValidationError):
        console.print(f"[bold red]Validation Error:[/bold red] {e}", style="red")
        return EXIT_VALIDATION_ERROR
    elif isinstance(e, SpotKitResourceNotFoundError):
        console.print(f"[bold yellow]Not Found:[/bold yellow] {e}", style="yellow")
        return EXIT_NOT_FOUND
    elif isinstance(e, SpotKitError):
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        return EXIT_UNEXPECTED
    else:
        console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}", style="red")
        console.print(
            "\n[dim]This is a bug. Please report it with the log file from ~/.spotkit/spotkit.log[/dim]"
        )
        return EXIT_UNEXPECTED


def version_callback(value: bool):
    if value:
        console.print(f"SpotKit CLI Version: {__version__}")
        raise Exit()


def verbose_callback(value: bool):
    if value:
        console_handler.setLevel(logging.DEBUG)
        return


def quiet_callback(value: bool):
    if value:
        console_handler.setLevel(logging.ERROR)
        return


@app.callback()
def main(
    version: Annotated[
        Optional[bool], Option("--version", callback=version_callback)
    ] = None,
    verbose: Annotated[
        Optional[bool], Option("--verbose", callback=verbose_callback)
    ] = None,
    quiet: Annotated[Optional[bool], Option("--quiet", callback=quiet_callback)] = None,
):
    pass


# === AUTH ===

LOG_AUTH = get_logger("AuthCommand")


@app.command(name="auth", help="Authenticate with Spotify")
def login():
    LOG_AUTH.info("Starting Spotify authentication process")
    console.print("🔐 Starting Spotify authentication...")

    try:
        SpotifyClient()
        LOG_AUTH.info("Spotify authentication successful")
        console.print("[green]✓[/green] Authentication successful!", style="bold green")
    except Exception as e:
        LOG_AUTH.error("Authentication failed: %s", e)
        sys.exit(handle_error(e))


# === ADD ARTIST ===

LOG_ADD_ARTIST = get_logger("AddArtistCommand")


@app.command(name="add-artist", help="Add an artist to your Spotify library")
def add_artist(
    artist_name: str = Option(..., help="Name of the artist to add"),
    playlist: str = Option(
        ..., help="Name of the playlist to add the artist's tracks to"
    ),
    create: bool = Option(False, help="Create the playlist if it doesn't exist"),
):
    LOG_ADD_ARTIST.info("Adding artist '%s' to Spotify library", artist_name)
    console.print(
        f"🎵 Adding artist '[cyan]{artist_name}[/cyan]' to your Spotify library..."
    )

    try:
        client = SpotifyClient()
        artist = client.search_artist(artist_name)
        LOG_ADD_ARTIST.info(
            "Artist '%s' found: %s (ID: %s)", artist_name, artist["name"], artist["id"]
        )

        tracks = client.get_all_tracks(artist["id"])
        LOG_ADD_ARTIST.info("Found %d tracks for artist '%s'", len(tracks), artist_name)

        if not confirm(
            f"Add {len(tracks)} tracks by '{artist_name}' to playlist '{playlist}'?",
            default=True,
        ):
            console.print("[yellow]Cancelled[/yellow]")
            raise Exit()

        if create:
            playlist_info = client.create_playlist(playlist, False)
            LOG_ADD_ARTIST.info(
                "Playlist '%s' created (ID: %s)", playlist, playlist_info["id"]
            )
            console.print(
                f"[green]✓[/green] Playlist '[cyan]{playlist}[/cyan]' created!"
            )
        else:
            playlist_info = client.get_playlist_by_name(playlist)
            LOG_ADD_ARTIST.info(
                "Using playlist '%s' (ID: %s)", playlist, playlist_info["id"]
            )

        client.add_tracks_to_playlist(
            playlist_info["id"], [track["uri"] for track in tracks]
        )
        LOG_ADD_ARTIST.info("Artist '%s' added successfully", artist_name)
        console.print(
            f"[green]✓[/green] Artist '[cyan]{artist_name}[/cyan]' added successfully!",
            style="bold green",
        )

    except Exception as e:
        LOG_ADD_ARTIST.error("Failed to add artist: %s", e)
        sys.exit(handle_error(e))


# === LIST PLAYLISTS ===

LOG_LIST_PLAYLISTS = get_logger("ListPlaylistsCommand")


@app.command(name="list-playlists", help="List all your Spotify playlists")
def list_playlists(
    public: bool = Option(False, help="List only public playlists"),
    private: bool = Option(False, help="List only private playlists"),
):
    LOG_LIST_PLAYLISTS.info("Listing all Spotify playlists")
    console.print("📋 Fetching your Spotify playlists...")

    try:
        client = SpotifyClient()
        playlists = client.list_user_playlists()
        LOG_LIST_PLAYLISTS.info("Found %d playlists", len(playlists))

        table = Table(title="Your Spotify Playlists")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Total Tracks", style="green")
        table.add_column("Owner", style="yellow")
        table.add_column("Public/Private", style="red")
        table.add_column("ID", style="magenta")

        filtered_count = 0
        for playlist in playlists:
            if public and not playlist["public"]:
                continue
            if private and playlist["public"]:
                continue

            table.add_row(
                playlist["name"],
                str(playlist["tracks"]["total"]),
                playlist["owner"]["display_name"],
                "Public" if playlist["public"] else "Private",
                playlist["id"],
            )
            filtered_count += 1

        console.print(table)
        console.print(
            f"\n[dim]Showing {filtered_count} of {len(playlists)} playlists[/dim]"
        )

    except Exception as e:
        LOG_LIST_PLAYLISTS.error("Failed to list playlists: %s", e)
        sys.exit(handle_error(e))


# === LIST TRACKS ===

LOG_LIST_TRACKS = get_logger("ListTracksCommand")


@app.command(name="list-tracks", help="List tracks in a Spotify playlist")
def list_tracks(
    playlist: Annotated[
        str, Argument(..., help="Name of the playlist to list tracks from")
    ],
):
    LOG_LIST_TRACKS.info("Listing tracks from playlist '%s'", playlist)
    console.print(f"🎶 Fetching tracks from playlist '[cyan]{playlist}[/cyan]'...")

    try:
        client = SpotifyClient()
        playlist_info = client.get_playlist_by_name(playlist)
        tracks = client.get_playlist_tracks(playlist_info["id"])
        LOG_LIST_TRACKS.info("Found %d tracks in playlist '%s'", len(tracks), playlist)

        for idx, track in enumerate(tracks, start=1):
            console.print(
                f"{idx}. [cyan]{track['name']}[/cyan] by [yellow]{', '.join(track['artists'])}[/yellow]"
            )

        console.print(f"\n[dim]Total: {len(tracks)} tracks[/dim]")

    except Exception as e:
        LOG_LIST_TRACKS.error("Failed to list tracks: %s", e)
        sys.exit(handle_error(e))


# === COMMENT & RATE ===

LOG_COMMENT = get_logger("CommentCommand")


@app.command(name="comment", help="Add a comment to a Spotify track")
def comment(
    track_uri: Annotated[str, Argument(..., help="Spotify track URI")],
    show: bool = Option(False, help="Show current comment without editing"),
):
    try:
        # Initialize DB if needed
        db = MetadataStorage()
        db.init_db()

        with db as conn:
            track = conn.get_track_metadata(track_uri)
            if not track:
                client = SpotifyClient()
                track_data = client._client.track(track_uri)
                if not track_data:
                    console.print(
                        "[red]Track not found on Spotify. Check the URI.[/red]"
                    )
                    raise Exit(EXIT_NOT_FOUND)

                conn.upsert_track_metadata(
                    track_uri,
                    track_data["name"],
                    ", ".join(artist["name"] for artist in track_data["artists"]),
                )
                track = conn.get_track_metadata(track_uri)

            if show:
                current = track.get("user_comment") or "[dim]No comment[/dim]"
                console.print(
                    f"Comment for [cyan]{track['track_name']}[/cyan]: {current}"
                )
                raise Exit()

            console.print(f"Enter comment for [cyan]{track['track_name']}[/cyan]:")
            comment_text = input(f"[{track.get('user_comment', '')}] > ").strip()

            if not comment_text and not track.get("user_comment"):
                console.print("[yellow]No comment provided[/yellow]")
                raise Exit()

            final_comment = comment_text if comment_text else track.get("user_comment")

            conn.set_comment(
                track_uri,
                final_comment,
                {"name": track["track_name"], "artist": track["artist_name"]},
            )

            console.print(
                f"[green]✓[/green] Comment updated for '[cyan]{track['track_name']}[/cyan]'"
            )

    except Exit:
        raise
    except Exception as e:
        LOG_COMMENT.error("Failed to set comment: %s", e)
        sys.exit(handle_error(e))


LOG_RATE = get_logger("RateCommand")


@app.command(name="rate", help="Rate a Spotify track")
def rate(
    tracks_uri: Annotated[List[str], Argument(..., help="Spotify track URI(s)")],
    rating: Annotated[int, Argument(..., help="Rating from 1 to 5")],
    show: bool = Option(False, help="Show current rating without editing"),
):
    try:
        if rating < 1 or rating > 5:
            raise SpotKitValidationError("rating", rating, "integer between 1 and 5")

        # Initialize DB if needed
        db = MetadataStorage()
        db.init_db()

        with db as conn:
            for track_uri in tracks_uri:
                track = conn.get_track_metadata(track_uri)
                if not track:
                    client = SpotifyClient()
                    track_data = client._client.track(track_uri)
                    if not track_data:
                        console.print(
                            f"[red]Track {track_uri} not found on Spotify[/red]"
                        )
                        continue

                    conn.upsert_track_metadata(
                        track_uri,
                        track_data["name"],
                        ", ".join(artist["name"] for artist in track_data["artists"]),
                    )
                    track = conn.get_track_metadata(track_uri)

                if show:
                    current = track.get("user_rating") or "[dim]Not rated[/dim]"
                    console.print(
                        f"Rating for [cyan]{track['track_name']}[/cyan]: {current}"
                    )
                    continue

                conn.set_rating(
                    track_uri,
                    rating,
                    {"name": track["track_name"], "artist": track["artist_name"]},
                )

                stars = "⭐" * rating
                console.print(
                    f"[green]✓[/green] '[cyan]{track['track_name']}[/cyan]' rated {stars}"
                )

    except Exit:
        raise
    except Exception as e:
        LOG_RATE.error("Failed to set rating: %s", e)
        sys.exit(handle_error(e))


# === EXPORT ===

LOG_EXPORT = get_logger("ExportCommand")


class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    MARKDOWN = "md"


@app.command(name="export", help="Export playlist with metadata")
def export(
    playlist_id: Annotated[str, Argument(..., help="Spotify playlist ID")],
    format: ExportFormat = ExportFormat.CSV,
    output: Annotated[Path, Option(help="Output file path")] = Path(),
):
    LOG_EXPORT.info("Exporting playlist %s to %s", playlist_id, format)
    console.print(f"📤 Exporting playlist to [cyan]{format.value.upper()}[/cyan]...")

    try:
        # Initialize DB if needed
        db = MetadataStorage()
        db.init_db()

        client = SpotifyClient()
        pe = PlaylistExporter(db)

        playlist_tracks = client.get_playlist_tracks(playlist_id)
        playlist_data = pe.prepare_data(playlist_tracks)

        if output.is_dir():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = output / f"playlist_export_{timestamp}.{format.value}"
        else:
            format = ExportFormat(output.suffix.lstrip("."))

        if format == ExportFormat.CSV:
            pe.export_csv(playlist_data, output)
        elif format == ExportFormat.JSON:
            pe.export_json(playlist_data, output)
        elif format == ExportFormat.MARKDOWN:
            pe.export_markdown(playlist_data, output)

        console.print(f"[green]✓[/green] Exported to [cyan]{output}[/cyan]")
        LOG_EXPORT.info("Export completed: %s", output)

    except Exception as e:
        LOG_EXPORT.error("Failed to export: %s", e)
        sys.exit(handle_error(e))


# === CONFIG ===

LOG_CONFIG = get_logger("ConfigCommand")


@app.command("config", help="Manage the config")
def config(
    show: bool = Option(False, help="Show current config"),
    reset: bool = Option(False, help="Reset to default configuration"),
):
    try:
        config = load_config()
    except Exception as e:
        LOG_CONFIG.error("Failed to load config: %s", e)
        sys.exit(handle_error(e))

    if show:
        console.print("Current config:\n")
        for key, value in config.data.items():
            console.print(f"[cyan]{key}[/cyan]: {value}")

        raise Exit()

    if reset:
        console.print("Reseting config...")
        for key in config.data.keys():
            LOG_CONFIG.info("Reseting {key}...")
            try:
                config.set(key, "")
            except Exception as e:
                LOG_CONFIG.error(f"Failed to reset {key} in config: %s", e)
                sys.exit(handle_error(e))

        LOG_CONFIG.info("Reset config completed")
        console.print("[green]✓[/green] Config reseted")
        raise Exit()

    console.print("To show current config use --show")
    console.print("To reset current config use --reset")


# ===  SEARCH ===

LOG_SEARCH = get_logger("SearchCommand")


@app.command("search", help="Search for tracks, artist or album")
def search(query: Annotated[str, Argument(..., help="Query parameter to search")]):
    try:
        client = SpotifyClient()

        artist = client.search_artist(query)

        console.print(artist)
    except Exception as e:
        LOG_SEARCH.error(f"Failed to search for {query}: %s", e)
        sys.exit(handle_error(e))
