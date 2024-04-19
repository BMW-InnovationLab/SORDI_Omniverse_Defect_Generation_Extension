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
from defect.generation.ui.widgets import PathWidget
from defect.generation.utils.helpers import *
from pxr import Sdf
import omni.kit.notification_manager as nm


# Target Prim
class ObjectParameters():
    def __init__(self, defect_parameters_list = None):
        self.defect_parameters_list = defect_parameters_list
        self.current_selected_prim = ui.SimpleStringModel()
        self.target_prim = None

    @property
    def current_selected_prim_value(self) -> str:
        """
        Path of the target Prim in the scene

        :type: str
        """
        return self.current_selected_prim.get_value_as_string()
    


    def set_current_selected_prim(self, value) -> None:
        self.current_selected_prim.set_value(value)

    def on_add(self, fn):
        self.update_ui = fn

    def build_ui(self):
        #creates empty _build
        self.target_prim = PathWidget("Target Prim")

        def _apply_primvars(prim):
            # Apply prim vars
            prim.CreateAttribute('primvars:d1_forward_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_right_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_up_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_position', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:v3_scale', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            nm.post_notification(f"Applied Primvars to: {prim.GetPath()}", hide_after_timeout=True, duration=5, status=nm.NotificationStatus.INFO)

        def _apply():
            prim_path = self.target_prim.path_value

            if not check_path(prim_path):
                return 
            
            # Check if prim is valid
            prim = is_valid_prim(prim_path)
            if prim is None:
                return
            
            _apply_primvars(get_prim(prim_path))
            self.apply_on_new_path()

        ui.Button("Apply",  
            style={"padding": 5}, 
            clicked_fn=lambda: _apply(), 
            tooltip="Apply Primvars and Material to selected Prim."
        )

        with ui.HStack():
            ui.Label(f"Current target prim")
            ui.StringField(model=self.current_selected_prim, read_only=True)
    def apply_on_new_path(self): 
        self.defect_parameters_list[self.target_prim.path_value] = []
        self.set_current_selected_prim(self.target_prim.path_value)
        self.update_ui()

    def destroy(self):
        self.target_prim.destroy()
        self.target_prim = None

class MaterialParameters():
    def __init__(self) -> None:
        pass