import omni.ui as ui
from defect.generation.ui.widgets import MinMaxWidget, CustomDirectory, PathWidget
from defect.generation.ui.defects.defect_types.base_defect_ui import BaseDefectUI
from defect.generation.utils.helpers import *
from pxr import Sdf
from pathlib import Path
import omni.kit.notification_manager as nm



class ScratchesUI(BaseDefectUI):
    def __init__(self) -> None:
        super().__init__()
        self._count_model = ui.SimpleIntModel(1)
    def prepare_defect_args(self):
        return {"dim_w_min": self.dim_w.min_value,
                "dim_w_max": self.dim_w.max_value,
                "dim_h_min": self.dim_h.min_value,
                "dim_h_max": self.dim_h.max_value,
                "rot_min": self.rot.min_value,
                "rot_max": self.rot.max_value,
                "semantic_label": self.semantic_label.as_string,
                "count": self._count_model.as_int}
    
    def build_ui(self):
        self._build_base_ui()
        self.dim_w = MinMaxWidget("Defect Dimensions Width",
                                  min_value=0.1,
                                  tooltip="Defining the Minimum and Maximum Width of the Defect")
        self.dim_h = MinMaxWidget("Defect Dimensions Length",
                                  min_value=0.1,
                                  tooltip="Defining the Minimum and Maximum Length of the Defect")

        self.rot = MinMaxWidget("Defect Rotation", 
                                tooltip="Defining the Minimum and Maximum Rotation of the Defect")

        with ui.HStack(height=0, tooltip="Number of defects to generate"):
            with ui.HStack():
                ui.Label("Count", width=0)
                ui.IntDrag(model=self._count_model)
    @property
    def defect_name(self) -> str:
        return 'scratch'
        
    def destroy(self):
        self.semantic_label = None
        self.defect_text.destroy()
        self.defect_text = None
        self.dim_w.destroy()
        self.dim_w = None
        self.dim_h.destroy()
        self.dim_h = None
        self.rot.destroy()
        self.rot = None