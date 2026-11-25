# Ubuntu Screenshots Addon

A GNOME Shell shortcut that opens **Save As** when you press **Ctrl+S** in the screenshot selector. It saves the PNG for the selected screen area to the location and filename you choose.

GNOME continues to handle ordinary captures: **Enter** takes a screenshot and **Ctrl+C** copies it. The companion service waits quietly in the background and opens a file dialog only when the add-on requests one.

## Requirements

- Ubuntu with GNOME Shell 50, using a Wayland session
- Python 3 with GTK 4 introspection, included in the standard Ubuntu GNOME desktop
- GNOME user extensions enabled

## Install

```sh
git clone https://github.com/ayushxaw/ubuntu-screenshots-addon.git
cd ubuntu-screenshots-addon
./install.sh
```

Sign out and back in after installing. GNOME discovers a manually installed Shell extension when the next session starts.

## Use

1. Open GNOME's screenshot selector with **Print Screen**.
2. Select an area.
3. Press **Ctrl+S** to open **Save As**.

Press **Enter** to capture normally. Press **Ctrl+C** to copy the screenshot to the clipboard without opening **Save As**. GNOME also keeps its usual screenshot copy in `~/Pictures/Screenshots`.

## Uninstall

```sh
./uninstall.sh
```

This removes the user service and Shell extension installed by this project.
