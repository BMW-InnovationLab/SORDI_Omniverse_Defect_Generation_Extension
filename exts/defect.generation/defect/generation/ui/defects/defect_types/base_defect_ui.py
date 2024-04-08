import omni.ui as ui
from defect.generation.ui.widgets import MinMaxWidget, CustomDirectory, PathWidget
from defect.generation.utils.helpers import *
from pxr import Sdf
from pathlib import Path
import omni.kit.notification_manager as nm



class BaseDefectUI:
    def __init__(self) -> None:
        pass
            
    def prepare_defect_args(self):
        pass
    
    @property
    def defect_name(self) -> str:
        pass

    # Set function which updates UI after adding a new defect row
    def on_add(self,fn):
        self.update_ui = fn


    def set_defect_parameters_list(self, defect_parameters_list):
        self.defect_parameters_list = defect_parameters_list

    def add_new_defect_row(self):
        self.defect_parameters_list.append({
            "uuid": generate_small_uuid(),
            "defect_name": self.defect_name,
            "args": self.prepare_defect_args()
        })
        # Call function which updates UI after adding a new defect row
        self.update_ui()

    def add_new_defect_row_based_on_input(self, defect_name, args):
        self.defect_parameters_list.append({
            "uuid": generate_small_uuid(),
            "defect_name": self.defect_name,
            "args": args
        })
        # Call function which updates UI after adding a new defect row
        self.update_ui()

    def _build_base_ui(self):
        self.semantic_label = ui.SimpleStringModel(self.defect_name)
        self.count = ui.SimpleIntModel(1)
        with ui.HStack():
            ui.Spacer(width=13)
            ui.Button("+", clicked_fn=self.add_new_defect_row)
        self._build_semantic_label()

    def _build_semantic_label(self):
        with ui.HStack(height=0, tooltip="The label that will be associated with the defect"):
            ui.Label("Defect Semantic")
            ui.StringField(model=self.semantic_label)
    
    def destroy(self):
        self.semantic_label = None
        self.dim_w.destroy()
        self.dim_w = None
        self.dim_h.destroy()
        self.dim_h = None
        self.rot.destroy()
        self.rot = None