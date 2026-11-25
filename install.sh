#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
extension_uuid=screenshot-save@theayushlab.github.io
extension_dir="$HOME/.local/share/gnome-shell/extensions/$extension_uuid"

install -d "$HOME/.local/share/screenshot-preview" "$extension_dir" \
    "$HOME/.config/systemd/user"
install -m 0644 "$project_dir/preview.py" \
    "$HOME/.local/share/screenshot-preview/preview.py"
install -m 0644 "$project_dir/shell-extension/metadata.json" \
    "$project_dir/shell-extension/extension.js" "$extension_dir/"
install -m 0644 "$project_dir/screenshot-preview.service" \
    "$HOME/.config/systemd/user/screenshot-preview.service"

/usr/bin/python3 - <<'PY'
from gi.repository import Gio

settings = Gio.Settings.new("org.gnome.shell")
extension_uuid = "screenshot-save@theayushlab.github.io"
enabled = settings.get_strv("enabled-extensions")
disabled = settings.get_strv("disabled-extensions")

if extension_uuid not in enabled:
    settings.set_strv("enabled-extensions", [*enabled, extension_uuid])
if extension_uuid in disabled:
    settings.set_strv("disabled-extensions", [
        item for item in disabled if item != extension_uuid
    ])

Gio.Settings.sync()
PY

systemctl --user daemon-reload
systemctl --user enable --now screenshot-preview.service

printf '%s\n' 'Installation complete. Sign out and back in to load the GNOME shortcut.'
