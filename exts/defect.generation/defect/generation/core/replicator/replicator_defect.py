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

import omni.replicator.core as rep
import carb
from defect.generation.utils.helpers import get_textures, is_valid_prim
from defect.generation.domain.models.defect_generation_request import DefectGenerationRequest, DefectObject
import logging
import os
import random
from defect.generation.core.writer.bmw_writer import BMWWriter
logger = logging.getLogger(__name__)
camera_path = "/World/Camera"





def _create_randomizers():

    def move_defect(defect_objet: DefectObject, prim_path: str):

        semantic_label = defect_objet.args.get("semantic_label", "default")
        rot_min = defect_objet.args.get("rot_min", 0)
        rot_max = defect_objet.args.get("rot_max", 1)
        dim_h_min = defect_objet.args.get("dim_h_min", 0)
        dim_h_max = defect_objet.args.get("dim_h_max", 1)
        dim_w_min = defect_objet.args.get("dim_w_min", 0)
        dim_w_max = defect_objet.args.get("dim_w_max", 1)




        defects = rep.get.prims(semantics=[('uuid', defect_objet.uuid + '_mesh')])
        plane = rep.get.prim_at_path(prim_path)
        with defects:
            #rep.randomizer.scatter_2d(surface_prims=[plane_samp, sphere_samp], check_for_collisions=True)
            rep.randomizer.scatter_2d(plane, seed=random.randint(0, 999999))
            rep.modify.pose(
                rotation=rep.distribution.uniform(
                    (rot_min, 0, 90), 
                    (rot_max, 0, 90)
                ),
                scale=rep.distribution.uniform(
                    (1, dim_h_min,dim_w_min),
                    (1, dim_h_max, dim_w_max)
                )
            )

        return defects.node
    
    def change_defect_image(defect_objet: DefectObject, texture_dir: str):
        texture_dir = os.path.join(texture_dir, defect_objet.defect_name)
        diffuse_textures = get_textures(texture_dir, "_D.png")
        normal_textures = get_textures(texture_dir, "_N.png")
        roughness_textures = get_textures(texture_dir, "_R.png")

        projections = rep.get.prims(semantics=[('uuid', defect_objet.uuid + '_projectmat')])
        with projections:
            rep.modify.projection_material(
                diffuse=rep.distribution.sequence(diffuse_textures),
                normal=rep.distribution.sequence(normal_textures),
                roughness=rep.distribution.sequence(roughness_textures))
        return projections.node

    rep.randomizer.register(move_defect)
    rep.randomizer.register(change_defect_image)

def _create_camera(prim_path):
    if is_valid_prim(camera_path) is None:
        #camera positioned conveniantly oposing the cube for testing purposes.
        camera = rep.create.camera(position=(0.09826, 3.90823, 1.10067), look_at=rep.get.prim_at_path(prim_path))
        carb.log_info(f"Creating Camera: {camera}")
    else:
        camera = rep.get.prim_at_path(camera_path)
    return camera

def _create_defects(defect_objet: DefectObject, prim_path: str):
    semantic_label = defect_objet.args.get("semantic_label", "default")
    count = defect_objet.args.get("count", 1)
    
    target_prim = rep.get.prims(path_pattern=prim_path)
    for i in range(count):
        cube = rep.create.cube(visible=False, semantics=[('class', semantic_label + '_mesh'),('uuid', defect_objet.uuid + '_mesh')], position=0, scale=1, rotation=(0, 0, 90))
        with target_prim:
            rep.create.projection_material(cube, [('class', semantic_label + '_projectmat'),('uuid', defect_objet.uuid + '_projectmat')])

def create_defect_layer(req: DefectGenerationRequest, frames: int = 1, output_dir: str = "_defects", rt_subframes: int = 0, use_seg: bool = False, use_bb: bool = True, use_bmw: bool =True):
    if len(req.texture_dir) <= 0:
        carb.log_error("No directory selected")
        return
    with rep.new_layer("Defect"):

        _create_randomizers()   
        

        for defect_prim_objects in req.prim_defects:
            for defect in defect_prim_objects.defects:
                _create_defects(defect, prim_path=defect_prim_objects.prim_path)

        # Create / Get camera #TODO: Will we have multiple cameras ?
        camera = _create_camera(req.prim_defects[0].prim_path)
        
        # Add Default Light
        distance_light = rep.create.light(rotation=(315,0,0), intensity=3000, light_type="distant")

        render_product  = rep.create.render_product(camera, (1024, 1024))

        # Initialize and attach writer
        if use_bmw:
            # Create a list containing all the defect names present in scene.
            defect_names = []
            for prim_defect in req.prim_defects:
                for defect in prim_defect.defects:
                    if defect.defect_name not in defect_names:
                        defect_names.append(defect.defect_name)
            rep.WriterRegistry.register(BMWWriter)
            writer = rep.WriterRegistry.get("BMWWriter")
            writer.initialize(output_dir=output_dir, rgb=True, bounding_box_2d_tight=use_bb,semantic_segmentation=use_seg, defect=defect_names)
        else:
            writer = rep.WriterRegistry.get("BasicWriter")
            writer.initialize(output_dir=output_dir, rgb=True, semantic_segmentation=use_seg, bounding_box_2d_tight=use_bb)
            # Attach render_product to the writer
        writer.attach([render_product])

        # Setup randomization
        with rep.trigger.on_frame(num_frames=frames, rt_subframes=rt_subframes):
            for defect_prim_objects in req.prim_defects:
                for defect in defect_prim_objects.defects:
                    rep.randomizer.move_defect(defect_objet=defect, prim_path=defect_prim_objects.prim_path)
                    rep.randomizer.change_defect_image(defect_objet=defect, texture_dir=req.texture_dir)
