video_downloader_package_sources = files([
  '__init__.py',
  '__main__.py',
  'about_dialog.py',
  'authentication_dialog.py',
  'main.py',
  'model.py',
  'playlist_dialog.py',
  'shortcuts_dialog.py',
  'window.py',
])
python_sources_for_linting += video_downloader_package_sources
install_data(video_downloader_package_sources, install_dir: moduledir)

app_sources = files([
  'app/__init__.py',
  'app/application.py',
  'app/model.py',
])
python_sources_for_linting += app_sources
install_data(app_sources, install_dir: moduledir / 'app')

ui_sources = files([
  'ui/__init__.py',
  'ui/about.py',
  'ui/authentication.py',
  'ui/download_page.py',
  'ui/playlist.py',
  'ui/shortcuts.py',
  'ui/window.py',
])
python_sources_for_linting += ui_sources
install_data(ui_sources, install_dir: moduledir / 'ui')

subdir('downloader')
subdir('util')
