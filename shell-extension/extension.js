import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

const SHORTCUT_MODIFIERS = Clutter.ModifierType.CONTROL_MASK |
    Clutter.ModifierType.SHIFT_MASK | Clutter.ModifierType.META_MASK |
    Clutter.ModifierType.SUPER_MASK | Clutter.ModifierType.MOD1_MASK;

export default class ScreenshotSave extends Extension {
    enable() {
        this._ui = Main.screenshotUI;
        this._handler = this._ui.connect('captured-event', (ui, event) => {
            if (event.type() !== Clutter.EventType.KEY_PRESS ||
                event.get_key_symbol() !== Clutter.KEY_s ||
                (event.get_state() & SHORTCUT_MODIFIERS) !== Clutter.ModifierType.CONTROL_MASK ||
                !ui._shotButton.checked || Main.sessionMode.isLocked || Main.sessionMode.isGreeter)
                return Clutter.EVENT_PROPAGATE;

            if (!this._saving)
                this._captureForSave(ui, event.get_time()).catch(error => console.error(error));
            return Clutter.EVENT_STOP;
        });
    }

    disable() {
        this._ui.disconnect(this._handler);
        this._ui = null;
    }

    async _captureForSave(ui, timestamp) {
        this._saving = true;
        let file;
        const id = ui.connect('screenshot-taken', (_ui, capture) => {
            file = capture;
        });
        try {
            await ui._onCaptureButtonClicked();
            if (file && this._ui === ui)
                this._openSaveDialog(file, timestamp);
        } finally {
            ui.disconnect(id);
            this._saving = false;
        }
    }

    _openSaveDialog(file, timestamp) {
        Main.overview.hide();
        const context = global.create_app_launch_context(timestamp, -1);
        const token = context.get_startup_notify_id(null, []) ?? '';
        const request = new GLib.Variant('(sava{sv})', [
            'save-capture', [new GLib.Variant('(ss)', [file.get_uri(), token])], {},
        ]);
        Gio.DBus.session.call('io.github.theayushlab.ScreenshotPreview',
            '/io/github/theayushlab/ScreenshotPreview', 'org.gtk.Actions', 'Activate',
            request, null, Gio.DBusCallFlags.NONE, 3000, null, (connection, result) => {
                try {
                    connection.call_finish(result);
                } catch (error) {
                    if (token)
                        context.launch_failed(token);
                    console.error(`Could not open screenshot Save As: ${error.message}`);
                }
            });
    }
}
