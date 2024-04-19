from typing import Any, List
from pydantic import BaseModel

class DefectObject(BaseModel):
    defect_name: str
    args: Any
    uuid: str

class PrimDefectObject(BaseModel):
    prim_path: str
    defects: List[DefectObject]

class DefectGenerationRequest(BaseModel):
    prim_defects: List[PrimDefectObject]
    texture_dir: str

