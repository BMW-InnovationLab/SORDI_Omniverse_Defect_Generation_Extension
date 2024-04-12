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

import carb
from typing import List
import json
import omni.ui as ui
from omni.ui import DockPreference
from omni.kit.window.file_exporter import get_file_exporter
from omni.kit.window.filepicker import FilePickerDialog
from defect.generation.ui.style import *
from defect.generation.ui.widgets import CustomDirectory
from defect.generation.core.replicator_defect import create_defect_layer
from defect.generation.utils.replicator_utils import rep_preview, does_defect_layer_exist, rep_run, get_defect_layer
from defect.generation.ui.rep_widgets import ObjectParameters
from defect.generation.ui.defects.defect_types_factory import DefectUIFactory
from defect.generation.utils.helpers import *
from defect.generation.utils.file_picker import open_file_dialog, click_open_json_startup
from defect.generation.domain.models.defect_generation_request import DefectGenerationRequest, DefectObject
from pathlib import Path
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Get delete Icon
@lru_cache()
def _ui_get_delete_glyph():
    return omni.ui.get_custom_glyph_code("${glyphs}/menu_delete.svg")

# Get Folder Icon
@lru_cache()
def _ui_get_open_folder_glyph():
    return ui.get_custom_glyph_code("${glyphs}/folder_open.svg")

class MainWindow(ui.Window):
    def __init__(self, title: str, dockPreference: DockPreference = DockPreference.DISABLED, **kwargs) -> None:
        super().__init__(title, dockPreference, **kwargs)
        # Models
        self.frames = ui.SimpleIntModel(1, min=1)
        self.rt_subframes = ui.SimpleIntModel(1, min=1)
        # Widgets
        self.defect_params = None
        self.object_params = None
        self.output_dir = None
        self.frame_change = None
        # Defects UI
        self.defect_ui_factory = DefectUIFactory()
        self.defect_methods_ui = self.defect_ui_factory.get_all_defect_method_ui()
        self.defect_methods_ui = sorted(self.defect_methods_ui, key=lambda x: x.defect_name)

        # List that stores all the defect parameters to be applied
        self.defect_parameters_list = []


        self.frame.set_build_fn(self._build_frame)
    
    # Function to update the UI of the list of appended defect methods
    def update_defect_parameters_list_ui(self):

        # Clear the UI of the appended defect methods
        self.defect_parameters_list_ui.clear()

        with self.defect_parameters_list_ui:
            with ui.HStack(spacing=2):
                ui.Label("Defect Name", width=150)
                ui.Label("Args", width=150)

            with ui.HStack():
                ui.Line(height=ui.Length(20))

            # Loop over each appended defect method, and format the content in the UI
            for i, defect in enumerate(self.defect_parameters_list):

                args_formatted = []
                for k, v in defect["args"].items():
                    args_formatted.append(f"{k}: {v}" if not isinstance(v,float) else f"{k}: {v:.2f}")
                args_formatted = '\n'.join(args_formatted)

                with ui.HStack(spacing=2):
                    ui.Label(defect["defect_name"], width=150, word_wrap=True, style={"color": 0xFF777777})
                    ui.Label(args_formatted, word_wrap=True, style={"color": 0xFF777777})
                    ui.Button(
                        f"{_ui_get_delete_glyph()}",
                        width=20,
                        clicked_fn=lambda idx=i: self.delete_dm(idx),
                        tooltip="Remove entry",
                    )
                with ui.HStack():
                    ui.Line(height = 10)
    # Function to be called when the delete defect method icon is pressed
    def delete_dm(self, idx):
        logger.warning(idx)
        del self.defect_parameters_list[idx]

        # After updating the list, re-update the UI
        self.update_defect_parameters_list_ui()
    
    # Export  defect methods logic
    def _export_dm_handler(self, filename: str, dirname: str, extension: str, selections: List[str]):
        try:
            full_path = os.path.join(dirname, f"{filename}{extension}")

            if self.defect_parameters_list:
                with open(full_path, 'w') as defect_file:
                    json.dump(self.defect_parameters_list, defect_file)
                logger.info(f"Exported defect data to '{full_path}'")

        except Exception as e:
            logger.error(f"Error exporting defect methods: {e}")
    # Open export defect methods dialog
    def open_export_dm_dialog(self):

        file_exporter = get_file_exporter()
        file_exporter.show_window(
            title="Export As ...",
            export_button_label="Save",
            export_handler=self._export_dm_handler,
            filename_url="defect_methods.json",  # Default filename
            file_extension_types=[(".json", "JSON Files")]
        )
    # Load defect methods 
    def load_defect(self):
        def _set_defects(defect):
            self.defect_parameters_list.clear()

            for defect_method in defect:
                defect_name = defect_method.get("defect_name")
                args = defect_method.get("args")

                defect_ui = self.defect_ui_factory.get_defect_method_ui(defect_name)
                defect_ui.add_new_defect_row_based_on_input(defect_name=defect_name, args=args)

            self.update_defect_parameters_list_ui()

        logger.info(f"Defect data: {self.defect_parameters_list}")
        def _validate_json_structure(data):
            for item in data:
                if not all(key in item for key in ('defect_name','args')):
                    raise ValueError(
                        "Invalid JSON structure. Each dictionary must have 'defect_name and 'args' keys.")

        defect_path = self.defect_path.model.get_value_as_string()
        with open(defect_path, 'r') as file:
            defect = json.load(file)
            # Validate the JSON structure
            try:
                _validate_json_structure(defect)
                logger.info("JSON structure is valid.")
                _set_defects(defect)
                self.info_defect.text = f"{len(defect)} defects"
            except ValueError as e:
                logger.error("Invalid JSON structure:", e)
    



    ###############################
    # UI
    ###############################
    def _build_collapse_base(self, label: str, collapsed: bool = False):
        v_stack = None
        with ui.CollapsableFrame(label, height=0, collapsed=collapsed):
            with ui.ZStack():
                ui.Rectangle()
                v_stack = ui.VStack()
        return v_stack

    def _build_frame(self):
        with self.frame:
            with ui.ScrollingFrame(style=default_defect_main):
                with ui.VStack(style={"margin": 3}):
                    self._build_object_param()               
                    self._build_defect_param()
                    self._build_replicator_param()

    def _build_object_param(self):
        with self._build_collapse_base("Object Parameters"):
            self.object_params = ObjectParameters()

    def _build_defect_param(self):
        def on_click_open_defect(dialog: FilePickerDialog, filename: str, dirname: str):
            _, fullpath = click_open_json_startup(dialog, filename, dirname)
            self.defect_path.model.set_value(fullpath)

        def click_open_file_dialog_defect():
            open_file_dialog(on_click_open_defect, "json")





        with self._build_collapse_base("Defect Parameters"):

            #TODO: Move to separate widget
            TEXTURE_DIR = os.path.join(Path(__file__).parent,"data")
            self.defect_text = CustomDirectory("Defect Texture Folder",
                                        default_dir=str(TEXTURE_DIR),
                                        tooltip="A folder location containing a single or set of textures (.png)",
                                        file_types=[("*.png", "PNG"), ("*", "All Files")])

            for defect_method_ui in self.defect_methods_ui:
                # Preparing defect method UIs
                defect_method_ui.set_defect_parameters_list(self.defect_parameters_list)
                defect_method_ui.on_add(self.update_defect_parameters_list_ui)
                with ui.CollapsableFrame(defect_method_ui.defect_name, height=0) as frame:
                    with ui.Frame():
                        with ui.VStack():
                            logger.info(f"Building ui: {defect_method_ui.defect_name}")
                            defect_method_ui.build_ui()

            with self._build_collapse_base("Params"):
                self.defect_parameters_list_ui = ui.VStack(spacing=5)
                with ui.Frame():
                    with self.defect_parameters_list_ui:
                        with ui.HStack(spacing=2):
                            ui.Label("Defect Name", width=150)
                            ui.Label("Args", width=200)

                        with ui.HStack():
                            ui.Line(height=ui.Length(20))
            with ui.Frame():
                with ui.VStack():
                    with ui.HStack(spacing=5):
                        ui.Spacer(width=13)
                        ui.Label("Defect JSON file", width=100)
                        self.defect_path = ui.StringField()
                        ui.Button("Browse", clicked_fn=click_open_file_dialog_defect)
                        ui.Button("Load", clicked_fn=self.load_defect)
                        ui.Button(
                            f"{_ui_get_open_folder_glyph()}",
                            width=20,
                            clicked_fn=lambda: open_file_using_os_default(self.defect_path.model.get_value_as_string()),
                            tooltip="Open defects",
                        )
                        ui.Spacer(width=25)
                        self.info_defect = ui.Label("", style={"color": ui.color(255, 255, 0)})
                    with ui.HStack(spacing=5):
                        ui.Button("Export Defect Methods", clicked_fn=lambda: self.open_export_dm_dialog())
    
    def _build_replicator_param(self):
        def _create_defect_layer(*args):
            req = DefectGenerationRequest(
                        prims_path=[self.object_params.target_prim.path_value],
                        texture_dir=self.defect_text.directory,
                        defects = [DefectObject(defect_name=d['defect_name'], args=d['args'], uuid=d['uuid']) for d in self.defect_parameters_list]
                    )
            create_defect_layer(req, *args)

        def preview_data():
            if does_defect_layer_exist():
                rep_preview()
            else:
                _create_defect_layer()
                self.rep_layer_button.text = "Recreate Replicator Graph"
        
        def remove_replicator_graph():
            if get_defect_layer() is not None:
                layer, pos = get_defect_layer()
                omni.kit.commands.execute('RemoveSublayer',
                    layer_identifier=layer.identifier,
                    sublayer_position=pos)
                if is_valid_prim('/World/Looks'):
                    delete_prim('/World/Looks')
                if is_valid_prim(self.object_params.target_prim.path_value + "/Projection"):
                    delete_prim(self.object_params.target_prim.path_value + "/Projection")
            if is_valid_prim('/Replicator'):
                delete_prim('/Replicator')

        def run_replicator():
            remove_replicator_graph()
            total_frames = self.frames.get_value_as_int()
            subframes = self.rt_subframes.get_value_as_int()
            if subframes <= 0:
                subframes = 0
            if total_frames > 0:
                _create_defect_layer(self.output_dir.directory, subframes, self._use_seg.as_bool, self._use_bb.as_bool)
                self.rep_layer_button.text = "Recreate Replicator Graph"
                rep_run()
            else:
                carb.log_error(f"Number of frames is {total_frames}. Input value needs to be greater than 0.")
        
        def create_replicator_graph():
            remove_replicator_graph()
            _create_defect_layer()
            self.rep_layer_button.text = "Recreate Replicator Graph"

        def set_text(label, model):
            label.text = model.as_string

        with self._build_collapse_base("Replicator Parameters"):
            home_dir = Path.home()
            valid_out_dir = home_dir / "omni.replicator_out"
            self.output_dir = CustomDirectory("Output Directory", default_dir=str(valid_out_dir.as_posix()), tooltip="Directory to specify where the output files will be stored. Default is [DRIVE/Users/USER/omni.replicator_out]")
            with ui.HStack(height=0, tooltip="Check off which annotator you want to use; You can also use both"):
                ui.Label("Annotations: ", width=0)
                ui.Spacer()
                ui.Label("Segmentation", width=0)
                self._use_seg = ui.CheckBox().model
                ui.Label("Bounding Box", width=0)
                self._use_bb = ui.CheckBox().model
                ui.Spacer()
            with ui.HStack(height=0):
                ui.Label("Render Subframe Count: ", width=0,
                         tooltip="Defines how many subframes of rendering occur before going to the next frame")
                ui.Spacer(width=ui.Fraction(0.25))
                ui.IntField(model=self.rt_subframes)
            self.rep_layer_button = ui.Button("Create Replicator Layer", 
                                              clicked_fn=lambda: create_replicator_graph(), 
                                              tooltip="Creates/Recreates the Replicator Graph, based on the current Defect Parameters")
            with ui.HStack(height=0):
                ui.Button("Preview", width=0, clicked_fn=lambda: preview_data(),
                          tooltip="Preview a Replicator Scene")
                ui.Label("or", width=0)
                ui.Button("Run for", width=0, clicked_fn=lambda: run_replicator(),
                          tooltip="Run replicator for so many frames")
            
                with ui.ZStack(width=0):
                    l = ui.Label("", style={"color": ui.color.transparent, "margin_width": 10})
                    self.frame_change = ui.StringField(model=self.frames)
                    self.frame_change_cb = self.frame_change.model.add_value_changed_fn(lambda m, l=l: set_text(l, m))
                ui.Label("frame(s)")

    ###############################
    # End UI
    ###############################

        
    def destroy(self) -> None:
        self.frames = None
        self.defect_semantic = None
        if self.frame_change is not None:
            self.frame_change.model.remove_value_changed_fn(self.frame_change_cb)
        if self.defect_params is not None:
            self.defect_params.destroy()
            self.defect_params = None
        if self.object_params is not None:
            self.object_params.destroy()
            self.object_params = None
        if self.defect_text is not None:
            self.defect_text.destroy()
            self.defect_text = None
        return super().destroy()
