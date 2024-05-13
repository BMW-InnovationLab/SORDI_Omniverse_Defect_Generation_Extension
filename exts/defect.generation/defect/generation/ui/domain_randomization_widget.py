import omni.ui as ui 
from omni.ui import color as cl
import omni.kit.notification_manager as nm
from defect.generation.ui.widgets import MinMaxWidget, PathWidget, RGBMinMaxWidget
from defect.generation.utils import helpers
from defect.generation.domain.models.domain_randomization_request import DomainRandomizationRequest, LightDomainRandomizationParameters, CameraDomainRandomizationParameters, ColorDomainRandomizationParameters

MAX_NUMBER_PRIM_PATH_CHARACTERS_TO_SHOW = 25

class RandomizerParameters():
    def __init__(self) -> None:
        # Light Params
        self.light_intensity = None
        self.light_rotation = None
        self.light_color = None
        self.light_scale = None
        self.light_position = None
        self.light_count_model = ui.SimpleIntModel(1)

        # Camera Params
        self.camera_params_list = []
        self.camera_distance = None

        # Color Params
        self.prim_colors = {}
        
        self.build_randomization_ui()

    def prepare_domain_randomization_request(self) -> DomainRandomizationRequest:
        light_domain_randomization_params = LightDomainRandomizationParameters()
        camera_domain_randomization_params = CameraDomainRandomizationParameters()

        color_domain_randomization_params = ColorDomainRandomizationParameters()

        if self.light_cb.get_value_as_bool():
            light_domain_randomization_params.active = True
            if self.light_intensity is not None:
                light_domain_randomization_params.light_intensity_min_value = self.light_intensity.min_value
                light_domain_randomization_params.light_intensity_max_value = self.light_intensity.max_value
            if self.light_rotation is not None:
                light_domain_randomization_params.light_rotation_min_value = self.light_rotation.min_value
                light_domain_randomization_params.light_rotation_max_value = self.light_rotation.max_value
            if self.light_color is not None:
                light_domain_randomization_params.light_color_min_value = self.light_color.min_values
                light_domain_randomization_params.light_color_max_value = self.light_color.max_values
            if self.light_scale is not None:
                light_domain_randomization_params.light_scale_min_value = self.light_scale.min_value
                light_domain_randomization_params.light_scale_max_value = self.light_scale.max_value
            if self.light_position is not None:
                light_domain_randomization_params.light_position_min_value = self.light_position.min_value
                light_domain_randomization_params.light_position_max_value = self.light_position.max_value

            light_domain_randomization_params.light_count = self.light_count_model.as_int
        if self.camera_cb.get_value_as_bool():
            camera_domain_randomization_params.active = True
            if self.camera_distance is not None:
                camera_domain_randomization_params.camera_distance_min_value = self.camera_distance.min_value
                camera_domain_randomization_params.camera_distance_max_value = self.camera_distance.max_value
            if len(self.camera_params_list) != 0:
                camera_domain_randomization_params.camera_prims = self.camera_params_list
            else:
                camera_domain_randomization_params.camera_prims = []
          

        
        if self.color_cb.get_value_as_bool(): 
            color_domain_randomization_params.active = True
            if len(self.prim_colors) != 0:
                color_domain_randomization_params.prim_colors = self.prim_colors            
            else: 
                color_domain_randomization_params.prim_colors = {}

        return DomainRandomizationRequest(
            light_domain_randomization_params=light_domain_randomization_params,
            camera_domain_randomization_params=camera_domain_randomization_params,
            color_domain_randomization_params=color_domain_randomization_params
        )

    def add_randomization_checkbox(self, name, callback):
        container = ui.VStack(height=0)
        with container:
            with ui.HStack():
                ui.Label(f"{name} Randomizations")
                cb = ui.CheckBox(name=f"{name} Randomization", width=200).model
                cb.add_value_changed_fn(callback)
        return container, cb
    
    # Check Scatter and Look at Prim values and add them to list. 
    def add_camera_params(self): 
        scattering_prim_path = self.scattering_prim.path_value
        lookat_prim_path = self.lookat_prim.path_value
        
        # Check if scattering prim path is added and is valid
        if scattering_prim_path:
            if helpers.is_valid_prim(scattering_prim_path):
                scattering_prim_valid = True
            else:
                scattering_prim_valid = False
                nm.post_notification(f"There is no '{scattering_prim_path}' Prim in the stage", hide_after_timeout=True, duration=5, status=nm.NotificationStatus.WARNING)
        # Valid if not provided
        else:
            scattering_prim_valid = True 

        # Check if lookat prim path is added and is valid
        if lookat_prim_path:
            if helpers.is_valid_prim(lookat_prim_path):
                lookat_prim_valid = True 
            else:
                lookat_prim_valid = False
                nm.post_notification(f"There is no '{lookat_prim_path}' Prim in the stage.", hide_after_timeout=True, duration=5, status=nm.NotificationStatus.WARNING)
        # Valid if not provided
        else:
            lookat_prim_valid = True  

        if scattering_prim_valid and lookat_prim_valid:  
            # Selected Scatter and Look at Prims have to be different.
            if self.scattering_prim.path_value != self.lookat_prim.path_value: 
                new_camera_params = (self.scattering_prim.path_value, self.lookat_prim.path_value)
                if new_camera_params not in self.camera_params_list:
                    self.camera_params_list.append(new_camera_params)
                    self.view_added_params()
            
            # If Scatter and Look At prims are the same, send notification and do not add to list. 
            else: 
                nm.post_notification("Scatter Prim and Look At Prim cannot be the same.", hide_after_timeout=True, duration=5, status=nm.NotificationStatus.WARNING)

    # Display the added Scatter and Look at Prims in the UI. 
    def view_added_params(self): 
        with self.camera_params: 
            with self.camera_params_frame:
                with ui.VStack(height=0):

                    self.camera_distance = MinMaxWidget("Camera Distance", min_value=0, max_value=10, tooltip="Set camera distance if no scattering and look at prims will be provided.")
                    with ui.HStack(height=0):
                        self.scattering_prim = PathWidget("Scattering Prim")
                        self.lookat_prim = PathWidget("Look At Prim")
                    
                    with ui.HStack(): 
                        ui.Button("Add", clicked_fn=lambda: self.add_camera_params(), tooltip="Add the Current Scattering Prim and LookAt Prim")
                        ui.Button("Reset", clicked_fn=lambda: self.reset_current_camera_params(), tooltip="Reset the Scattering Prim and LookAt Prim")
                    if self.camera_params_list != []:
                        self.added_camera_params_frame = ui.CollapsableFrame("Added Camera Params")
                        with self.added_camera_params_frame:
                            self.camera_params_list_ui = ui.VStack()
                            with self.camera_params_list_ui: 
                                with ui.HStack(spacing=2):
                                    ui.Label("Scattering Prim", width = 150)
                                    ui.Label("Look At Prim", width = 150)
                                    ui.Label("Look At Prim Center", width = 150)
                            self.update_added_camera_params_ui()
           
    def update_added_camera_params_ui(self): 
        with self.added_camera_params_frame: 
            self.camera_params_list_ui.clear()

            with self.camera_params_list_ui:
                with ui.HStack(height=0, spacing=2):
                    ui.Label("Scattering Prim", width = 225)
                    ui.Label("Look At Prim", width = 225)
                    ui.Label("Look At Prim Center", width = 225)

                with ui.HStack():
                    ui.Line(height=ui.Length(20))
                
                for scattering, lookat in self.camera_params_list:
                    with ui.HStack(height=0):
                        ui.Label(f"{str(scattering)[:MAX_NUMBER_PRIM_PATH_CHARACTERS_TO_SHOW]}{'...' if len(str(scattering))>MAX_NUMBER_PRIM_PATH_CHARACTERS_TO_SHOW else ''}", width=225, style={"color": 0xFF777777})
                        ui.Label(f"{str(lookat)[:MAX_NUMBER_PRIM_PATH_CHARACTERS_TO_SHOW]}{'...' if len(str(lookat))>MAX_NUMBER_PRIM_PATH_CHARACTERS_TO_SHOW else ''}", width=225, style={"color": 0xFF777777})
                        if lookat != "":
                            coords = helpers.get_center_coordinates(prim_path=lookat)
                            formatted_coords = ", ".join("{:.2f}".format(num) for num in coords)
                            ui.Label(f"({formatted_coords})", width=225, style={"color": 0xFF777777})
                    ui.Line(height=ui.Length(20))

                ui.Button("Reset All", clicked_fn=lambda: self.reset_all_camera_params(), tooltip="Reset all added Scattering Prim and LookAt Prim")
    
    # Reset Scattering and Look At Path Widgets.
    def reset_current_camera_params(self): 
        with self.camera_params:
            self.scattering_prim._path_model.set_value("")
            self.lookat_prim._path_model.set_value("")
                            
    # Reset all added camera params
    def reset_all_camera_params(self): 
        self.camera_params_list = []
        self.view_added_params()

#--------------------------------------------------------end camera fns---------------------------------------------------------------------------------------#
    def get_color_values(self):

        r_abs, g_abs, b_abs, a_abs = self.rgb_color_values.get_item_children()

        # Get the selected color
        r = self.rgb_color_values.get_item_value_model(r_abs).as_float
        g = self.rgb_color_values.get_item_value_model(g_abs).as_float
        b = self.rgb_color_values.get_item_value_model(b_abs).as_float
        a = self.rgb_color_values.get_item_value_model(a_abs).as_float

        return (r,g,b,a)
    
    def add_color(self):
        r, g, b, a = self.get_color_values()
        # Assign the color to all selected prims
        self.color_prim_path = self.color_prim.path_value
        if self.color_prim_path!= "":
            if self.color_prim_path not in self.prim_colors:
                self.prim_colors[self.color_prim_path] = [(r, g, b)]
            else:
                # Add the color to the path if it is not already present  
                if (r, g, b) not in self.prim_colors[self.color_prim_path]:
                    self.prim_colors[self.color_prim_path].append((r, g, b))
                    nm.post_notification(f"Added new color: r={r:.4f}, g={g:.4f}, b={b:.4f} to {self.color_prim_path}", hide_after_timeout=True, duration=5, status=nm.NotificationStatus.INFO)
                else:
                    nm.post_notification(f"Color: r={r:.4f}, g={g:.4f}, b={b:.4f} already exists for {self.color_prim_path}", hide_after_timeout=True, duration=5, status=nm.NotificationStatus.WARNING)

            self.update_added_colors_ui()

    def update_added_colors_ui(self): 
        self.added_color_params_frame.visible=True
        with self.added_color_params_frame: 
            self.color_params_list_ui.clear()

            with self.color_params_list_ui:
                with ui.HStack(spacing=2):
                    ui.Label("Prim Path", width = 150)
                    ui.Label("RGB Value", width = 150)
                    ui.Label("RGB Color", width = 150)

                ui.Line(height=ui.Length(20))
                for i, (path, colors_list) in enumerate(self.prim_colors.items()):
                    with ui.HStack(height=0):
                        ui.Label(str(path)[:MAX_NUMBER_PRIM_PATH_CHARACTERS_TO_SHOW], width=150, style={"color": 0xFF777777})
                        with ui.VStack():
                            for color in colors_list: 
                                color_formatted = f"{color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f}"
                                ui.Label(color_formatted, width=150, style={"color": 0xFF777777})
                        with ui.VStack():
                            for color in colors_list: 
                                color_hex = helpers.rgba_to_hex(color)
                                ui.Rectangle(
                                width=21,
                                height=21,
                                style={
                                    "background_color": cl(str(color_hex))
                                },
                                )
                    ui.Line(height=ui.Length(20))
                ui.Button("Reset all", tooltip="Reset all picked colors and all prims", clicked_fn=self.reset_all)

    def reset_colors(self):
        # Remove all colors for the selected prims

        if self.color_prim.path_value in self.prim_colors:
            del self.prim_colors[self.color_prim.path_value]
            self.update_added_colors_ui()

    def reset_all(self):
        # Remove all colors and all their prims
            self.prim_colors = {}
            self.update_added_colors_ui()
#--------------------------------------------------------end color fns---------------------------------------------------------------------------------------#


    # Build the Light Params in the UI when the Light Checkbox is clicked. 
    def build_light_ui(self):        
        # If Light Randomization is Checked
        if self.light_cb.get_value_as_bool():                                  
            with self.light_params:
                with ui.CollapsableFrame("Light Randomization Parameters", height=0):
                    with ui.VStack():
                        self.light_intensity = MinMaxWidget("Light Intensity", min_value=500, max_value=5000)
                        self.light_rotation = MinMaxWidget("Light Rotation",min_value=0, max_value=360)
                        self.light_color = RGBMinMaxWidget("Light Color")
                        self.light_scale = MinMaxWidget("Light Scale", min_value=5, max_value=10)
                        self.light_position = MinMaxWidget("Light Scale", min_value=-30, max_value=30)
                        ui.IntDrag(model=self.light_count_model)
        
        # If Light Randomization is Unchecked
        else:                                                           
            self.light_params.clear()
            with self.light_params:
                with ui.HStack():
                    ui.Label("Light Randomizations")
                    self.light_cb = ui.CheckBox(name = "Light Randomization", width=200, enabled=True, checked=False).model
                    self.light_cb.add_value_changed_fn(lambda _: self.build_light_ui())


    # Build the Camera Params in the UI when the Camera Checkbox is clicked. 
    def build_camera_ui(self):
        # If Camera Randomization is checked
        if self.camera_cb.get_value_as_bool():
            with self.camera_params: 
                self.camera_params_frame = ui.CollapsableFrame("Camera Randomization Parameters", height=0)
                with self.camera_params_frame:
                    with ui.VStack(height=0):
                        if self.camera_params_list == []:
                            self.camera_distance = MinMaxWidget("Camera Distance", min_value=0, max_value=10, tooltip="Set camera distance if no scattering and look at prims will be provided.")
                        with ui.HStack(height=0):
                            self.scattering_prim = PathWidget("Scattering Prim")
                            self.lookat_prim = PathWidget("Look At Prim")
                    
                        with ui.HStack(): 
                            ui.Button("Add", clicked_fn=lambda: self.add_camera_params(), tooltip="Add the Current Scattering Prim and LookAt Prim")
                            ui.Button("Reset", clicked_fn=lambda: self.reset_current_camera_params(), tooltip="Reset the Scattering Prim and LookAt Prim")
                       
                        self.added_camera_params_frame = ui.CollapsableFrame("Added Camera Params", visible=False)
                        with self.added_camera_params_frame:
                            self.camera_params_list_ui = ui.VStack()
                            with self.camera_params_list_ui: 
                                with ui.HStack(spacing=2):
                                    ui.Label("Scattering Prim", width = 150)
                                    ui.Label("Look At Prim", width = 150)
                                    ui.Label("Look At Prim Center", width = 150)

                        if self.camera_params_list != []: 
                            self.view_added_params()

        # If Camera Randomization is Unchecked
        else: 
            self.camera_params.clear()
            with self.camera_params: 
                with ui.HStack():
                    ui.Label("Camera Randomizations")
                    self.camera_cb = ui.CheckBox(name = "Camera Randomization", width=200).model
                    self.camera_cb.add_value_changed_fn(lambda _: self.build_camera_ui())
    
    # Build the Color Params in the UI when the Color Checkbox is clicked. 
    def build_color_ui(self):
        # If Color Randomization is Checked
        if self.color_cb.get_value_as_bool():
            with self.color_params:
                self.color_params_frame = ui.CollapsableFrame("Color Randomization Parameters", height=0)
                with self.color_params_frame: 
                    with ui.VStack(height=0):
                        with ui.HStack(style={"margin": 3}, height=0, spacing=5):
                            self.color_prim = PathWidget("Color Prim")
                            ui.Label("RGB Color Picker", width=70, tooltip="Select color to be added to the current prim path.")
                            self.rgb_color_values = ui.ColorWidget(width=25, height=0, style={"margin":6}).model

                        with ui.HStack():
                            ui.Button("Add", tooltip="Add picked color", clicked_fn=self.add_color)
                            ui.Button("Reset", tooltip="Reset picked colors of this prim", clicked_fn=self.reset_colors)

                        self.added_color_params_frame = ui.CollapsableFrame("Added Color Params", visible=False)
                        with self.added_color_params_frame:
                            self.color_params_list_ui = ui.VStack()
                            with self.color_params_list_ui:
                                with ui.HStack(spacing=2):
                                    ui.Label("Prim Path", width = 150)
                                    ui.Label("RGB Value", width = 150)
                                    ui.Label("RGB Color", width = 150)
                                ui.Line(height=ui.Length(20))
                        if self.prim_colors != {}: 
                            self.update_added_colors_ui()

        # If Color Randomization is Unchecked
        else: 
            self.color_params.clear()
            with self.color_params: 
                with ui.HStack():
                    ui.Label("Color Randomizations")
                    self.color_cb = ui.CheckBox(name = "Color Randomization", width=200).model
                    self.color_cb.add_value_changed_fn(lambda _: self.build_color_ui())
    
    def build_randomization_ui(self):
        self.light_params, self.light_cb = self.add_randomization_checkbox("Light", lambda _: self.build_light_ui())
        self.camera_params, self.camera_cb = self.add_randomization_checkbox("Camera", lambda _: self.build_camera_ui())
        self.color_params, self.color_cb = self.add_randomization_checkbox("Color", lambda _: self.build_color_ui())
