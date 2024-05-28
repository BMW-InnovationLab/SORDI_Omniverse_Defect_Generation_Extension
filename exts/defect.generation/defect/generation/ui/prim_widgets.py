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
from defect.generation.utils.helpers import is_valid_prim, get_prim, check_path
from pxr import Sdf
from omni.kit.notification_manager import post_notification, NotificationStatus
import logging

logger = logging.getLogger(__name__)

# Target Prim
class ObjectParameters():
    def __init__(self, defect_parameters_list):
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

        ui.Button("Apply",  
            style={"padding": 5}, 
            clicked_fn=lambda: self.apply(self.target_prim.path_value), 
            tooltip="Apply Primvars and Material to selected Prim."
        )

        with ui.HStack():
            ui.Label(f"Current target prim")
            ui.StringField(model=self.current_selected_prim, read_only=True)

    def apply(self, target_prim_path):
        def _apply_primvars(prim):
            # Apply prim vars
            prim.CreateAttribute('primvars:d1_forward_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_right_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_up_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_position', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:v3_scale', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            post_notification(f"Applied Primvars to: {prim.GetPath()}", hide_after_timeout=True, duration=5, status=NotificationStatus.INFO)

        if not check_path(target_prim_path):
            post_notification(f"You Need to Choose at Least One Target Prim to Apply",hide_after_timeout=True, duration=5, status=NotificationStatus.WARNING)
            return 
        
        # Check if prim is valid
        prim = is_valid_prim(target_prim_path)
        if prim is None:
            post_notification(f"Please Select a Valid Prim to Apply Primvars on",hide_after_timeout=True, duration=5, status=NotificationStatus.WARNING)
            return


        
        _apply_primvars(get_prim(target_prim_path))
        self.apply_on_new_path(target_prim_path)




    def apply_on_new_path(self, target_prim_path): 
        if target_prim_path not in self.defect_parameters_list:
            self.defect_parameters_list[target_prim_path] = []
        self.set_current_selected_prim(target_prim_path)
        self.update_ui()

    def destroy(self):
        self.target_prim.destroy()
        self.target_prim = None
