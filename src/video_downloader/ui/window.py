"""Main application window hosting multiple download tabs."""

import gettext

from gi.repository import Adw, GLib, Gtk

from video_downloader.ui import ShortcutsDialog, build_about_dialog
from video_downloader.ui.download_page import DownloadPage
from video_downloader.util import gobject_log
from video_downloader.util.connection import CloseStack, SignalConnection, create_action

N_ = gettext.gettext


@Gtk.Template(resource_path="/com/github/unrud/VideoDownloader/window.ui")
class Window(Adw.ApplicationWindow):
    __gtype_name__ = "VideoDownloaderWindow"

    tab_view_wdg = Gtk.Template.Child()
    tab_bar_wdg = Gtk.Template.Child()
    new_tab_button_wdg = Gtk.Template.Child()

    def __init__(self, application):
        super().__init__(application=application)
        self.application = application
        self._cs = CloseStack()
        self.window_group = gobject_log(Gtk.WindowGroup())
        self.window_group.add_window(self)
        self._sessions = {}

        create_action(self, self._cs, "close", self.destroy, no_args=True)
        create_action(self, self._cs, "about", self._show_about_dialog, no_args=True)
        create_action(
            self, self._cs, "shortcuts", self._show_shortcuts_dialog, no_args=True
        )
        create_action(
            self,
            self._cs,
            "change-download-folder",
            self._change_download_folder,
            no_args=True,
        )
        create_action(self, self._cs, "new-tab", self._create_session, no_args=True)

        self._cs.push(
            SignalConnection(self.tab_view_wdg, "close-page", self._on_close_page)
        )
        self._cs.push(
            SignalConnection(
                self.tab_view_wdg,
                "notify::selected-page",
                lambda *_: self._on_selected_page_changed(),
                no_args=True,
            )
        )

        self._create_session()

    def _create_session(self, *_):
        page = gobject_log(DownloadPage(self.application, self, self.window_group))
        tab_page = self.tab_view_wdg.append(page)
        tab_page.set_title(N_("Download"))
        tab_page.set_icon_name("download-symbolic")
        page.bind_tab_page(tab_page)
        self._sessions[page] = tab_page
        self.tab_view_wdg.set_selected_page(tab_page)
        page.on_selected()

    def _on_selected_page_changed(self):
        page = self._get_current_page()
        if page is not None:
            page.on_selected()

    def _get_current_page(self):
        tab_page = self.tab_view_wdg.get_selected_page()
        if tab_page is None:
            return None
        return tab_page.get_child()

    def _change_download_folder(self):
        page = self._get_current_page()
        if page is not None:
            page.change_download_folder()

    def _on_close_page(self, tab_view, tab_page):
        page = tab_page.get_child()
        tab_view.close_page_finish(tab_page, True)
        if page in self._sessions:
            del self._sessions[page]
        page.destroy()
        if self.tab_view_wdg.get_n_pages() == 0:
            GLib.idle_add(self._create_session)

    def _show_shortcuts_dialog(self):
        dialog = gobject_log(ShortcutsDialog(self))
        self.window_group.add_window(dialog)
        dialog.show()

    def _show_about_dialog(self):
        dialog = gobject_log(build_about_dialog(self))
        self.window_group.add_window(dialog)
        dialog.show()

    def destroy(self):
        for page in list(self._sessions.keys()):
            page.destroy()
        self._sessions.clear()
        self._cs.close()
        super().destroy()
