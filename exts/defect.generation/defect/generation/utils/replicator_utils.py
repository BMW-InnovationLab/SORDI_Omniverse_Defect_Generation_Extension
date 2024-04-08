import omni.replicator.core as rep
import carb
from defect.generation.utils.helpers import *



def rep_preview():
    rep.orchestrator.preview()

def rep_run():
    rep.orchestrator.run()

def does_defect_layer_exist() -> bool:
    stage = get_current_stage()
    for layer in stage.GetLayerStack():
        if layer.GetDisplayName() == "Defect":
            return True
    return False

def get_defect_layer():
    stage = get_current_stage()
    pos = 0
    for layer in stage.GetLayerStack():
        if layer.GetDisplayName() == "Defect":
            return layer, pos
        pos = pos + 1
    return None