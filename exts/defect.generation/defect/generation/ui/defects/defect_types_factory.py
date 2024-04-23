from typing import List, Dict
from defect.generation.ui.defects.defect_types.base_defect_ui import  BaseDefectUI
from defect.generation.utils.subclass_utils import get_subclasses
import os
# Import defect uis
from defect.generation.ui.defects.defect_types.scratches_defect_ui import ScratchesUI
from defect.generation.ui.defects.defect_types.cracks_defect_ui import CracksUI
from defect.generation.ui.defects.defect_types.holes_defect_ui import HolesUI

import logging

logger = logging.getLogger(__name__)


class DefectUIFactory:
    def __init__(self):
        defect_uis = get_subclasses(BaseDefectUI)
        logger.warning(f"In defect factory, defect UIs are {defect_uis}")
        self._defect_methods_ui: Dict[str, BaseDefectUI] = {}
        for defect_ui in defect_uis:
            defect_ui_instance = defect_ui()
            self._defect_methods_ui[defect_ui_instance.defect_name] = defect_ui_instance

    def get_defect_method_ui(self, defect_method: str) -> BaseDefectUI:
        return self._defect_methods_ui[defect_method]

    def get_all_defect_method_ui(self) -> List[BaseDefectUI]:
        return list(self._defect_methods_ui.values())

    def get_defect_methods_ui(self, defect_methods: List[str]) -> List[BaseDefectUI]:
        return [self._defect_methods_ui[key] for key in defect_methods if key in self._defect_methods_ui]

