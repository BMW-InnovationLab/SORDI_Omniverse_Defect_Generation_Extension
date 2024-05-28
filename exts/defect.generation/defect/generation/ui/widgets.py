# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import omni.ui as ui
import omni.kit.commands
from typing import List, Callable
import omni.usd
import asyncio
from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.notification_manager import post_notification, NotificationStatus

class CustomDirectory:
    def __init__(self, label: str, tooltip: str = "", default_dir: str = "") -> None:
        self._label_text = label
        self._tooltip = tooltip
        self._dir = ui.SimpleStringModel(default_dir)
        self._build_directory()

    @property
    def directory(self) -> str:
        """
        Selected Directory name from file importer

        :type: str
        """
        return self._dir.get_value_as_string()
    
    def _build_directory(self):
        with ui.HStack(height=0, tooltip=self._tooltip):
            ui.Label(self._label_text)
            ui.StringField(model=self._dir)
            ui.Button("Browse", width=0, style={"padding": 5}, clicked_fn=self.click_open_file_dialog_dir)

    
    def open_dir_dialog(self, callable_fn: Callable):
    
        def _on_selection_changed(items: List[FileBrowserItem]):
            if len(items) != 1:
                return False
            item = items[0]
            if not item.is_folder:
                return False
            else:
                dialog.set_filename(item.name)
        def _create_filepicker(
                title: str,
                filters: list = ["All Files (*)"],
                click_apply_fn: Callable = None,
                error_fn: Callable = None
        ) -> FilePickerDialog:
            async def on_click_handler(dirname: str, dialog: FilePickerDialog, click_fn: Callable):
                click_fn(dirname)
                dialog.hide()

            dialog = FilePickerDialog(
                title,
                allow_multi_selection=False,
                apply_button_label="Select",
                click_apply_handler=lambda filename, dirname: asyncio.ensure_future(on_click_handler(dirname, dialog, click_apply_fn)),
                click_cancel_handler=lambda filename, dirname: dialog.hide(),
                selection_changed_fn= _on_selection_changed,
                item_filter_options=filters,
                error_handler=error_fn)
            dialog.set_filebar_label_name("Folder name")
            dialog.set_current_directory(self.directory)
            dialog.hide()
            return dialog

        dialog = _create_filepicker(
            "Select Directory",
            click_apply_fn=lambda dirname: callable_fn(dialog, dirname),
        )
        dialog.show()
    def click_open_dir_startup(self, dialog: FilePickerDialog, dirname: str):
        selections = dialog.get_current_selections()
        dialog.hide()
        dirname = dirname.strip()
        if dirname and not dirname.endswith("/"):
            dirname += "/"

        return selections, dirname
    def click_open_file_dialog_dir(self):
        def on_click_open_dir(dialog: FilePickerDialog, dirname: str):
            _, fullpath = self.click_open_dir_startup(dialog, dirname)
            self._dir.set_value(fullpath)

        self.open_dir_dialog(on_click_open_dir)
        
    def destroy(self):
        self._dir = None


class MinMaxWidget:
    def __init__(self, label: str, min_value: float = 0, max_value: float = 1, tooltip: str = "") -> None:
        self._min_model = ui.SimpleFloatModel(min_value)
        self._max_model = ui.SimpleFloatModel(max_value)
        self._label_text = label
        self._tooltip = tooltip
        self._build_min_max()

    @property
    def min_value(self) -> float:
        """
        Min Value of the UI

        :type: float
        """
        if self._min_model.get_value_as_float() < 0:
            post_notification(
                f"Min Value: {self._min_model.get_value_as_float()} in {self._label_text} is less than 0. Setting it to 0.",
                duration=5,
                status=NotificationStatus.WARNING
            )
            self._min_model.set_value(0)
        return self._min_model.get_value_as_float()

    @property
    def max_value(self) -> float:
        """
        Max Value of the UI

        :type: float
        """
        if self._max_model.get_value_as_float() < self.min_value:
            post_notification(
                f"Max Value: {self._max_model.get_value_as_float()} is less than Min Value: {self.min_value} in label {self._label_text}. Setting the Max Value to Min Value.",
                duration=5,
                status=NotificationStatus.WARNING
            )
            self._max_model.set_value(self.min_value)
        return self._max_model.get_value_as_float()

    def _build_min_max(self):
        with ui.HStack(height=0, tooltip=self._tooltip):
            ui.Label(self._label_text)
            with ui.HStack():
                ui.Label("Min", width=0)
                ui.FloatDrag(model=self._min_model)
                ui.Label("Max", width=0)
                ui.FloatDrag(model=self._max_model)

    def destroy(self):
        self._max_model = None
        self._min_model = None


class PositionMinMaxWidget(MinMaxWidget):
    def __init__(self, label: str, min_value: float = 0, max_value: float = 1, tooltip: str = ""):
        super().__init__(label, min_value, max_value, tooltip)

    @property
    def min_value(self) -> float:
        """
        Min Value of the UI

        :type: float
        """
        return self._min_model.get_value_as_float()

    @property
    def max_value(self) -> float:
        """
        Max Value of the UI

        :type: float
        """
        if self._max_model.get_value_as_float() < self.min_value:
            post_notification(
                f"Max Value: {self._max_model.get_value_as_float()} is less than Min Value: {self.min_value} in label {self._label_text}. Setting the Max Value to Min Value.",
                duration=5,
                status=NotificationStatus.WARNING
            )
            self._max_model.set_value(self.min_value)
        return self._max_model.get_value_as_float()


class RGBMinMaxWidget:
    def __init__(self, label: str, min_r_value: float = 0, max_r_value: float = 1, min_g_value: float = 0, max_g_value: float = 1, min_b_value: float = 0, max_b_value: float = 1, tooltip: str = "") -> None:
        self._min_values = [min_r_value, min_g_value, min_b_value]
        self._max_values = [max_r_value, max_g_value, max_b_value]
        self._label_text = label
        self._tooltip = tooltip
        self._min_models = []
        self._max_models = []
        self._build_min_max()

    @property
    def min_values(self) -> List[float]:
        """
        Min Values of the UI

        :type: List[float]
        """
        for label , model in zip(["R", "G", "B"], self._min_models):
            if model.get_value_as_float() < 0:
                post_notification(
                    f"Min Value : {model.get_value_as_float()}, in Channel {label} is Less than 0, Setting it to 0",
                    duration=5,
                    status=NotificationStatus.WARNING
                )
                model.set_value(0)
        return [model.get_value_as_float() for model in self._min_models]
    
    @property 
    def max_values(self) -> List[float]:
        """
        Max Values of the UI

        :type: List[float]
        """
        labels = ["R", "G", "B"]
        for i in range(len(self._max_values)):
            if self._max_models[i].get_value_as_float() < self._min_models[i].get_value_as_float():
                post_notification(
                    f"Max Value: {self._max_models[i].get_value_as_float()} is less than Min Value: {self.min_values[i]} in Channel {labels[i]}. Setting the Max Value to Min Value.",
                    duration=5,
                    status=NotificationStatus.WARNING
                )
                self._max_models[i].set_value(self.min_values[i])
        return [model.get_value_as_float() for model in self._max_models]

    def _build_min_max(self):
            with ui.HStack(height=0, tooltip=self._tooltip):
                ui.Label(self._label_text)
                with ui.VStack(): 
                    with ui.HStack(spacing=7):
                        ui.Label("Min", width=0)
                        for label, min_value in zip(["R", "G", "B"], self._min_values):
                            ui.Label(label, width=0)
                            min_model = ui.SimpleFloatModel(min_value)
                            self._min_models.append(min_model)
                            ui.FloatDrag(model=min_model, min=0.0, max=2.0)
                    with ui.HStack(spacing=7):
                        ui.Label("Max", width=0)
                        for label, max_value in zip(["R", "G", "B"], self._max_values):
                            ui.Label(label, width=0)
                            max_model = ui.SimpleFloatModel(max_value)
                            self._max_models.append(max_model)
                            ui.FloatDrag(model=max_model, min=0.0, max=2.0)


    def destroy(self):
        self._min_models= None
        self._max_models= None


class PathWidget:
    def __init__(self, label: str, button_label: str = "Copy", read_only: bool = False, tooltip: str = "") -> None:
        self._label_text = label
        self._tooltip = tooltip
        self._button_label = button_label
        self._read_only = read_only
        self._path_model = ui.SimpleStringModel()
        self._top_stack = ui.HStack(height=0, tooltip=self._tooltip)
        self._button = None
        self.ctx = omni.usd.get_context()
        self._build()
    
    @property
    def path_value(self) -> str:
        """
        Path of the Prim in the scene

        :type: str
        """
        return self._path_model.get_value_as_string()
   
    @path_value.setter
    def path_value(self, value) -> None:
        """
        Sets the path value

        :type: str
        """
        self._path_model.set_value(value)


    def _build(self):
        def copy():
            selection = self.ctx.get_selection().get_selected_prim_paths()
            if len(selection) > 0:
                # If only one prim is selected
                if len(selection) == 1:
                    self._path_model.set_value(str(selection[0]))
                # If multiple prims are selected, move them under the same Xform group
                else: 
                    omni.kit.commands.execute('GroupPrims',
                        prim_paths=selection)
                    # Get group  name
                    grouped_prims_path = self.ctx.get_selection().get_selected_prim_paths()
                    self._path_model.set_value(str(grouped_prims_path[0]))
     
        with self._top_stack:
            ui.Label(self._label_text)
            ui.StringField(model=self._path_model, read_only=self._read_only)
            self._button = ui.Button(self._button_label, width=0, style={"padding": 5}, clicked_fn=lambda: copy(), tooltip="Copies the Current Selected Path in the Stage")
   

    def destroy(self):
        self._path_model = None
