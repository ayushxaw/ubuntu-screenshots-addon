#!/bin/sh
set -eu

extension_uuid=screenshot-save@theayushlab.github.io

systemctl --user disable --now screenshot-preview.service || true

/usr/bin/python3 - <<'PY'
from gi.repository import Gio

settings = Gio.Settings.new("org.gnome.shell")
extension_uuid = "screenshot-save@theayushlab.github.io"

for key in ("enabled-extensions", "disabled-extensions"):
    extensions = settings.get_strv(key)
    updated = [item for item in extensions if item != extension_uuid]
    if updated != extensions:
        settings.set_strv(key, updated)

Gio.Settings.sync()
PY

rm -f "$HOME/.config/systemd/user/screenshot-preview.service"
rm -f "$HOME/.local/share/screenshot-preview/preview.py"
rm -f "$HOME/.local/share/gnome-shell/extensions/$extension_uuid/extension.js"
rm -f "$HOME/.local/share/gnome-shell/extensions/$extension_uuid/metadata.json"
rmdir "$HOME/.local/share/screenshot-preview" \
    "$HOME/.local/share/gnome-shell/extensions/$extension_uuid" 2>/dev/null || true

systemctl --user daemon-reload
printf '%s\n' 'Uninstalled. Sign out and back in to remove the GNOME shortcut from this session.'
