from typing import Any, List, Tuple
from pydantic import BaseModel

class LightDomainRandomizationParameters(BaseModel):
    light_intensity_min_value: float = None
    light_intensity_max_value: float = None
    light_rotation_min_value: float = None
    light_rotation_max_value: float = None
    light_scale_min_value: float = None
    light_scale_max_value: float = None
    light_position_min_value: float = None
    light_position_max_value: float = None
    light_color_min_value: List[float] = None
    light_color_max_value: List[float] = None
    light_count: int= None
    active = False


class CameraDomainRandomizationParameters(BaseModel):
    camera_distance_min_value: List[float] = None
    camera_distance_max_value: List[float] = None
    camera_prims: List[Tuple[str]] = None
    active = False


class DomainRandomizationRequest(BaseModel):
    # Light params
    light_domain_randomization_params: LightDomainRandomizationParameters
    # Camera params
    camera_domain_randomization_params: CameraDomainRandomizationParameters
    # Color params
    #TODO: Add color randomization params