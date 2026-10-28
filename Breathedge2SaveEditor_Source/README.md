# Breathedge 2 Save Editor

Version 1.0.0 · Windows desktop application

This repository contains the complete Python source for the Save Editor distributed on Nexus Mods. It is a local-only Tkinter application for inspecting and editing supported Breathedge 2 save files.

## Features

- Browse autosaves and manual saves in the selected save directory.
- Edit player position, view direction, and playtime.
- Inspect inventory entries, change stack quantities, remove entries, and add items.
- Create a timestamped backup beside the original save before writing changes.
- Read the installed game's asset manifest for item names when available.
- German and English user interface.

The tool does not include game files or game assets. It does not connect to the internet. It reads and writes local save files only. The game should be closed before editing a save.

## Run from source

Requirements: 64-bit Windows, Python 3.14 with Tcl/Tk included. The application uses only Python standard-library modules.

```powershell
py -3.14 .\Breathedge2SaveEditor.py
```

If the `py` launcher is unavailable, run `python .\Breathedge2SaveEditor.py` using the Python 3.14 installation that includes Tkinter.

## Build the Windows application

The official Nexus download is packaged with PyInstaller in `onedir` mode. Follow [BUILDING.md](BUILDING.md) for the pinned build tool version and commands. The resulting application consists of `Breathedge2SaveEditor.exe` and its `_internal` directory; keep both together.

## Data safety

The editor creates a backup before saving. This is a safeguard, not a guarantee that every future game save format is supported. The inventory editor is enabled only for save layouts it recognizes. Keep an independent copy of important saves.

## AI disclosure

The application source and parts of its user interface were produced with substantial generative-AI assistance. The Nexus upload should use the applicable **AI-Generated Content** tag under Nexus Mods' current tagging rules.
