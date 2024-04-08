from typing import Any, List
from pydantic import BaseModel

class DefectObject(BaseModel):
    defect_name: str
    args: Any
    uuid: str
    
class DefectGenerationRequest(BaseModel):
    prims_path: List[str]
    texture_dir: str
    defects: List[DefectObject]

