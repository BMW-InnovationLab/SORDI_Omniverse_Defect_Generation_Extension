# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import uuid
from typing import List
import omni.usd
import carb
import omni.kit.commands
import os
from pxr import Usd, Gf
from defect.generation.domain.models.defect_generation_request import PrimDefectObject, DefectObject
import matplotlib as mpl

def get_current_stage():
    context = omni.usd.get_context()
    stage = context.get_stage()
    return stage

def check_path(path: str) -> bool:
    if not path:
        carb.log_error("No path was given")
        return False
    return True

def is_valid_prim(path: str):
    prim = get_prim(path)
    if not prim.IsValid():
        carb.log_warn(f"No valid prim at path given: {path}")
        return None
    return prim

def delete_prim(path: str):
    omni.kit.commands.execute('DeletePrims',
        paths=[path],
        destructive=False)

def get_prim_attr(prim_path: str, attr_name: str):
    prim = get_prim(prim_path)
    return prim.GetAttribute(attr_name).Get()

def get_textures(dir_path, png_type=".png"):
    textures = []
    dir_path += "/"
    for file in os.listdir(dir_path):
        if file.endswith(png_type):
            textures.append(dir_path + file)
    textures.sort()
    return textures

def get_prim(prim_path: str):
    stage = get_current_stage()
    prim = stage.GetPrimAtPath(prim_path)
    return prim


def get_all_children_paths(children, parent_prim: Usd.Prim):
    # Iterates over all children
    for child_prim in parent_prim.GetAllChildren():
        if child_prim.GetTypeName() == "Xform":
            get_all_children_paths(children, child_prim)
        else:
            children.append(child_prim.GetPath())
    return children


def generate_small_uuid():
    return str(uuid.uuid4())[:8]

def get_center_coordinates(prim_path: str):
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(prim_path)
    matrix: Gf.Matrix4d = omni.usd.get_world_transform_matrix(prim)
    translate: Gf.Vec3d = matrix.ExtractTranslation()
    return translate

def fetch_all_defect_objects(prim_defect_list: [PrimDefectObject]) -> List[DefectObject]:
    all_defect_objects = []
    for prim_defect in prim_defect_list:
        for defect in prim_defect.defects:
            all_defect_objects.append(defect)
    return all_defect_objects

def find_prim_defect_by_uuid(prim_defects: List[PrimDefectObject], target_uuid: str) -> PrimDefectObject:
    for prim_defect in prim_defects:
        for defect in prim_defect.defects:
            if defect.uuid == target_uuid:
                return prim_defect

def rgba_to_hex(color):
    r, g, b = color
    hex = mpl.colors.rgb2hex((r, g, b), keep_alpha=False)
    return hex

def get_bbox_dimensions(prim_path):
    #Get the Top, Bottom, Left, Right Coordinates of a prim based on its path
    bbox = omni.usd.get_context().compute_path_world_bounding_box(prim_path)
    min_coordinates = bbox[0]
    max_coordinates = bbox[1]
    return min_coordinates,max_coordinates