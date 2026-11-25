#!/usr/bin/python3
import re
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk


class ScreenshotSaveDialog(Gtk.FileChooserDialog):
    def __init__(self, application, screenshot, png, startup_id):
        super().__init__(application=application, title="Save Screenshot", modal=True,
                         action=Gtk.FileChooserAction.SAVE)
        self.screenshot = screenshot
        self.png = png
        self.saving = False

        if startup_id:
            self.set_startup_id(startup_id)
        self.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        save = self.add_button("_Save", Gtk.ResponseType.ACCEPT)
        save.add_css_class("suggested-action")
        self.set_default_response(Gtk.ResponseType.ACCEPT)
        self.set_current_folder(screenshot.get_parent().get_parent())
        self.set_current_name(screenshot.get_basename())
        self.connect("response", self._respond)

    def _respond(self, _dialog, response):
        if self.saving:
            return
        if response != Gtk.ResponseType.ACCEPT:
            self.destroy()
            return

        destination = self.get_file()
        if destination is None:
            return
        self.saving = True
        self.set_sensitive(False)
        destination.replace_contents_bytes_async(
            self.png, None, False, Gio.FileCreateFlags.REPLACE_DESTINATION,
            None, self._write_finished,
        )

    def _write_finished(self, destination, result):
        try:
            destination.replace_contents_finish(result)
        except GLib.Error as error:
            self.saving = False
            self.set_sensitive(True)
            Gtk.AlertDialog(message="Couldn’t save the screenshot", detail=error.message).show(self)
        else:
            self.destroy()


class ScreenshotSaver(Gtk.Application):
    def __init__(self, directory):
        super().__init__(application_id="io.github.theayushlab.ScreenshotPreview",
                         flags=Gio.ApplicationFlags.IS_SERVICE)
        self.screenshot_folder = Gio.File.new_for_path(str(directory))
        filename = GLib.dgettext("gnome-shell", "Screenshot From %s")
        date_time = r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}-[0-9]{2}-[0-9]{2}"
        name = re.escape(filename).replace("%s", date_time)
        self.screenshot_name = re.compile(rf"{name}(?:-[0-9]+)?\.png")

    def do_startup(self):
        Gtk.Application.do_startup(self)
        save_capture = Gio.SimpleAction.new("save-capture", GLib.VariantType.new("(ss)"))
        save_capture.connect("activate", self._save_capture)
        self.add_action(save_capture)
        self.hold()

    def _save_capture(self, _action, parameter):
        uri, startup_id = parameter.unpack()
        screenshot = Gio.File.new_for_uri(uri)
        parent = screenshot.get_parent()
        if (parent is None or not parent.equal(self.screenshot_folder)
                or not self.screenshot_name.fullmatch(screenshot.get_basename())):
            return

        for dialog in self.get_windows():
            if dialog.screenshot.equal(screenshot):
                if startup_id:
                    dialog.set_startup_id(startup_id)
                dialog.present()
                return

        try:
            png, _etag = screenshot.load_bytes(None)
        except GLib.Error as error:
            print(f"Couldn’t open screenshot: {error.message}", file=sys.stderr)
            return

        ScreenshotSaveDialog(self, screenshot, png, startup_id).present()


def main():
    pictures = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
    directory = Path(pictures or GLib.get_home_dir()) / GLib.dgettext("gnome-shell", "Screenshots")
    application = ScreenshotSaver(directory)
    return application.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
