import csv
from datetime import datetime
import json


class PlaylistExporter:
    def __init__(self, metadata_storage):
        self.storage = metadata_storage

    def prepare_data(self, playlist_tracks, order_by="playlist"):
        data = []

        for track in playlist_tracks:
            with self.storage as storage:
                metadata = storage.get_track_metadata(track["uri"])

                data.append(
                    {
                        "track_name": track["name"],
                        "artist_name": ", ".join(track["artists"]),
                        "album_name": track["album"],
                        "duration": format_duration(track["duration_ms"]),
                        "uri": track["uri"],
                        "rating": metadata["user_rating"] if metadata else None,
                        "comment": metadata["user_comment"] if metadata else "",
                        "exported_at": datetime.utcnow().isoformat(),
                    }
                )

        if order_by == "playlist":
            return data

        elif order_by == "rating":
            data.sort(key=lambda x: (x["rating"] is None, -(x["rating"] or 0)))

        elif order_by == "name":
            data.sort(key=lambda x: x["track_name"].lower())

        return data

    def export_csv(self, data, output_path):
        fieldnames = [
            "track_name",
            "artist_name",
            "album_name",
            "duration",
            "uri",
            "rating",
            "comment",
            "exported_at",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

            return output_path

    def export_json(self, data, output_path):
        # TODO: JSON structure: {playlist_name, export_date, track_count, tracks: [...]}
        #   - data = prepare_data() -> need 'playlist_name'

        with open(output_path, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=2)

            return output_path

    def export_markdown(self, data, output_path):
        # TODO: Markdown structure: metadata (playlist name, date, total tracks) + format table
        #   - data = prepare_data() -> need 'playlist_name'

        with open(output_path, "w", encoding="utf-8") as mdfile:
            mdfile.write(f"# Playlist: {data['playlist_name']}\n\n")

            mdfile.write(f"**Exported At:** {datetime.utcnow().isoformat()}\n\n")
            mdfile.write(f"**Total Tracks:** {len(data)}\n\n")
            mdfile.write(
                f"**Playlist URL:** [{data['playlist_url']}]({data['playlist_url']})\n\n"
            )

            mdfile.write("## Tracks\n\n")

            mdfile.write(
                "| Track Name | Artist Name | Album Name | Duration | URI | Rating | Comment |\n"
            )
            mdfile.write(
                "|------------|-------------|------------|----------|-----|--------|---------|\n"
            )
            for row in data["tracks"]:
                mdfile.write(
                    f"| {row['track_name']} | {row['artist_name']} | {row['album_name']} | {row['duration']} | [Spotify]({row['uri']}) | {'⭐' * (row['rating'] or 0) or ''} | {row['comment']} |\n"
                )

            return output_path


def format_duration(ms):
    seconds = ms // 1000
    return f"{seconds // 60}:{seconds % 60:02d}"
