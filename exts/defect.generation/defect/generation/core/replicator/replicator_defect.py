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
from defect.generation.utils.helpers import get_textures, is_valid_prim, get_center_coordinates, get_prim, get_all_children_paths
from defect.generation.domain.models.defect_generation_request import DefectGenerationRequest, DefectObject
from defect.generation.domain.models.domain_randomization_request import DomainRandomizationRequest, LightDomainRandomizationParameters, CameraDomainRandomizationParameters
import logging
import os
import random
from defect.generation.core.writer.bmw_writer import BMWWriter
from pxr import Sdf

logger = logging.getLogger(__name__)



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
        defect_prim = rep.get.prim_at_path(prim_path)
        with defects:
            #rep.randomizer.scatter_2d(surface_prims=[plane_samp, sphere_samp], check_for_collisions=True)
            rep.randomizer.scatter_2d(defect_prim, seed=random.randint(0, 999999))
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
        seed=random.randint(0, 999999)
        with projections:
            rep.modify.projection_material(
                diffuse=rep.distribution.choice(diffuse_textures,seed=seed),
                normal=rep.distribution.choice(normal_textures,seed=seed),
                roughness=rep.distribution.choice(roughness_textures,seed=seed))
            rep.modify.visibility(rep.distribution.choice([True, False]))
        return projections.node

    rep.randomizer.register(move_defect)
    rep.randomizer.register(change_defect_image)

    def change_light(light_randomization: LightDomainRandomizationParameters):
        lights = rep.create.light(
                    light_type="Distant",
                    color=rep.distribution.uniform(light_randomization.light_color_min_value, light_randomization.light_color_max_value),
                    intensity=rep.distribution.uniform(light_randomization.light_intensity_min_value, light_randomization.light_intensity_max_value),
                    position=rep.distribution.uniform(light_randomization.light_position_min_value, light_randomization.light_position_max_value),
                    scale=rep.distribution.uniform(light_randomization.light_scale_min_value, light_randomization.light_scale_max_value),
                    rotation =  rep.distribution.uniform(light_randomization.light_rotation_min_value, light_randomization.light_rotation_max_value),
                    count=light_randomization.light_count,
                )
        return lights.node
    rep.randomizer.register(change_light)


def _create_camera():
    camera = rep.create.camera()
    logger.warning(f"Creating Camera: {camera}")
    return camera

def _create_camera_randomizer():
    def change_camera(change_camera_params, prim_defects_path, camera_domain_randomization_params: CameraDomainRandomizationParameters):
        for camera_option in change_camera_params:
                
                camera_randomization_params = camera_option["randomization"]
                camera = camera_option["camera"]
                scatter_prim_path, look_at_prim_path = camera_randomization_params

                logger.warn(f"Scatter prim is {scatter_prim_path}")
                logger.warn(f"Look at prim is {look_at_prim_path}")

                if scatter_prim_path and not look_at_prim_path:
                    logger.warning(f"Routed omni graph to [YES] scatter prim and [NO] look at prim ...")
                    # Choose a random look at prim from all the prims which have defects
                    look_at_prim_path = rep.distribution.choice(prim_defects_path, with_replacements=True)
                elif not scatter_prim_path and look_at_prim_path:
                    logger.warning(f"Routed omni graph to [NO] scatter prim and [YES] look at prim...")
                    # Create a sphere scatter prim around the look at prim
                    scatter_prim_path = rep.create.sphere(position=get_center_coordinates(look_at_prim_path), scale=camera_domain_randomization_params.camera_distance_max_value, visible=False)
                else:
                    # Using the provided scatter prim and look at prim
                    logger.warning(f"Routed omni graph to [YES] scatter prim and [YES] look at prim...")
                with camera:
                    rep.randomizer.scatter_3d(scatter_prim_path, seed=random.randint(0, 999999))
                    rep.modify.pose(look_at=look_at_prim_path)

    rep.randomizer.register(change_camera)


def _create_defects(defect_objet: DefectObject, prim_path: str):
    semantic_label = defect_objet.args.get("semantic_label", "default")
    # Get prim to place defect on
    target_prim = rep.get.prims(path_pattern=prim_path)
    # Create cube for projecting the material
    cube = rep.create.cube(visible=False, semantics=[('class', semantic_label + '_mesh'),('uuid', defect_objet.uuid + '_mesh')], position=0, scale=1, rotation=(0, 0, 90))
    with target_prim:
        rep.create.projection_material(cube, [('class', semantic_label + '_projectmat'),('uuid', defect_objet.uuid + '_projectmat')])

def create_defect_layer(defect_generation_request: DefectGenerationRequest, domain_randomization_request :DomainRandomizationRequest, frames: int = 1, output_dir: str = "_defects", rt_subframes: int = 0, use_seg: bool = False, use_bb: bool = True, use_bmw: bool =True):
    if len(defect_generation_request.texture_dir) <= 0:
        carb.log_error("No directory selected")
        return
    with rep.new_layer("Defect"):
        change_camera_params = []
        render_list = []
        prim_defects_path = []
        # Create randomizers
        _create_randomizers()
        _create_camera_randomizer()
        # Get camera params
        camera_randomization_params = domain_randomization_request.camera_domain_randomization_params.camera_prims

        # Go through every prim which has defects
        for defect_prim_objects in defect_generation_request.prim_defects:
            # Add list of meshes with derfects
            prim = get_prim(defect_prim_objects.prim_path)
            if prim.GetTypeName() == "Xform":
                logger.warning(f"{defect_prim_objects.prim_path} is an Xform")
                children = []
                prim_defects_path.extend(get_all_children_paths(children, prim))
            else:
                logger.warning(f"{defect_prim_objects.prim_path} is not an Xform")
                prim_defects_path.append(Sdf.Path(defect_prim_objects.prim_path))

            # Create defects
            for defect in defect_prim_objects.defects:
                _create_defects(defect, prim_path=defect_prim_objects.prim_path)

        # Remove duplicate paths
        prim_defects_path = list(set(prim_defects_path))
        logger.warning(f"All prims with defects: {prim_defects_path}")   
 

        # Camera scatter prim and lookat prim randomization
        if domain_randomization_request.camera_domain_randomization_params.active:
            # If no scatter prim or look at prim specified, create a look at prim for each defect
            if len(domain_randomization_request.camera_domain_randomization_params.camera_prims) == 0:
                for prim_defect_path in prim_defects_path:
                    camera_randomization_params.append((None, str(prim_defect_path)))
                logger.warning(f"No camera prims were specified, new camera params: {camera_randomization_params}")
            # Create cameras with randomization information
            for camera_param in camera_randomization_params:
                camera = _create_camera()
                change_camera_params.append({"camera": camera, "randomization": camera_param})
                render_product = rep.create.render_product(camera, (1024, 1024))
                render_list.append(render_product)
            logger.warning(f"Randomization params are : {change_camera_params}")
        else:
            # If not domain randomization on camera, create a regular camera
            camera = _create_camera()
            render_product = rep.create.render_product(camera, (1024, 1024))
            render_list.append(render_product)

        # Initialize and attach writer
        if use_bmw:
            # Create a list containing all the defect names present in scene.
            defect_names = []

            for prim_defect in defect_generation_request.prim_defects:
                for defect in prim_defect.defects:
                    if defect.defect_name not in defect_names:
                        defect_names.append(defect.defect_name)
            rep.WriterRegistry.register(BMWWriter)
            writer = rep.WriterRegistry.get("BMWWriter")
            writer.initialize(output_dir=output_dir, rgb=True, bounding_box_2d_tight=use_bb,semantic_segmentation=use_seg, defects=defect_names)
        else:
            writer = rep.WriterRegistry.get("BasicWriter")
            writer.initialize(output_dir=output_dir, rgb=True, semantic_segmentation=use_seg, bounding_box_2d_tight=use_bb)
        # Attach all render products to the writer
        writer.attach(render_list)

        # Setup randomization
        with rep.trigger.on_frame(num_frames=frames, rt_subframes=rt_subframes):
            # Light domain randomization
            if domain_randomization_request.light_domain_randomization_params.active:
                rep.randomizer.change_light(domain_randomization_request.light_domain_randomization_params)
            # Camera domain randomization
            if domain_randomization_request.camera_domain_randomization_params.active:
                rep.randomizer.change_camera(change_camera_params, prim_defects_path, domain_randomization_request.camera_domain_randomization_params)
            # Defects domain randomization
            for defect_prim_objects in defect_generation_request.prim_defects:
                for defect in defect_prim_objects.defects:
                    rep.randomizer.move_defect(defect_objet=defect, prim_path=defect_prim_objects.prim_path)
                    rep.randomizer.change_defect_image(defect_objet=defect, texture_dir=defect_generation_request.texture_dir)