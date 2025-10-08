# Architecture overview

The Video Downloader code base is organised into a set of small, purpose driven
packages. The goal of the refactor is to make it easier to navigate the source
code, reason about the interactions between components and provide stable import
paths for third-party integrations.

## Package layout

- `video_downloader.app`
  - Hosts the GTK `Application` subclass and the persistent `Model` used by the
    UI. The module also exposes `run()` and `build_application()` helpers which
    are consumed by the CLI launcher as well as tests.
- `video_downloader.ui`
  - Contains widgets, dialogs and the main window implementation. The UI layer
    only depends on the abstractions exposed by `video_downloader.app` and the
    utilities package.
- `video_downloader.downloader`
  - Implements the RPC protocol used to communicate with the background
    `yt-dlp` process. The module is intentionally decoupled from the rest of the
    application to ensure we can reason about process management in isolation.
- `video_downloader.util`
  - A collection of shared helpers ranging from GObject connection management to
    filesystem utilities.

Legacy module names such as `video_downloader.window` are implemented as thin
wrappers over the new locations. This keeps existing integrations functional
while giving the project a coherent internal layout.

## Entry points

- `python -m video_downloader`
  - Launches the GTK application through `video_downloader.app.run()`.
- `video_downloader.app.run(argv=None)`
  - Primary programmatic entry point. Accepts an optional list of arguments to
    simplify automated tests.
- `video_downloader.app.build_application()`
  - Helper used by tests to instantiate the GTK application without starting the
    main loop.

## Testing hooks

The refactor introduces a `tests/` folder where new unit tests can exercise
utility functions and the legacy import compatibility layer. Tests can be
executed with `python -m pytest` or `python -m unittest discover` once the
required dependencies are installed.
