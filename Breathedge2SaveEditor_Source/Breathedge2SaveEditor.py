from __future__ import annotations

import copy
import hashlib
import math
import os
import re
import shutil
import struct
import tempfile
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


APP_TITLE = "Breathedge 2 — Save Editor"
DEFAULT_SAVE_DIR = (
    Path.home()
    / "AppData"
    / "Local"
    / "Breathedge2Game"
    / "Saved"
    / "SaveGames"
)
STEAM_GAME_DIR = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Breathedge2"
)
ITEM_MANIFEST = STEAM_GAME_DIR / "Manifest_UFSFiles_Win64.txt"
SAVE_CLASS = b"/Game/Base/GeneralObjects/BP_SaveGameData.BP_SaveGameData_C"
STRUCT_PATH = "/Script/CoreUObject"
TICKS_PER_HOUR = 36_000_000_000
MAX_COORDINATE = 1_000_000_000.0
MAX_STACK_COUNT = 9999
COLORS = {
    "background": "#0b1220",
    "panel": "#111b2c",
    "panel_alt": "#17243a",
    "panel_hover": "#20324c",
    "border": "#263750",
    "text": "#e8eef8",
    "muted": "#91a2ba",
    "accent": "#61c7f2",
    "accent_hover": "#8bd9fa",
    "accent_text": "#071522",
    "danger": "#3a1e2a",
    "danger_hover": "#542635",
    "danger_text": "#ffc7d2",
    "selection": "#214c70",
}
TEXTS = {
    "de": {
        "window_title": "Breathedge 2 — Save Editor",
        "status_choose_save": "Wähle links einen Speicherstand aus.",
        "eyebrow": "LOKALER SPIELSTAND-EDITOR",
        "subtitle": "Spielstand verwalten",
        "offline_badge": "OFFLINE  •  LOKALE DATEI",
        "language": "SPRACHE",
        "save_folder": "SAVE-ORDNER",
        "choose_folder": "Ordner wählen",
        "refresh": "↻  Aktualisieren",
        "saves_title": "  DEINE SPEICHERSTÄNDE  ",
        "slot": "Slot",
        "modified": "Geändert",
        "saves_footer": "Automatische und manuelle Spielstände",
        "selected_save": "  AUSGEWÄHLTER SPIELSTAND  ",
        "no_save_selected": "Kein Speicherstand ausgewählt.",
        "player_tab": "SPIELERWERTE",
        "inventory_tab": "INVENTAR",
        "editable_values": "Bearbeitbare Werte",
        "position": "Spielerposition (cm)",
        "orientation": "Blickrichtung (Grad)",
        "playtime": "Spielzeit",
        "hours_since_start": "Stunden seit Spielbeginn",
        "save_hint": "Vor dem Bearbeiten Breathedge 2 schließen. Beim Speichern wird automatisch eine Sicherungskopie neben dem Original angelegt.",
        "discard": "Änderungen verwerfen",
        "save": "Änderungen speichern",
        "choose_supported_save": "Wähle einen unterstützten Speicherstand aus.",
        "item": "Item",
        "quantity": "Menge",
        "durability": "Haltbarkeit",
        "charge": "Ladung",
        "asset_path_none": "Asset-Pfad: —",
        "selected_quantity": "Menge des ausgewählten Items",
        "apply_quantity": "Menge übernehmen",
        "remove_item": "Item entfernen",
        "add_item": "Item hinzufügen",
        "add": "+  Hinzufügen",
        "folder_dialog": "Breathedge 2-Speicherordner wählen",
        "folder_missing": "Speicherordner nicht gefunden. Wähle den SaveGames-Ordner aus.",
        "folder_missing_status": "Ordner nicht gefunden: {folder}",
        "saves_found_one": "1 Speicherstand gefunden.",
        "saves_found_many": "{count} Speicherstände gefunden.",
        "no_saves": "Keine *_Data.sav-Dateien in diesem Ordner gefunden.",
        "choose_save_meta": "Wähle links einen Speicherstand aus.",
        "unsupported_file": "Datei kann nicht sicher bearbeitet werden:\n{error}",
        "unsupported_save": "Nur unterstützte Breathedge 2-Spielstände können geändert werden.",
        "meta_summary": "Slot: {slot}\nDatei: {filename}\nZuletzt geändert: {modified}    |    Spielversion: {version}\nKapitelkennung: {stage}    |    Dateigröße: {size:,.1f} KB",
        "status_loaded": "Speicherstand geladen. Spielerwerte und Inventar können bearbeitet werden.",
        "inventory_unsupported": "Inventar ist für dieses Save-Format nicht freigegeben: {error}",
        "inventory_loaded": "{count} Einträge geladen. Stapelbare Mengen lassen sich ändern; Einzelstücke können entfernt oder erneut hinzugefügt werden.",
        "single_item": "1 (Einzelstück)",
        "asset_path": "Asset-Pfad: {path}",
        "invalid_quantity_title": "Ungültige Menge",
        "quantity_whole": "Die Menge muss eine ganze Zahl sein.",
        "quantity_range": "Die Menge muss zwischen 1 und {maximum} liegen.",
        "status_quantity_set": "Menge von {item} auf {count} gesetzt.",
        "status_item_removed": "{item} wird beim Speichern aus dem Inventar entfernt.",
        "error_no_template": "Dieser Spielstand enthält keine Vorlage zum Erstellen eines Inventareintrags.",
        "error_no_stackable_template": "Es gibt keine stapelbare Vorlage in diesem Inventar.",
        "error_no_count_field": "Für diesen Eintrag gibt es kein Mengenfeld.",
        "error_single_item": "Dieser Eintrag ist ein Einzelstück und hat kein Mengenfeld.",
        "error_choose_item": "Wähle ein Item aus der Liste aus.",
        "error_add_title": "Item konnte nicht hinzugefügt werden",
        "error_item_title": "Item fehlt",
        "status_item_added": "{item} wird beim Speichern zum Inventar hinzugefügt.",
        "status_reloaded": "Spielerwerte und Inventar aus dem Original-Speicherstand erneut geladen.",
        "number_required": "„{field}“ muss eine Zahl sein.",
        "finite_required": "„{field}“ muss eine endliche Zahl sein.",
        "coordinate_range": "„{field}“ liegt außerhalb des erlaubten Koordinatenbereichs.",
        "hours_number": "Die Spielzeit muss eine Zahl sein.",
        "hours_range": "Die Spielzeit muss zwischen 0 und 1.000.000 Stunden liegen.",
        "invalid_input_title": "Ungültige Eingabe",
        "read_error_title": "Lesefehler",
        "read_error": "Der Speicherstand kann nicht gelesen werden:\n{error}",
        "save_changed_title": "Speicherstand geändert",
        "save_changed": "Die Datei wurde seit dem Laden geändert. Lade den Speicherstand neu, bevor du speicherst.",
        "inventory_save_error_title": "Inventar konnte nicht gespeichert werden",
        "save_error_title": "Speichern fehlgeschlagen",
        "save_error": "Die Datei konnte nicht sicher geschrieben werden:\n{error}",
        "saved_status": "Gespeichert. Sicherung: {backup}",
        "saved_title": "Speicherstand aktualisiert",
        "saved_message": "Die Änderungen wurden gespeichert.\n\nSicherungskopie:\n{backup}",
        "language_changed_de": "Sprache auf Deutsch umgestellt.",
        "language_changed_en": "Language set to English.",
        "unknown": "unbekannt",
        "autosave_prefix": "Automatisches Speichern",
        "autosave_english": "Autosave",
        "category_consumption": "Verbrauchsgüter",
        "category_resources": "Ressourcen",
        "category_collectable": "Sammlerstücke",
        "category_tools": "Werkzeuge",
        "category_equipment": "Ausrüstung",
        "category_weapons": "Waffen",
    },
    "en": {
        "window_title": "Breathedge 2 — Save Editor",
        "status_choose_save": "Select a save from the list.",
        "eyebrow": "LOCAL SAVE EDITOR",
        "subtitle": "Manage your save",
        "offline_badge": "OFFLINE  •  LOCAL SAVE",
        "language": "LANGUAGE",
        "save_folder": "SAVE FOLDER",
        "choose_folder": "Browse",
        "refresh": "↻  Refresh",
        "saves_title": "  YOUR SAVES  ",
        "slot": "Slot",
        "modified": "Modified",
        "saves_footer": "Autosaves and manual saves",
        "selected_save": "  SELECTED SAVE  ",
        "no_save_selected": "No save selected.",
        "player_tab": "PLAYER",
        "inventory_tab": "INVENTORY",
        "editable_values": "Editable values",
        "position": "Player position (cm)",
        "orientation": "View direction (degrees)",
        "playtime": "Playtime",
        "hours_since_start": "Hours since start",
        "save_hint": "Close Breathedge 2 before editing. Saving automatically creates a backup next to the original file.",
        "discard": "Discard changes",
        "save": "Save changes",
        "choose_supported_save": "Select a supported save file.",
        "item": "Item",
        "quantity": "Quantity",
        "durability": "Durability",
        "charge": "Charge",
        "asset_path_none": "Asset path: —",
        "selected_quantity": "Selected item quantity",
        "apply_quantity": "Apply quantity",
        "remove_item": "Remove item",
        "add_item": "Add item",
        "add": "+  Add",
        "folder_dialog": "Choose Breathedge 2 save folder",
        "folder_missing": "Save folder not found. Choose the SaveGames folder.",
        "folder_missing_status": "Folder not found: {folder}",
        "saves_found_one": "1 save found.",
        "saves_found_many": "{count} saves found.",
        "no_saves": "No *_Data.sav files found in this folder.",
        "choose_save_meta": "Select a save from the list.",
        "unsupported_file": "This file cannot be safely edited:\n{error}",
        "unsupported_save": "Only supported Breathedge 2 saves can be edited.",
        "meta_summary": "Slot: {slot}\nFile: {filename}\nModified: {modified}    |    Game version: {version}\nChapter: {stage}    |    File size: {size:,.1f} KB",
        "status_loaded": "Save loaded. Player values and inventory are ready to edit.",
        "inventory_unsupported": "Inventory editing is unavailable for this save format: {error}",
        "inventory_loaded": "{count} entries loaded. Stack quantities can be changed; single items can be removed or added again.",
        "single_item": "1 (single item)",
        "asset_path": "Asset path: {path}",
        "invalid_quantity_title": "Invalid quantity",
        "quantity_whole": "Quantity must be a whole number.",
        "quantity_range": "Quantity must be between 1 and {maximum}.",
        "status_quantity_set": "Set {item} quantity to {count}.",
        "status_item_removed": "{item} will be removed from the inventory when saved.",
        "error_no_template": "This save has no inventory entry that can be used as a template.",
        "error_no_stackable_template": "There is no stackable template in this inventory.",
        "error_no_count_field": "This entry has no quantity field.",
        "error_single_item": "This is a single item and has no quantity field.",
        "error_choose_item": "Choose an item from the list.",
        "error_add_title": "Could not add item",
        "error_item_title": "No item selected",
        "status_item_added": "{item} will be added to the inventory when saved.",
        "status_reloaded": "Player values and inventory reloaded from the original save.",
        "number_required": "“{field}” must be a number.",
        "finite_required": "“{field}” must be a finite number.",
        "coordinate_range": "“{field}” is outside the allowed coordinate range.",
        "hours_number": "Playtime must be a number.",
        "hours_range": "Playtime must be between 0 and 1,000,000 hours.",
        "invalid_input_title": "Invalid input",
        "read_error_title": "Read error",
        "read_error": "The save file could not be read:\n{error}",
        "save_changed_title": "Save changed",
        "save_changed": "The file changed after it was loaded. Reload the save before saving.",
        "inventory_save_error_title": "Could not save inventory",
        "save_error_title": "Save failed",
        "save_error": "The file could not be written safely:\n{error}",
        "saved_status": "Saved. Backup: {backup}",
        "saved_title": "Save updated",
        "saved_message": "Changes saved.\n\nBackup copy:\n{backup}",
        "language_changed_de": "Sprache auf Deutsch umgestellt.",
        "language_changed_en": "Language set to English.",
        "unknown": "unknown",
        "autosave_prefix": "Automatisches Speichern",
        "autosave_english": "Autosave",
        "category_consumption": "Consumables",
        "category_resources": "Resources",
        "category_collectable": "Collectibles",
        "category_tools": "Tools",
        "category_equipment": "Equipment",
        "category_weapons": "Weapons",
    },
}

ERROR_TEXTS_EN = {
    "Unerwartetes Dateiende beim Lesen eines FString.": "Unexpected end of file while reading a string.",
    "Ungültiger FString im Speicherstand.": "The save contains an invalid string.",
    "Ungültiger UTF-16-FString im Speicherstand.": "The save contains an invalid UTF-16 string.",
    "Unvollständiger Eigenschafts-Header.": "The property header is incomplete.",
    "Unvollständiger Struct-Header.": "The struct header is incomplete.",
    "Ein Inventareintrag hat kein unterstütztes DataAsset-Feld.": "An inventory entry has an unsupported DataAsset field.",
    "Der Item-Pfad im Inventar ist ungültig.": "The item path in the inventory is invalid.",
    "Das Feld InventoryBytes wurde nicht gefunden.": "The InventoryBytes field was not found.",
    "InventoryBytes hat ein unbekanntes Format.": "InventoryBytes has an unknown format.",
    "Der Inventar-Arraytyp wird nicht unterstützt.": "This inventory array type is not supported.",
    "Die Länge von InventoryBytes ist ungültig.": "The InventoryBytes length is invalid.",
    "Die Inventarversion wird nicht sicher unterstützt.": "This inventory version is not supported.",
    "Die Inventarliste enthält eine ungültige Anzahl Einträge.": "The inventory contains an invalid number of entries.",
    "Der Inventarlistenmarker ist unbekannt.": "The inventory list marker is unknown.",
    "Die Inventareinträge konnten nicht sicher abgegrenzt werden.": "The inventory entries could not be separated safely.",
    "Ein Inventareintrag hat eine ungültige Länge.": "An inventory entry has an invalid length.",
    "Der Item-Pfad im Vorlageneintrag kommt unerwartet oft vor.": "The item path appears an unexpected number of times in the template.",
    "Für diesen Eintrag gibt es kein Mengenfeld.": "This entry has no quantity field.",
    "Dieser Eintrag ist ein Einzelstück und hat kein Mengenfeld.": "This is a single item and has no quantity field.",
    "Der neue InventoryBytes-Block ist unvollständig.": "The new InventoryBytes block is incomplete.",
    "Die Datei beginnt nicht mit dem Unreal-Save-Header GVAS.": "The file does not start with the Unreal GVAS save header.",
    "Das ist kein unterstützter Breathedge 2-Spielstand.": "This is not a supported Breathedge 2 save.",
    "Der SaveGame-Header ist nicht vollständig.": "The save game header is incomplete.",
}


class SaveFormatError(ValueError):
    """The save file does not match the supported Breathedge 2 layout."""


def read_fstring(data: bytes | bytearray, offset: int) -> tuple[str, int]:
    if offset + 4 > len(data):
        raise SaveFormatError("Unerwartetes Dateiende beim Lesen eines FString.")
    length = struct.unpack_from("<i", data, offset)[0]
    offset += 4
    if length == 0:
        return "", offset
    if length > 0:
        end = offset + length
        if end > len(data) or data[end - 1] != 0:
            raise SaveFormatError("Ungültiger FString im Speicherstand.")
        return bytes(data[offset : end - 1]).decode("utf-8", "replace"), end
    char_count = -length
    end = offset + char_count * 2
    if end > len(data):
        raise SaveFormatError("Ungültiger UTF-16-FString im Speicherstand.")
    raw = bytes(data[offset:end])
    if raw.endswith(b"\0\0"):
        raw = raw[:-2]
    return raw.decode("utf-16-le", "replace"), end


def fstring_bytes(value: str) -> bytes:
    raw = value.encode("utf-8") + b"\0"
    return struct.pack("<i", len(raw)) + raw


def find_struct_value(
    data: bytes,
    class_end: int,
    name: str,
    expected_struct: str,
    expected_size: int,
) -> int:
    """Return the start of a known UE5 struct payload, after its 8-byte marker."""
    needle = fstring_bytes(name)
    limit = min(len(data), class_end + 32_768)
    tag_start = data.find(needle, class_end, limit)
    if tag_start < 0:
        raise SaveFormatError(f"Die Eigenschaft „{name}“ wurde nicht gefunden.")

    parsed_name, cursor = read_fstring(data, tag_start)
    prop_type, cursor = read_fstring(data, cursor)
    if parsed_name != name or prop_type != "StructProperty":
        raise SaveFormatError(f"Die Eigenschaft „{name}“ hat ein unbekanntes Format.")

    if cursor + 4 > len(data):
        raise SaveFormatError("Unvollständiger Eigenschafts-Header.")
    array_index = struct.unpack_from("<i", data, cursor)[0]
    cursor += 4
    struct_name, cursor = read_fstring(data, cursor)
    if cursor + 4 > len(data):
        raise SaveFormatError("Unvollständiger Struct-Header.")
    struct_marker = struct.unpack_from("<I", data, cursor)[0]
    cursor += 4
    struct_path, cursor = read_fstring(data, cursor)
    if cursor + 8 > len(data):
        raise SaveFormatError("Unvollständiger Struct-Header.")
    property_guid_flag, property_size = struct.unpack_from("<II", data, cursor)
    cursor += 8

    if (
        array_index != 1
        or struct_name != expected_struct
        or struct_marker != 1
        or struct_path != STRUCT_PATH
        or property_guid_flag != 0
        or property_size != expected_size
        or cursor + 1 + expected_size > len(data)
        or data[cursor] != 8
    ):
        raise SaveFormatError(
            f"Das Format von „{name}“ weicht vom unterstützten Spielstand ab. "
            "Die Datei wurde nur lesend geöffnet."
        )
    return cursor + 1


def read_property(
    data: bytes | bytearray,
    name: str,
    expected_type: str,
) -> tuple[int, int, int] | None:
    """Return (value offset, property size, size-field offset) for a simple tag."""
    needle = fstring_bytes(name)
    search_from = 0
    while True:
        tag_start = data.find(needle, search_from)
        if tag_start < 0:
            return None
        search_from = tag_start + 1
        try:
            parsed_name, cursor = read_fstring(data, tag_start)
            prop_type, cursor = read_fstring(data, cursor)
        except SaveFormatError:
            continue
        if parsed_name != name or prop_type != expected_type or cursor + 9 > len(data):
            continue
        _array_index, size = struct.unpack_from("<ii", data, cursor)
        size_offset = cursor + 4
        value_offset = cursor + 9
        if size < 0 or value_offset + size > len(data):
            continue
        return value_offset, size, size_offset


@dataclass
class InventoryItem:
    asset_path: str
    count: int | None
    durability: float | None
    charge: float | None
    sort_index: int | None
    raw: bytes
    count_offset: int | None
    tail_count_offset: int | None
    sort_index_offset: int | None
    tail_sort_offset: int | None
    dataasset_size_offset: int


def read_inventory_item(raw: bytes) -> InventoryItem:
    name, cursor = read_fstring(raw, 0)
    prop_type, cursor = read_fstring(raw, cursor)
    if name != "DataAsset" or prop_type != "ObjectProperty" or cursor + 9 > len(raw):
        raise SaveFormatError("Ein Inventareintrag hat kein unterstütztes DataAsset-Feld.")

    _array_index, property_size = struct.unpack_from("<ii", raw, cursor)
    property_size_offset = cursor + 4
    path_offset = cursor + 9
    asset_path, path_end = read_fstring(raw, path_offset)
    if (
        not asset_path.startswith("/Game/Items/")
        or property_size != path_end - path_offset
    ):
        raise SaveFormatError("Der Item-Pfad im Inventar ist ungültig.")

    count_tag = read_property(raw, "Count", "IntProperty")
    durability_tag = read_property(raw, "Durability", "FloatProperty")
    charge_tag = read_property(raw, "Charge", "FloatProperty")
    sort_tag = read_property(raw, "SortIndex", "IntProperty")

    count = None
    if count_tag and count_tag[1] == 4:
        count = struct.unpack_from("<i", raw, count_tag[0])[0]
    durability = None
    if durability_tag and durability_tag[1] == 4:
        durability = struct.unpack_from("<f", raw, durability_tag[0])[0]
    charge = None
    if charge_tag and charge_tag[1] == 4:
        charge = struct.unpack_from("<f", raw, charge_tag[0])[0]
    sort_index = None
    if sort_tag and sort_tag[1] == 4:
        sort_index = struct.unpack_from("<i", raw, sort_tag[0])[0]

    encoded_path = fstring_bytes(asset_path)
    first_path = raw.find(encoded_path, path_offset)
    second_path = raw.find(encoded_path, first_path + len(encoded_path))
    tail_start = second_path + len(encoded_path) if second_path >= 0 else None
    tail_count_offset = None
    tail_sort_offset = None
    if tail_start is not None:
        if count is not None and tail_start + 4 <= len(raw):
            if struct.unpack_from("<i", raw, tail_start)[0] == count:
                tail_count_offset = tail_start
        if sort_index is not None and tail_start + 20 <= len(raw):
            if struct.unpack_from("<i", raw, tail_start + 16)[0] == sort_index:
                tail_sort_offset = tail_start + 16

    return InventoryItem(
        asset_path=asset_path,
        count=count,
        durability=durability,
        charge=charge,
        sort_index=sort_index,
        raw=raw,
        count_offset=count_tag[0] if count_tag and count_tag[1] == 4 else None,
        tail_count_offset=tail_count_offset,
        sort_index_offset=sort_tag[0] if sort_tag and sort_tag[1] == 4 else None,
        tail_sort_offset=tail_sort_offset,
        dataasset_size_offset=property_size_offset,
    )


@dataclass
class InventoryDocument:
    size_offset: int
    value_offset: int
    original_size: int
    prefix: bytes
    suffix: bytes
    items: list[InventoryItem]
    version: int


def parse_inventory(data: bytes, class_end: int) -> InventoryDocument:
    needle = fstring_bytes("InventoryBytes")
    tag_start = data.find(needle, class_end)
    if tag_start < 0:
        raise SaveFormatError("Das Feld InventoryBytes wurde nicht gefunden.")

    name, cursor = read_fstring(data, tag_start)
    prop_type, cursor = read_fstring(data, cursor)
    if name != "InventoryBytes" or prop_type != "ArrayProperty" or cursor + 4 > len(data):
        raise SaveFormatError("InventoryBytes hat ein unbekanntes Format.")

    array_index = struct.unpack_from("<i", data, cursor)[0]
    cursor += 4
    inner_type, cursor = read_fstring(data, cursor)
    if array_index != 1 or inner_type != "ByteProperty" or cursor + 8 > len(data):
        raise SaveFormatError("Der Inventar-Arraytyp wird nicht unterstützt.")

    guid_flag = struct.unpack_from("<I", data, cursor)[0]
    size_offset = cursor + 4
    value_offset = size_offset + 4
    property_size = struct.unpack_from("<I", data, size_offset)[0]
    if guid_flag != 0 or property_size < 13 or value_offset + property_size > len(data):
        raise SaveFormatError("Die Länge von InventoryBytes ist ungültig.")

    blob = data[value_offset : value_offset + property_size]
    inner_size = struct.unpack_from("<I", blob, 1)[0]
    version = struct.unpack_from("<I", blob, 5)[0]
    item_count = struct.unpack_from("<I", blob, 9)[0]
    if blob[0] != 0 or inner_size != property_size - 4 or version != 3:
        raise SaveFormatError("Die Inventarversion wird nicht sicher unterstützt.")
    if item_count > 10_000:
        raise SaveFormatError("Die Inventarliste enthält eine ungültige Anzahl Einträge.")

    # The byte array stores a one-byte marker after its 12-byte header.
    item_start = 14
    if blob[13] != 0:
        raise SaveFormatError("Der Inventarlistenmarker ist unbekannt.")
    pattern = fstring_bytes("DataAsset") + fstring_bytes("ObjectProperty")
    starts: list[int] = []
    search_from = item_start
    while True:
        found = blob.find(pattern, search_from)
        if found < 0:
            break
        starts.append(found)
        search_from = found + 1

    if item_count:
        if len(starts) <= item_count or starts[0] != item_start:
            raise SaveFormatError("Die Inventareinträge konnten nicht sicher abgegrenzt werden.")
        entry_end = starts[item_count]
    else:
        entry_end = starts[0] if starts else len(blob)

    items: list[InventoryItem] = []
    for index in range(item_count):
        start = starts[index]
        end = starts[index + 1]
        if end <= start:
            raise SaveFormatError("Ein Inventareintrag hat eine ungültige Länge.")
        items.append(read_inventory_item(blob[start:end]))

    return InventoryDocument(
        size_offset=size_offset,
        value_offset=value_offset,
        original_size=property_size,
        prefix=blob[:item_start],
        suffix=blob[entry_end:],
        items=items,
        version=version,
    )


def asset_category(asset_path: str) -> str:
    parts = asset_path.split("/")
    try:
        return parts[parts.index("Items") + 1]
    except (ValueError, IndexError):
        return "Sonstige"


def asset_label(asset_path: str) -> str:
    leaf = asset_path.rsplit("/", 1)[-1].split(".", 1)[0]
    if leaf.startswith("DA_"):
        leaf = leaf[3:]
    leaf = leaf.replace("_", " ")
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", leaf)


@dataclass(frozen=True)
class AssetOption:
    asset_path: str
    label: str


def load_item_catalog(fallback_paths: list[str], language: str = "de") -> list[AssetOption]:
    paths: set[str] = set()
    try:
        if ITEM_MANIFEST.is_file():
            for line in ITEM_MANIFEST.read_text(encoding="utf-8", errors="replace").splitlines():
                relative = line.split("\t", 1)[0].replace("\\", "/")
                if not relative.endswith(".uasset") or "/Content/Items/" not in relative:
                    continue
                if "/DataAssets/DA_" not in relative:
                    continue
                package = relative.split("/Content/", 1)[1][:-7]
                asset_name = package.rsplit("/", 1)[-1]
                paths.add(f"/Game/{package}.{asset_name}")
    except OSError:
        pass

    paths.update(fallback_paths)
    category_keys = {
        "Consumption": "category_consumption",
        "Resources": "category_resources",
        "Collectable": "category_collectable",
        "Tools": "category_tools",
        "Equipment": "category_equipment",
        "Weapons": "category_weapons",
    }
    options: list[AssetOption] = []
    seen_labels: set[str] = set()
    for asset_path in sorted(
        paths,
        key=lambda value: (
            asset_category(value).lower(),
            asset_label(value).lower(),
            value.lower(),
        ),
    ):
        category = asset_category(asset_path)
        translated_category = TEXTS[language].get(category_keys.get(category, ""), category)
        label = f"{translated_category} — {asset_label(asset_path)}"
        if label in seen_labels:
            label += f" [{asset_path.rsplit('/', 1)[-1].split('.')[0]}]"
        seen_labels.add(label)
        options.append(AssetOption(asset_path=asset_path, label=label))
    return options


def clone_inventory_item(template: InventoryItem, new_path: str, count: int, sort_index: int) -> InventoryItem:
    old_path_bytes = fstring_bytes(template.asset_path)
    new_path_bytes = fstring_bytes(new_path)
    positions: list[int] = []
    search_from = 0
    while True:
        found = template.raw.find(old_path_bytes, search_from)
        if found < 0:
            break
        positions.append(found)
        search_from = found + len(old_path_bytes)
    if len(positions) != 2:
        raise SaveFormatError("Der Item-Pfad im Vorlageneintrag kommt unerwartet oft vor.")

    raw = bytearray(template.raw)
    for position in reversed(positions):
        raw[position : position + len(old_path_bytes)] = new_path_bytes

    struct.pack_into("<i", raw, template.dataasset_size_offset, len(new_path_bytes))

    count_tag = read_property(raw, "Count", "IntProperty")
    if count_tag and count_tag[1] == 4:
        struct.pack_into("<i", raw, count_tag[0], count)
    elif count != 1:
        raise SaveFormatError("Für diesen Eintrag gibt es kein Mengenfeld.")

    sort_tag = read_property(raw, "SortIndex", "IntProperty")
    if sort_tag and sort_tag[1] == 4:
        struct.pack_into("<i", raw, sort_tag[0], sort_index)

    result = read_inventory_item(bytes(raw))
    if result.tail_count_offset is not None and result.count is not None:
        struct.pack_into("<i", raw, result.tail_count_offset, result.count)
    if result.tail_sort_offset is not None and result.sort_index is not None:
        struct.pack_into("<i", raw, result.tail_sort_offset, result.sort_index)
    return read_inventory_item(bytes(raw))


def update_inventory_count(item: InventoryItem, count: int) -> InventoryItem:
    if item.count_offset is None:
        raise SaveFormatError("Dieser Eintrag ist ein Einzelstück und hat kein Mengenfeld.")
    raw = bytearray(item.raw)
    struct.pack_into("<i", raw, item.count_offset, count)
    if item.tail_count_offset is not None:
        struct.pack_into("<i", raw, item.tail_count_offset, count)
    return read_inventory_item(bytes(raw))


def write_inventory(data: bytes, document: InventoryDocument, items: list[InventoryItem]) -> bytes:
    blob = bytearray(document.prefix + b"".join(item.raw for item in items) + document.suffix)
    if len(blob) < 13:
        raise SaveFormatError("Der neue InventoryBytes-Block ist unvollständig.")
    struct.pack_into("<I", blob, 1, len(blob) - 4)
    struct.pack_into("<I", blob, 9, len(items))

    new_data = bytearray(
        data[: document.value_offset]
        + bytes(blob)
        + data[document.value_offset + document.original_size :]
    )
    struct.pack_into("<I", new_data, document.size_offset, len(blob))
    return bytes(new_data)


def extract_header_info(path: Path, fallback_slot: str) -> tuple[str, str]:
    header_path = Path(str(path).replace("_Data.sav", "_Header.sav"))
    if not header_path.exists():
        return fallback_slot, "unbekannt"
    try:
        raw = header_path.read_bytes()
    except OSError:
        return fallback_slot, "unbekannt"

    slot = fallback_slot
    for match in re.finditer(rb"(?:Automatisches Speichern|Autosave)[^\x00]{0,48}", raw):
        slot = match.group(0).decode("utf-8", "replace")
        break
    version_match = re.search(rb"(?<![0-9])\d+\.\d+\.\d+(?![0-9])", raw)
    version = version_match.group(0).decode("ascii") if version_match else "unbekannt"
    return slot, version


@dataclass
class SaveRecord:
    path: Path
    display_name: str
    modified: str
    stage: str
    game_version: str
    location_offsets: tuple[int, int, int]
    rotation_offsets: tuple[int, int, int]
    time_offset: int
    inventory: InventoryDocument | None
    inventory_error: str | None
    source_bytes: bytes
    source_hash: str


def parse_save(path: Path) -> SaveRecord:
    raw = path.read_bytes()
    if not raw.startswith(b"GVAS"):
        raise SaveFormatError("Die Datei beginnt nicht mit dem Unreal-Save-Header GVAS.")

    class_needle = fstring_bytes(SAVE_CLASS.decode("ascii"))
    class_start = raw.find(class_needle)
    if class_start < 0:
        raise SaveFormatError("Das ist kein unterstützter Breathedge 2-Spielstand.")
    _, class_end = read_fstring(raw, class_start)
    if class_end >= len(raw) or raw[class_end] != 0:
        raise SaveFormatError("Der SaveGame-Header ist nicht vollständig.")
    class_end += 1

    location = find_struct_value(raw, class_end, "PlayerLocation", "Vector", 24)
    rotation = find_struct_value(raw, class_end, "PlayerRotation", "Rotator", 24)
    game_time = find_struct_value(raw, class_end, "GameTime", "Timespan", 8)
    stage_match = re.search(rb"GameStage::([A-Za-z0-9_]+)", raw[: min(len(raw), class_end + 32_768)])
    stage = stage_match.group(1).decode("ascii") if stage_match else "unbekannt"

    inventory = None
    inventory_error = None
    try:
        inventory = parse_inventory(raw, class_end)
    except SaveFormatError as exc:
        inventory_error = str(exc)

    slot_number = re.search(r"Auto_(\d+)_Data\.sav$", path.name, re.IGNORECASE)
    fallback_slot = f"Automatisches Speichern {int(slot_number.group(1)) + 1}" if slot_number else path.stem
    display_name, header_version = extract_header_info(path, fallback_slot)
    save_version_match = re.search(rb"(?<![0-9])\d+\.\d+\.\d+(?![0-9])", raw[: min(len(raw), class_end + 32_768)])
    game_version = save_version_match.group(0).decode("ascii") if save_version_match else header_version
    modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%d.%m.%Y %H:%M")

    return SaveRecord(
        path=path,
        display_name=display_name,
        modified=modified,
        stage=stage,
        game_version=game_version,
        location_offsets=tuple(location + i * 8 for i in range(3)),
        rotation_offsets=tuple(rotation + i * 8 for i in range(3)),
        time_offset=game_time,
        inventory=inventory,
        inventory_error=inventory_error,
        source_bytes=raw,
        source_hash=hashlib.sha256(raw).hexdigest(),
    )


class BreathedgeSaveEditor:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1140x780")
        self.root.minsize(1000, 680)

        self.language = tk.StringVar(value="Deutsch")
        self.language_code = "de"
        self.localized_widgets: list[tuple[object, str]] = []
        self.localized_headings: list[tuple[ttk.Treeview, str, str]] = []
        self.notebook: ttk.Notebook | None = None
        self.notebook_tabs: dict[str, object] = {}
        self.directory = tk.StringVar(value=str(DEFAULT_SAVE_DIR))
        self.status = tk.StringVar(value=self.t("status_choose_save"))
        self.fields: dict[str, tk.StringVar] = {}
        self.record: SaveRecord | None = None
        self.current_path: Path | None = None
        self.inventory_document: InventoryDocument | None = None
        self.inventory_items: list[InventoryItem] = []
        self.catalog: list[AssetOption] = []
        self.catalog_by_label: dict[str, str] = {}
        self.inventory_count_var = tk.StringVar(value="1")
        self.add_count_var = tk.StringVar(value="1")
        self.inventory_tree: ttk.Treeview
        self.tree: ttk.Treeview
        self.meta_label: ttk.Label
        self.inventory_note: ttk.Label
        self.inventory_path_label: ttk.Label
        self.inventory_count_spin: ttk.Spinbox
        self.apply_count_button: ttk.Button
        self.remove_item_button: ttk.Button
        self.add_combo: ttk.Combobox
        self.add_button: ttk.Button
        self.save_button: ttk.Button

        self._make_ui()
        self.refresh_saves()

    def t(self, key: str, **values: object) -> str:
        return TEXTS[self.language_code][key].format(**values)

    def _text(self, widget: object, key: str) -> object:
        self.localized_widgets.append((widget, key))
        widget.configure(text=self.t(key))
        return widget

    def _heading(self, tree: ttk.Treeview, column: str, key: str) -> None:
        self.localized_headings.append((tree, column, key))
        tree.heading(column, text=self.t(key))

    def _localized_error(self, error: object) -> str:
        message = str(error)
        if self.language_code == "de":
            return message
        if message in TEXTS["en"].values():
            return message
        if message.startswith("Quantity must be between 1 and "):
            return message
        if message in ERROR_TEXTS_EN:
            return ERROR_TEXTS_EN[message]
        dynamic = re.match(r"Die Eigenschaft „(.+)“ wurde nicht gefunden\.", message)
        if dynamic:
            return f'The "{dynamic.group(1)}" property was not found.'
        dynamic = re.match(r"Die Eigenschaft „(.+)“ hat ein unbekanntes Format\.", message)
        if dynamic:
            return f'The "{dynamic.group(1)}" property has an unknown format.'
        if message.startswith("Das Format von „"):
            return "This save uses a different format and was opened read-only."
        return "The save data uses an unsupported format."

    def _slot_label(self, path: Path) -> str:
        match = re.search(r"Auto_(\d+)_Data\.sav$", path.name, re.IGNORECASE)
        if not match:
            return path.stem
        prefix = self.t("autosave_english") if self.language_code == "en" else self.t("autosave_prefix")
        return f"{prefix} {int(match.group(1)) + 1}"

    def _localized_slot_name(self, slot: str) -> str:
        match = re.match(r"(?:Automatisches Speichern|Autosave)\s+(\d+)$", slot, re.IGNORECASE)
        if not match:
            return slot
        prefix = self.t("autosave_english") if self.language_code == "en" else self.t("autosave_prefix")
        return f"{prefix} {match.group(1)}"

    def _update_meta_label(self) -> None:
        if self.record is None:
            self.meta_label.configure(text=self.t("no_save_selected"))
            return
        record = self.record
        version = record.game_version
        stage = record.stage
        if version == "unbekannt":
            version = self.t("unknown")
        if stage == "unbekannt":
            stage = self.t("unknown")
        self.meta_label.configure(
            text=self.t(
                "meta_summary",
                slot=self._localized_slot_name(record.display_name),
                filename=record.path.name,
                modified=record.modified,
                version=version,
                stage=stage,
                size=len(record.source_bytes) / 1024,
            )
        )

    def _update_inventory_note(self) -> None:
        if self.record is None:
            self.inventory_note.configure(text=self.t("choose_supported_save"))
        elif self.inventory_document is None:
            self.inventory_note.configure(
                text=self.t(
                    "inventory_unsupported",
                    error=self._localized_error(self.record.inventory_error or "unbekanntes Format"),
                )
            )
        else:
            self.inventory_note.configure(
                text=self.t("inventory_loaded", count=len(self.inventory_items))
            )

    def on_language_change(self, _event: object = None) -> None:
        self.language_code = "en" if self.language.get() == "English" else "de"
        self.root.title(self.t("window_title"))
        for widget, key in self.localized_widgets:
            widget.configure(text=self.t(key))
        for tree, column, key in self.localized_headings:
            tree.heading(column, text=self.t(key))
        if self.notebook is not None:
            for key, tab in self.notebook_tabs.items():
                self.notebook.tab(tab, text=self.t(key))

        for iid in self.tree.get_children():
            values = self.tree.item(iid, "values")
            self.tree.item(iid, values=(self._slot_label(Path(iid)), values[1]))
        self._update_meta_label()
        self._update_inventory_note()
        selected_index = int(self.inventory_tree.selection()[0]) if self.inventory_tree.selection() else None
        pending_quantity = self.inventory_count_var.get()
        selected_asset_path = self.catalog_by_label.get(self.add_combo.get())
        current_paths = [option.asset_path for option in self.catalog]
        self.catalog = load_item_catalog(current_paths, self.language_code)
        self.catalog_by_label = {option.label: option.asset_path for option in self.catalog}
        self.add_combo.configure(values=[option.label for option in self.catalog])
        if self.catalog:
            matching = next((option.label for option in self.catalog if option.asset_path == selected_asset_path), None)
            self.add_combo.set(matching or self.catalog[0].label)
        self.refresh_inventory_tree(selected_index)
        if selected_index is not None:
            self.inventory_count_var.set(pending_quantity)
            if 0 <= selected_index < len(self.inventory_items):
                self.inventory_path_label.configure(
                    text=self.t("asset_path", path=self.inventory_items[selected_index].asset_path)
                )
        else:
            self.inventory_path_label.configure(text=self.t("asset_path_none"))
        self.status.set(self.t("language_changed_en" if self.language_code == "en" else "language_changed_de"))

    def _make_ui(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        self.root.configure(background=COLORS["background"])
        style.configure(".", font=("Segoe UI", 10), foreground=COLORS["text"])
        style.configure("TFrame", background=COLORS["background"])
        style.configure("App.TFrame", background=COLORS["background"])
        style.configure("Header.TFrame", background=COLORS["background"])
        style.configure("Toolbar.TFrame", background=COLORS["panel"])
        style.configure("TLabel", background=COLORS["panel"], foreground=COLORS["text"])
        style.configure("Card.TLabel", background=COLORS["panel"], foreground=COLORS["text"])
        style.configure("Title.TLabel", background=COLORS["background"], foreground=COLORS["text"], font=("Segoe UI", 24, "bold"))
        style.configure("Eyebrow.TLabel", background=COLORS["background"], foreground=COLORS["accent"], font=("Segoe UI", 9, "bold"))
        style.configure("Hint.TLabel", background=COLORS["background"], foreground=COLORS["muted"])
        style.configure("CardHint.TLabel", background=COLORS["panel"], foreground=COLORS["muted"])
        style.configure("Pill.TLabel", background=COLORS["panel_alt"], foreground=COLORS["accent"], font=("Segoe UI", 9, "bold"), padding=(12, 7))
        style.configure("Status.TLabel", background=COLORS["panel"], foreground=COLORS["muted"], padding=(12, 9))

        style.configure(
            "TLabelframe",
            background=COLORS["panel"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "TLabelframe.Label",
            background=COLORS["panel"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
            padding=(4, 0),
        )
        style.configure(
            "TEntry",
            fieldbackground=COLORS["panel_alt"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            padding=(10, 8),
        )
        style.map(
            "TEntry",
            fieldbackground=[("disabled", COLORS["panel"]), ("focus", COLORS["panel_alt"])],
            bordercolor=[("focus", COLORS["accent"])],
        )
        style.configure(
            "TButton",
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            padding=(12, 9),
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "TButton",
            background=[("disabled", COLORS["panel"]), ("pressed", COLORS["selection"]), ("active", COLORS["panel_hover"])],
            foreground=[("disabled", "#53647b"), ("active", COLORS["text"])],
        )
        style.configure(
            "Save.TButton",
            background=COLORS["accent"],
            foreground=COLORS["accent_text"],
            padding=(18, 10),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Save.TButton",
            background=[("disabled", COLORS["panel"]), ("pressed", COLORS["accent_hover"]), ("active", COLORS["accent_hover"])],
            foreground=[("disabled", "#53647b"), ("active", COLORS["accent_text"])],
        )
        style.configure(
            "Danger.TButton",
            background=COLORS["danger"],
            foreground=COLORS["danger_text"],
            padding=(12, 9),
        )
        style.map(
            "Danger.TButton",
            background=[("disabled", COLORS["panel"]), ("pressed", COLORS["danger_hover"]), ("active", COLORS["danger_hover"])],
        )
        style.configure(
            "TNotebook",
            background=COLORS["background"],
            borderwidth=0,
            tabmargins=(0, 0, 0, 0),
        )
        style.configure(
            "TNotebook.Tab",
            background=COLORS["panel"],
            foreground=COLORS["muted"],
            padding=(18, 11),
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["panel_alt"]), ("active", COLORS["panel_hover"])],
            foreground=[("selected", COLORS["accent"]), ("active", COLORS["text"])],
        )
        style.configure(
            "Treeview",
            background=COLORS["panel"],
            fieldbackground=COLORS["panel"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            rowheight=34,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["selection"])],
            foreground=[("selected", "#ffffff")],
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["panel_alt"],
            foreground=COLORS["muted"],
            relief="flat",
            padding=(10, 10),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Treeview.Heading",
            background=[("active", COLORS["panel_hover"])],
            foreground=[("active", COLORS["text"])],
        )
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["panel_alt"],
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["accent"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            padding=(8, 7),
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORS["panel_alt"]), ("disabled", COLORS["panel"])],
            foreground=[("readonly", COLORS["text"]), ("disabled", "#53647b")],
            selectbackground=[("readonly", COLORS["selection"])],
            selectforeground=[("readonly", "#ffffff")],
        )
        style.configure(
            "TSpinbox",
            fieldbackground=COLORS["panel_alt"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["accent"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            padding=(8, 7),
        )
        style.configure("TSeparator", background=COLORS["border"])
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["panel_alt"],
            troughcolor=COLORS["panel"],
            bordercolor=COLORS["panel"],
            arrowcolor=COLORS["muted"],
            relief="flat",
            arrowsize=12,
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", COLORS["panel_hover"]), ("pressed", COLORS["selection"])],
        )

        outer = ttk.Frame(self.root, style="App.TFrame", padding=22)
        outer.pack(fill="both", expand=True)
        header = ttk.Frame(outer, style="Header.TFrame")
        header.pack(fill="x", pady=(0, 18))
        title_block = ttk.Frame(header, style="Header.TFrame")
        title_block.pack(side="left", anchor="w")
        self._text(ttk.Label(title_block, style="Eyebrow.TLabel"), "eyebrow").pack(anchor="w")
        ttk.Label(title_block, text="Breathedge 2", style="Title.TLabel").pack(anchor="w", pady=(2, 0))
        self._text(ttk.Label(title_block, style="Hint.TLabel"), "subtitle").pack(anchor="w", pady=(1, 0))
        header_tools = ttk.Frame(header, style="Header.TFrame")
        header_tools.pack(side="right", anchor="center")
        self._text(ttk.Label(header_tools, style="Pill.TLabel"), "offline_badge").pack(side="right", anchor="center")
        self.language_combo = ttk.Combobox(
            header_tools,
            textvariable=self.language,
            values=("Deutsch", "English"),
            state="readonly",
            width=10,
        )
        self.language_combo.pack(side="right", padx=(0, 10))
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        self._text(ttk.Label(header_tools, style="Eyebrow.TLabel"), "language").pack(side="right", padx=(12, 7))

        path_row = ttk.Frame(outer, style="Toolbar.TFrame", padding=(14, 12))
        path_row.pack(fill="x", pady=(0, 16))
        self._text(ttk.Label(path_row, style="CardHint.TLabel"), "save_folder").pack(side="left", padx=(0, 12))
        ttk.Entry(path_row, textvariable=self.directory).pack(side="left", fill="x", expand=True)
        self._text(ttk.Button(path_row, command=self.choose_directory), "choose_folder").pack(side="left", padx=(10, 0))
        self._text(ttk.Button(path_row, command=self.refresh_saves), "refresh").pack(side="left", padx=(8, 0))

        body = ttk.Frame(outer)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1, minsize=340)
        body.columnconfigure(1, weight=2, minsize=560)
        body.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(body, padding=12)
        self._text(list_frame, "saves_title")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(
            list_frame,
            columns=("name", "updated"),
            show="headings",
            selectmode="browse",
        )
        self._heading(self.tree, "name", "slot")
        self._heading(self.tree, "updated", "modified")
        self.tree.column("name", width=190, anchor="w")
        self.tree.column("updated", width=125, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self._text(ttk.Label(
            list_frame,
            style="CardHint.TLabel",
            wraplength=290,
        ), "saves_footer").grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        meta_frame = ttk.LabelFrame(right, padding=14)
        self._text(meta_frame, "selected_save")
        meta_frame.grid(row=0, column=0, sticky="ew")
        self.meta_label = ttk.Label(meta_frame, style="Card.TLabel", justify="left", wraplength=700, text=self.t("no_save_selected"))
        self.meta_label.pack(anchor="w", fill="x")

        notebook = ttk.Notebook(right)
        self.notebook = notebook
        notebook.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        player_tab = ttk.Frame(notebook, padding=12)
        inventory_tab = ttk.Frame(notebook, padding=12)
        self.notebook_tabs = {"player_tab": player_tab, "inventory_tab": inventory_tab}
        notebook.add(player_tab, text=self.t("player_tab"))
        notebook.add(inventory_tab, text=self.t("inventory_tab"))

        player_tab.columnconfigure(0, weight=1)
        edit_frame = ttk.LabelFrame(player_tab, padding=12)
        self._text(edit_frame, "editable_values")
        edit_frame.pack(fill="x")
        edit_frame.columnconfigure(1, weight=1)
        edit_frame.columnconfigure(3, weight=1)
        edit_frame.columnconfigure(5, weight=1)
        self._add_group(edit_frame, "position", ("X", "Y", "Z"), (0, 0))
        self._add_group(edit_frame, "orientation", ("Pitch", "Yaw", "Roll"), (1, 0))
        self._add_time_field(edit_frame)

        self._text(ttk.Label(
            player_tab,
            style="Hint.TLabel",
            wraplength=650,
            justify="left",
        ), "save_hint").pack(fill="x", anchor="w", pady=(12, 0))

        self._make_inventory_tab(inventory_tab)

        actions = ttk.Frame(right)
        actions.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        actions.columnconfigure(0, weight=1)
        self._text(ttk.Button(actions, command=self.reload_selected), "discard").pack(side="left")
        self.save_button = ttk.Button(actions, style="Save.TButton", command=self.save_changes)
        self._text(self.save_button, "save")
        self.save_button.pack(side="right")
        self.save_button.state(["disabled"])

        ttk.Label(outer, textvariable=self.status, style="Status.TLabel", anchor="w").pack(fill="x", pady=(14, 0))

    def _make_inventory_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        self.inventory_note = ttk.Label(
            parent,
            text=self.t("choose_supported_save"),
            style="Hint.TLabel",
            wraplength=700,
            justify="left",
        )
        self.inventory_note.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        list_frame = ttk.Frame(parent)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.inventory_tree = ttk.Treeview(
            list_frame,
            columns=("item", "count", "durability", "charge"),
            show="headings",
            selectmode="browse",
        )
        self._heading(self.inventory_tree, "item", "item")
        self._heading(self.inventory_tree, "count", "quantity")
        self._heading(self.inventory_tree, "durability", "durability")
        self._heading(self.inventory_tree, "charge", "charge")
        self.inventory_tree.column("item", width=300, anchor="w")
        self.inventory_tree.column("count", width=110, anchor="center")
        self.inventory_tree.column("durability", width=110, anchor="center")
        self.inventory_tree.column("charge", width=90, anchor="center")
        self.inventory_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.inventory_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        self.inventory_tree.bind("<<TreeviewSelect>>", self.on_inventory_select)

        self.inventory_path_label = ttk.Label(parent, text=self.t("asset_path_none"), style="Hint.TLabel", wraplength=720)
        self.inventory_path_label.grid(row=2, column=0, sticky="ew", pady=(8, 6))

        controls = ttk.Frame(parent, style="Toolbar.TFrame", padding=(12, 10))
        controls.grid(row=3, column=0, sticky="ew")
        self._text(ttk.Label(controls, style="Card.TLabel"), "selected_quantity").pack(side="left")
        self.inventory_count_spin = ttk.Spinbox(
            controls,
            from_=1,
            to=MAX_STACK_COUNT,
            textvariable=self.inventory_count_var,
            width=8,
            state="disabled",
        )
        self.inventory_count_spin.pack(side="left", padx=(8, 6))
        self.apply_count_button = ttk.Button(
            controls,
            command=self.apply_inventory_count,
            state="disabled",
        )
        self._text(self.apply_count_button, "apply_quantity")
        self.apply_count_button.pack(side="left")
        self.remove_item_button = ttk.Button(
            controls,
            command=self.remove_inventory_item,
            style="Danger.TButton",
            state="disabled",
        )
        self._text(self.remove_item_button, "remove_item")
        self.remove_item_button.pack(side="right")

        add_frame = ttk.LabelFrame(parent, padding=10)
        self._text(add_frame, "add_item")
        add_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        add_frame.columnconfigure(0, weight=1)
        self.add_combo = ttk.Combobox(add_frame, state="readonly")
        self.add_combo.grid(row=0, column=0, sticky="ew")
        self._text(ttk.Label(add_frame), "quantity").grid(row=0, column=1, padx=(10, 5))
        ttk.Spinbox(
            add_frame,
            from_=1,
            to=MAX_STACK_COUNT,
            textvariable=self.add_count_var,
            width=8,
        ).grid(row=0, column=2, padx=(0, 8))
        self.add_button = ttk.Button(
            add_frame,
            command=self.add_inventory_item,
            style="Save.TButton",
            state="disabled",
        )
        self._text(self.add_button, "add")
        self.add_button.grid(row=0, column=3)

    def _add_group(self, parent: ttk.LabelFrame, title_key: str, labels: tuple[str, str, str], grid: tuple[int, int]) -> None:
        group = ttk.LabelFrame(parent, padding=8)
        self._text(group, title_key)
        group.grid(row=grid[0], column=grid[1], columnspan=6, sticky="ew", pady=(0, 8))
        for col, label in enumerate(labels):
            ttk.Label(group, text=label).grid(row=0, column=col * 2, sticky="w", padx=(0, 5))
            var = tk.StringVar()
            self.fields[label] = var
            ttk.Entry(group, textvariable=var, width=15).grid(row=0, column=col * 2 + 1, sticky="ew", padx=(0, 12))
            group.columnconfigure(col * 2 + 1, weight=1)

    def _add_time_field(self, parent: ttk.LabelFrame) -> None:
        group = ttk.LabelFrame(parent, padding=8)
        self._text(group, "playtime")
        group.grid(row=2, column=0, columnspan=6, sticky="ew")
        self._text(ttk.Label(group), "hours_since_start").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.fields["hours"] = tk.StringVar()
        ttk.Entry(group, textvariable=self.fields["hours"], width=18).grid(row=0, column=1, sticky="w")

    def choose_directory(self) -> None:
        selected = filedialog.askdirectory(
            title=self.t("folder_dialog"),
            initialdir=self.directory.get() if Path(self.directory.get()).exists() else str(Path.home()),
        )
        if selected:
            self.directory.set(selected)
            self.refresh_saves()

    def refresh_saves(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        folder = Path(self.directory.get()).expanduser()
        if not folder.is_dir():
            self.record = None
            self.current_path = None
            self.inventory_document = None
            self.inventory_items = []
            self.meta_label.configure(text=self.t("folder_missing"))
            self.inventory_note.configure(text=self.t("folder_missing"))
            self.add_button.state(["disabled"])
            self.apply_count_button.state(["disabled"])
            self.remove_item_button.state(["disabled"])
            self.inventory_count_spin.state(["disabled"])
            self.inventory_path_label.configure(text=self.t("asset_path_none"))
            self.save_button.state(["disabled"])
            self.status.set(self.t("folder_missing_status", folder=folder))
            self.refresh_inventory_tree()
            return

        files = sorted(folder.glob("*_Data.sav"), key=lambda p: p.name.lower())
        for path in files:
            try:
                mod = datetime.fromtimestamp(path.stat().st_mtime).strftime("%d.%m.%Y %H:%M")
                name = self._slot_label(path)
                self.tree.insert("", "end", iid=str(path), values=(name, mod))
            except OSError:
                continue
        self.status.set(
            self.t("saves_found_one")
            if len(files) == 1
            else self.t("saves_found_many", count=len(files))
            if files
            else self.t("no_saves")
        )
        self.record = None
        self.current_path = None
        self.inventory_document = None
        self.inventory_items = []
        self.meta_label.configure(text=self.t("choose_save_meta"))
        self.inventory_note.configure(text=self.t("choose_supported_save"))
        self.add_button.state(["disabled"])
        self.apply_count_button.state(["disabled"])
        self.remove_item_button.state(["disabled"])
        self.inventory_count_spin.state(["disabled"])
        self.inventory_path_label.configure(text=self.t("asset_path_none"))
        self.save_button.state(["disabled"])
        for var in self.fields.values():
            var.set("")
        self.refresh_inventory_tree()

    def on_select(self, _event: object = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        path = Path(selection[0])
        try:
            record = parse_save(path)
        except (OSError, SaveFormatError) as exc:
            self.record = None
            self.current_path = None
            self.inventory_document = None
            self.inventory_items = []
            error_text = str(exc) if isinstance(exc, OSError) else self._localized_error(exc)
            self.meta_label.configure(text=self.t("unsupported_file", error=error_text))
            self.inventory_note.configure(text=error_text)
            self.add_button.state(["disabled"])
            self.apply_count_button.state(["disabled"])
            self.remove_item_button.state(["disabled"])
            self.inventory_count_spin.state(["disabled"])
            self.inventory_path_label.configure(text=self.t("asset_path_none"))
            self.save_button.state(["disabled"])
            self.status.set(self.t("unsupported_save"))
            self.refresh_inventory_tree()
            return

        self.record = record
        self.current_path = path
        for label, offset in zip(("X", "Y", "Z"), record.location_offsets):
            self.fields[label].set(f"{struct.unpack_from('<d', record.source_bytes, offset)[0]:.3f}")
        for label, offset in zip(("Pitch", "Yaw", "Roll"), record.rotation_offsets):
            self.fields[label].set(f"{struct.unpack_from('<d', record.source_bytes, offset)[0]:.3f}")
        ticks = struct.unpack_from("<q", record.source_bytes, record.time_offset)[0]
        self.fields["hours"].set(f"{ticks / TICKS_PER_HOUR:.6f}")

        self._update_meta_label()
        self.load_inventory(record)
        self.save_button.state(["!disabled"])
        self.status.set(self.t("status_loaded"))

    def load_inventory(self, record: SaveRecord) -> None:
        self.inventory_document = record.inventory
        self.inventory_items = copy.deepcopy(record.inventory.items) if record.inventory else []
        self.catalog = load_item_catalog([item.asset_path for item in self.inventory_items], self.language_code)
        self.catalog_by_label = {option.label: option.asset_path for option in self.catalog}
        self.add_combo.configure(values=[option.label for option in self.catalog])
        if self.catalog:
            self.add_combo.current(0)

        if record.inventory is None:
            self._update_inventory_note()
            self.add_button.state(["disabled"])
        else:
            self._update_inventory_note()
            self.add_button.state(["!disabled"] if self.catalog and self.inventory_items else ["disabled"])
        self.inventory_count_var.set("1")
        self.inventory_path_label.configure(text=self.t("asset_path_none"))
        self.apply_count_button.state(["disabled"])
        self.remove_item_button.state(["disabled"])
        self.inventory_count_spin.state(["disabled"])
        self.refresh_inventory_tree()

    def refresh_inventory_tree(self, select_index: int | None = None) -> None:
        if not hasattr(self, "inventory_tree"):
            return
        for child in self.inventory_tree.get_children():
            self.inventory_tree.delete(child)
        for index, item in enumerate(self.inventory_items):
            count_display = str(item.count) if item.count is not None else self.t("single_item")
            durability = "—" if item.durability is None else f"{item.durability:.2f}"
            charge = "—" if item.charge is None else f"{item.charge:.2f}"
            self.inventory_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(asset_label(item.asset_path), count_display, durability, charge),
            )
        if select_index is not None and 0 <= select_index < len(self.inventory_items):
            iid = str(select_index)
            self.inventory_tree.selection_set(iid)
            self.inventory_tree.focus(iid)
            self.inventory_tree.see(iid)

    def on_inventory_select(self, _event: object = None) -> None:
        selection = self.inventory_tree.selection()
        if not selection or not self.inventory_document:
            return
        index = int(selection[0])
        item = self.inventory_items[index]
        self.inventory_path_label.configure(text=self.t("asset_path", path=item.asset_path))
        if item.count is None:
            self.inventory_count_var.set("1")
            self.inventory_count_spin.state(["disabled"])
            self.apply_count_button.state(["disabled"])
        else:
            self.inventory_count_var.set(str(item.count))
            self.inventory_count_spin.state(["!disabled"])
            self.apply_count_button.state(["!disabled"])
        self.remove_item_button.state(["!disabled"])

    def apply_inventory_count(self) -> None:
        selection = self.inventory_tree.selection()
        if not selection:
            return
        index = int(selection[0])
        item = self.inventory_items[index]
        if item.count_offset is None:
            return
        try:
            count = int(self.inventory_count_var.get().strip())
        except ValueError:
            messagebox.showerror(self.t("invalid_quantity_title"), self.t("quantity_whole"), parent=self.root)
            return
        if count < 1 or count > MAX_STACK_COUNT:
            messagebox.showerror(
                self.t("invalid_quantity_title"),
                self.t("quantity_range", maximum=MAX_STACK_COUNT),
                parent=self.root,
            )
            return
        self.inventory_items[index] = update_inventory_count(item, count)
        self.refresh_inventory_tree(index)
        self.status.set(self.t("status_quantity_set", item=asset_label(item.asset_path), count=count))

    def remove_inventory_item(self) -> None:
        selection = self.inventory_tree.selection()
        if not selection:
            return
        index = int(selection[0])
        removed = self.inventory_items.pop(index)
        next_index = min(index, len(self.inventory_items) - 1)
        self.refresh_inventory_tree(next_index if next_index >= 0 else None)
        self.remove_item_button.state(["disabled"])
        self.apply_count_button.state(["disabled"])
        self.inventory_count_spin.state(["disabled"])
        self.inventory_path_label.configure(text=self.t("asset_path_none"))
        self.status.set(self.t("status_item_removed", item=asset_label(removed.asset_path)))

    def _parse_add_count(self) -> int:
        try:
            count = int(self.add_count_var.get().strip())
        except ValueError as exc:
            raise ValueError(self.t("quantity_whole")) from exc
        if count < 1 or count > MAX_STACK_COUNT:
            raise ValueError(self.t("quantity_range", maximum=MAX_STACK_COUNT))
        return count

    def _choose_inventory_template(self, asset_path: str, quantity: int) -> InventoryItem:
        if not self.inventory_items:
            raise SaveFormatError(self.t("error_no_template"))
        category = asset_category(asset_path)
        same_category = [item for item in self.inventory_items if asset_category(item.asset_path) == category]
        stackable = [item for item in same_category if item.count_offset is not None]
        if quantity > 1:
            candidates = stackable or [item for item in self.inventory_items if item.count_offset is not None]
            if not candidates:
                raise SaveFormatError(self.t("error_no_stackable_template"))
            return candidates[0]
        if same_category:
            return same_category[0]
        with_count = [item for item in self.inventory_items if item.count_offset is not None]
        return with_count[0] if with_count else self.inventory_items[0]

    def add_inventory_item(self) -> None:
        if self.inventory_document is None:
            return
        label = self.add_combo.get()
        asset_path = self.catalog_by_label.get(label)
        if not asset_path:
            messagebox.showerror(self.t("error_item_title"), self.t("error_choose_item"), parent=self.root)
            return
        try:
            quantity = self._parse_add_count()
            template = self._choose_inventory_template(asset_path, quantity)
            if quantity > 1 and template.count_offset is None:
                raise SaveFormatError(self.t("error_no_stackable_template"))
            sort_indexes = [item.sort_index for item in self.inventory_items if item.sort_index is not None]
            new_sort_index = max(sort_indexes, default=-1) + 1
            new_item = clone_inventory_item(template, asset_path, quantity, new_sort_index)
        except (ValueError, SaveFormatError, struct.error) as exc:
            messagebox.showerror(self.t("error_add_title"), self._localized_error(exc), parent=self.root)
            return

        self.inventory_items.append(new_item)
        self.refresh_inventory_tree(len(self.inventory_items) - 1)
        self.on_inventory_select()
        self.status.set(self.t("status_item_added", item=asset_label(asset_path)))

    def reload_selected(self) -> None:
        if self.current_path is None:
            return
        self.on_select()
        self.status.set(self.t("status_reloaded"))

    def _numeric_values(self) -> tuple[list[float], float]:
        values: list[float] = []
        for label in ("X", "Y", "Z", "Pitch", "Yaw", "Roll"):
            raw = self.fields[label].get().strip().replace(",", ".")
            try:
                value = float(raw)
            except ValueError as exc:
                raise ValueError(self.t("number_required", field=label)) from exc
            if not math.isfinite(value):
                raise ValueError(self.t("finite_required", field=label))
            if label in ("X", "Y", "Z") and abs(value) > MAX_COORDINATE:
                raise ValueError(self.t("coordinate_range", field=label))
            values.append(value)
        hours_raw = self.fields["hours"].get().strip().replace(",", ".")
        try:
            hours = float(hours_raw)
        except ValueError as exc:
            raise ValueError(self.t("hours_number")) from exc
        if not math.isfinite(hours) or hours < 0 or hours > 1_000_000:
            raise ValueError(self.t("hours_range"))
        return values, hours

    def save_changes(self) -> None:
        if self.record is None or self.current_path is None:
            return

        selection = self.inventory_tree.selection()
        if selection:
            selected_index = int(selection[0])
            selected_item = self.inventory_items[selected_index]
            if selected_item.count_offset is not None:
                try:
                    pending_count = int(self.inventory_count_var.get().strip())
                except ValueError:
                    messagebox.showerror(self.t("invalid_quantity_title"), self.t("quantity_whole"), parent=self.root)
                    return
                if pending_count < 1 or pending_count > MAX_STACK_COUNT:
                    messagebox.showerror(
                        self.t("invalid_quantity_title"),
                        self.t("quantity_range", maximum=MAX_STACK_COUNT),
                        parent=self.root,
                    )
                    return
                self.inventory_items[selected_index] = update_inventory_count(selected_item, pending_count)

        try:
            values, hours = self._numeric_values()
        except ValueError as exc:
            messagebox.showerror(self.t("invalid_input_title"), str(exc), parent=self.root)
            return

        try:
            current = self.current_path.read_bytes()
        except OSError as exc:
            messagebox.showerror(
                self.t("read_error_title"),
                self.t("read_error", error=exc),
                parent=self.root,
            )
            return
        if hashlib.sha256(current).hexdigest() != self.record.source_hash:
            messagebox.showwarning(
                self.t("save_changed_title"),
                self.t("save_changed"),
                parent=self.root,
            )
            return

        edited = bytearray(self.record.source_bytes)
        for offset, value in zip(self.record.location_offsets, values[:3]):
            struct.pack_into("<d", edited, offset, value)
        for offset, value in zip(self.record.rotation_offsets, values[3:]):
            struct.pack_into("<d", edited, offset, value)
        ticks = round(hours * TICKS_PER_HOUR)
        struct.pack_into("<q", edited, self.record.time_offset, ticks)

        try:
            if self.inventory_document is not None:
                edited = bytearray(write_inventory(bytes(edited), self.inventory_document, self.inventory_items))
        except (SaveFormatError, struct.error) as exc:
            messagebox.showerror(
                self.t("inventory_save_error_title"),
                self._localized_error(exc),
                parent=self.root,
            )
            return

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = self.current_path.with_name(self.current_path.name + f".bak-{stamp}")
        temp_path: Path | None = None
        try:
            shutil.copy2(self.current_path, backup)
            fd, temp_name = tempfile.mkstemp(
                prefix=self.current_path.name + ".",
                suffix=".tmp",
                dir=self.current_path.parent,
            )
            temp_path = Path(temp_name)
            with os.fdopen(fd, "wb") as output:
                output.write(edited)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temp_path, self.current_path)
        except OSError as exc:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass
            messagebox.showerror(
                self.t("save_error_title"),
                self.t("save_error", error=exc),
                parent=self.root,
            )
            return

        self.on_select()
        self.status.set(self.t("saved_status", backup=backup.name))
        messagebox.showinfo(
            self.t("saved_title"),
            self.t("saved_message", backup=backup),
            parent=self.root,
        )


def main() -> None:
    root = tk.Tk()
    BreathedgeSaveEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
