
import omni.ui as ui
from defect.generation.utils.helpers import generate_small_uuid
from omni.kit.notification_manager import post_notification, NotificationStatus
import carb


class BaseDefectUI:
    def __init__(self) -> None:
        pass
    
    def set_object_params(self, object_params):
        self.object_params = object_params

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
        if len(self.semantic_label.as_string) == 0:
            post_notification(
                f"Defect Semantic Cannot Be Empty",
                duration=5,
                status=NotificationStatus.WARNING
            )
            carb.log_error(f"Defect Semantic Cannot Be Empty")
        elif self.count.as_int < 1:
            post_notification(
                f"Defect Count Cannot be Less Than One",
                duration=5,
                status=NotificationStatus.WARNING
            )
            carb.log_error(f"Defect Count Cannot be Less Than One")
        else:
            # Check if current selected prim exists in the defects parameters list
            if self.object_params.current_selected_prim_value in self.defect_parameters_list:

                args = self.prepare_defect_args()

                # If it exists, append defects to it
                self.defect_parameters_list[self.object_params.current_selected_prim_value].append({
                    "defect_name": self.defect_name,
                    "args": args
                })

                post_notification(
                    f"Added defect: {self.defect_name}, count: {args['count']}, semantic label: {args['semantic_label']}",
                    duration = 5,
                    status=NotificationStatus.INFO
                )
            else:
                # If it does not exist, no defects are appended, and warning is sent to the user
                post_notification(
                    f"Prim Path {self.object_params.current_selected_prim_value} does not exist. Copy it from the stage and press Apply before adding defects.",
                    duration = 5,
                    status=NotificationStatus.WARNING
                )

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