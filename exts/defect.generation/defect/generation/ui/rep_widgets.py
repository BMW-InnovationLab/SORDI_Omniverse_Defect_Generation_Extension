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
from defect.generation.ui.widgets import MinMaxWidget, CustomDirectory, PathWidget
from defect.generation.utils.helpers import *
from pxr import Sdf
from pathlib import Path
import omni.kit.notification_manager as nm

TEXTURE_DIR = Path(__file__).parent / "data"
SCRATCHES_DIR = TEXTURE_DIR / "scratches" 

# Parameter Objects

class ObjectParameters():
    def __init__(self) -> None:
        self.target_prim = PathWidget("Target Prim")

        def apply_primvars(prim):
            # Apply prim vars
            prim.CreateAttribute('primvars:d1_forward_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_right_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_up_vector', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:d1_position', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            prim.CreateAttribute('primvars:v3_scale', Sdf.ValueTypeNames.Float3, custom=True).Set((0,0,0))
            nm.post_notification(f"Applied Primvars to: {prim.GetPath()}", hide_after_timeout=True, duration=5, status=nm.NotificationStatus.INFO)

        def apply():
            # Check Paths
            if not check_path(self.target_prim.path_value):
                return 
            
            # Check if prim is valid
            prim = is_valid_prim(self.target_prim.path_value)
            if prim is None:
                return
    
            apply_primvars(prim)
        
        ui.Button("Apply",  
            style={"padding": 5}, 
            clicked_fn=lambda: apply(), 
            tooltip="Apply Primvars and Material to selected Prim."
        )

    def destroy(self):
        self.target_prim.destroy()
        self.target_prim = None

class MaterialParameters():
    def __init__(self) -> None:
        pass