from typing import Callable
from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.widget.filebrowser import FileBrowserItem
from typing import List
import omni.ui as ui
import os


def on_filter_item(dialog: FilePickerDialog, item: FileBrowserItem, exts: List) -> bool:
    if not item or item.is_folder:
        return True
    if dialog.current_filter_option == 0:
        # Show only files with listed extensions
        _, ext = os.path.splitext(item.path)
        return ext in exts
    return True


def build_fn():
    with ui.CollapsableFrame("Reference Options"):
        with ui.HStack(height=0, spacing=2):
            ui.Label("Prim Path", width=0)
    return True


def click_open_json_startup(dialog: FilePickerDialog, filename: str, dirname: str):
    selections = dialog.get_current_selections()
    dialog.hide()
    dirname = dirname.strip()
    if dirname and not dirname.endswith("/"):
        dirname += "/"

    fullpath = f"{dirname}{filename}"
    return selections, fullpath


def open_file_dialog(callback_fn: Callable, extension: str):
    if extension == "json":
        title = "Json Filepicker"
        item_filters = [".json"]
        item_filter_options_description = ["JSON Files (*.json)"]

    elif extension == "ply":
        title = "PLY Filepicker"
        item_filters = [".ply"]
        item_filter_options_description = ["PLY Files (*.ply)"]

    else:
        title = "Filepicker"
        item_filters = []
        item_filter_options_description = ["Empty (*)"]

    dialog = FilePickerDialog(
        title,
        apply_button_label="Open",
        click_apply_handler=lambda filename, dirname: callback_fn(dialog, filename, dirname),
        item_filter_options=item_filter_options_description,
        item_filter_fn=lambda item: on_filter_item(dialog, item, item_filters),
        build_fn=build_fn,
    )
    dialog.show()
