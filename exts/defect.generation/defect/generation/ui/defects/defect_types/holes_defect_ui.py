import omni.ui as ui
from defect.generation.ui.widgets import MinMaxWidget
from defect.generation.ui.defects.defect_types.base_defect_ui import BaseDefectUI



class HolesUI(BaseDefectUI):
    def __init__(self) -> None:
        super().__init__()
        self._count_model = ui.SimpleIntModel(1)
    def prepare_defect_args(self):
        return {"dim_w_min": self.radius.min_value,
                "dim_w_max": self.radius.max_value,
                "dim_h_min": self.radius.min_value,
                "dim_h_max": self.radius.max_value,
                "rot_x_min": self.rot_x.min_value,
                "rot_x_max": self.rot_x.max_value,
                "rot_y_min": self.rot_y.min_value,
                "rot_y_max": self.rot_y.max_value,
                "rot_z_min": self.rot_z.min_value,
                "rot_z_max": self.rot_z.max_value,
                "semantic_label": self.semantic_label.as_string,
                "count": self._count_model.as_int}
    
    def build_ui(self):
        self._build_base_ui()
        self.radius = MinMaxWidget("Defect Radius",
                                  min_value=0.1,
                                  tooltip="Defining the Minimum and Maximum Radius of the Defect")
        self.rot_x = MinMaxWidget("Defect Rotation X", min_value=0, max_value=360,
                                tooltip="Defining the Minimum and Maximum X-Rotation of the Defect")

        self.rot_y = MinMaxWidget("Defect Rotation Y", min_value=0, max_value=360,
                        tooltip="Defining the Minimum and Maximum Y-Rotation of the Defect")
        
        self.rot_z = MinMaxWidget("Defect Rotation Z", min_value=0, max_value=360,
                                tooltip="Defining the Minimum and Maximum Z-Rotation of the Defect")
        
        with ui.HStack(height=0, tooltip="Number of defects to generate"):
            with ui.HStack():
                ui.Label("Count", width=0)
                ui.IntDrag(model=self._count_model)
    @property
    def defect_name(self) -> str:
        return 'hole'
        
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