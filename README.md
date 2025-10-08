# Video Downloader

[![Translation status](https://hosted.weblate.org/widgets/video-downloader/-/gui/svg-badge.svg)](https://hosted.weblate.org/engage/video-downloader/)

Download videos from websites with an easy-to-use interface.
Provides the following features:

  * Convert videos to MP3
  * Supports password-protected and private videos
  * Download single videos or whole playlists
  * Automatically selects a video format based on your quality demands

Based on [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Quick start

### Running from source

Video Downloader can be executed directly from a source checkout without a
system-wide installation. Ensure you have a Python 3 environment with
``gi``/PyGObject available and run:

```bash
meson setup builddir
ninja -C builddir run
```

Alternatively you can launch the application module directly which respects the
same command-line options as the installed binary:

```bash
python -m video_downloader --url "https://example.org/video"
```

### Repository layout

The repository now follows a layered structure which aligns with the
responsibilities of each component:

| Path | Description |
| ---- | ----------- |
| ``src/video_downloader/app`` | High-level application orchestration (GTK application, domain model). |
| ``src/video_downloader/ui`` | Widgets, dialogs and window templates. |
| ``src/video_downloader/downloader`` | Process supervisor and RPC glue to ``yt-dlp``. |
| ``src/video_downloader/util`` | Shared helpers used across layers. |
| ``docs`` | Developer documentation and architecture notes. |

Legacy module paths such as ``video_downloader.window`` remain available for
third-party integrations via lightweight compatibility shims.

## Installation

<a href='https://flathub.org/apps/details/com.github.unrud.VideoDownloader'><img width='240' alt='Download on Flathub' src='https://flathub.org/assets/badges/flathub-badge-en.png'/></a>

### Alternative installation methods

  * [Snap Store](https://snapcraft.io/video-downloader)
  * [Fedora](https://src.fedoraproject.org/rpms/video-downloader): `sudo dnf install video-downloader`
  * [Arch User Repository](https://aur.archlinux.org/packages/video-downloader)

## Translation

We use [Weblate](https://hosted.weblate.org/engage/video-downloader/) to translate the UI, so feel free to contribute translations over there.

## Screenshots

![screenshot 1](https://raw.githubusercontent.com/Unrud/video-downloader/master/screenshots/1.png)

![screenshot 2](https://raw.githubusercontent.com/Unrud/video-downloader/master/screenshots/2.png)

![screenshot 3](https://raw.githubusercontent.com/Unrud/video-downloader/master/screenshots/3.png)

## Hidden configuration options

The behavior of the program can be tweaked with GSettings.

### Automatic Subtitles

List of additional automatic subtitles to download. The entry `all` matches all languages.

The default is `[]`.

#### Flatpak

```
flatpak run --command=gsettings com.github.unrud.VideoDownloader set com.github.unrud.VideoDownloader automatic-subtitles "['de','en']"
```

#### Snap

```
snap run --shell video-downloader -c 'gsettings "$@"' '' set com.github.unrud.VideoDownloader automatic-subtitles "['de','en']"
```

## Debug

To display messages from **yt-dlp** run program with the environment variable `G_MESSAGES_DEBUG=yt-dlp`.

To display information about GOBject references, start the program with the environment variable `G_MESSAGES_DEBUG=gobject-ref`.

## Development

We recommend using a virtual environment for Python tooling:

```bash
python -m venv .venv
. .venv/bin/activate
pip install meson ninja flake8
```

Useful commands during development:

* ``meson compile -C builddir`` – build the project and compile resources.
* ``ninja -C builddir test`` – run the integration and translation checks.
* ``python -m compileall src/video_downloader`` – quick syntax validation of the Python sources.

For more details see ``docs/ARCHITECTURE.md``.
