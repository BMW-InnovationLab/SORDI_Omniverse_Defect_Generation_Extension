import omni.ui as ui
from defect.generation.ui.widgets import MinMaxWidget
from defect.generation.ui.defects.defect_types.base_defect_ui import BaseDefectUI


class ScratchesUI(BaseDefectUI):
    def __init__(self) -> None:
        super().__init__()

    def prepare_defect_args(self):
        common_args = {
            "dim_w_min": self.dim_w.min_value,
            "dim_w_max": self.dim_w.max_value,
            "dim_h_min": self.dim_h.min_value,
            "dim_h_max": self.dim_h.max_value,
            "rot_x_min": self.rot_x.min_value,
            "rot_x_max": self.rot_x.max_value,
            "semantic_label": self.semantic_label.as_string,
            "count": self.count.as_int,
        }

        if self.rotation_cb.get_value_as_bool():
            common_args.update({
                "rot_y_min": self.rot_y.min_value,
                "rot_y_max": self.rot_y.max_value,
                "rot_z_min": self.rot_z.min_value,
                "rot_z_max": self.rot_z.max_value,
            })
        else:
            common_args.update({
                "rot_y_min": 0,
                "rot_y_max": 0,
                "rot_z_min": 90,
                "rot_z_max": 90,
            })

        return common_args

    def build_ui(self):
        self._build_base_ui()
        self.dim_w = MinMaxWidget("Defect Dimensions Width",
                                  min_value=0.1,
                                  tooltip="Defining the Minimum and Maximum Width of the Defect")
        self.dim_h = MinMaxWidget("Defect Dimensions Length",
                                  min_value=0.1,
                                  tooltip="Defining the Minimum and Maximum Length of the Defect")

        with ui.HStack(height=0):
            ui.Label("Use Advanced Rotations")
            self.rotation_cb = ui.CheckBox().model
            self.rotation_cb.add_value_changed_fn(self.update_advanced_rotations)
        self.container = ui.VStack(height=0)
        with self.container:
            self.rot_x = MinMaxWidget("Defect Rotation ", min_value=0, max_value=360,
                                      tooltip="Defining the Minimum and Maximum X-Rotation of the Defect")

        self.countContainer = ui.HStack(height=0, tooltip="Number of defects to generate")
        with self.countContainer:
            with ui.HStack():
                ui.Label("Count", width=0)
                ui.IntDrag(model=self.count)


    @property
    def defect_name(self) -> str:
        return 'scratch'

    def update_advanced_rotations(self, event):
        self.container.clear()
        self.countContainer.clear()
        if self.rotation_cb.get_value_as_bool():
            with self.container:
                self.rot_x = MinMaxWidget("Defect Rotation X ", min_value=0, max_value=360,
                                          tooltip="Defining the Minimum and Maximum X-Rotation of the Defect")
                self.rot_y = MinMaxWidget("Defect Rotation Y", min_value=0, max_value=360,
                                          tooltip="Defining the Minimum and Maximum Y-Rotation of the Defect")
                self.rot_z = MinMaxWidget("Defect Rotation Z", min_value=0, max_value=360,
                                          tooltip="Defining the Minimum and Maximum Y-Rotation of the Defect")
            with self.countContainer:
                with ui.HStack():
                    ui.Label("Count", width=0)
                    ui.IntDrag(model=self.count)
        else:
            with self.container:
                self.rot_x = MinMaxWidget("Defect Rotation ", min_value=0, max_value=360,
                                          tooltip="Defining the Minimum and Maximum X-Rotation of the Defect")
            with self.countContainer:
                with ui.HStack():
                    ui.Label("Count", width=0)
                    ui.IntDrag(model=self.count)

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
