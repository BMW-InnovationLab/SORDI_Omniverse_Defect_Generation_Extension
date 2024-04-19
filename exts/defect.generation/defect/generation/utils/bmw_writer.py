import time
import asyncio
import json
import io
import os

import omni.kit
import omni.usd
import omni.replicator.core as rep
import numpy as np
from typing import Any, List
from omni.replicator.core import Writer, AnnotatorRegistry, BackendDispatch

class BMWWriter(Writer):
    def __init__(
            self,
            output_dir,
            rgb: bool = True,
            bounding_box_2d_tight: bool = False,
            semantic_segmentation: bool = False,
            image_output_format="png",
            defect: List[str] = []
    ):
        self._output_dir = output_dir
        self._backend = BackendDispatch({"paths": {"out_dir": output_dir}})
        self._frame_id = 0
        self._image_output_format = image_output_format

        self.annotators = []
        self.LABEL = defect
        # RGB
        if rgb:
            self.annotators.append(AnnotatorRegistry.get_annotator("rgb"))

        # Bounding Box 2D
        if bounding_box_2d_tight:
            self.annotators.append(AnnotatorRegistry.get_annotator("bounding_box_2d_tight",
                                                                   init_params={"semanticTypes": ["class"]}))

        # Semantic Segmentation
        if semantic_segmentation:
            self.annotators.append(AnnotatorRegistry.get_annotator("semantic_segmentation",
                                                                   init_params={"colorize": True}))

    def check_bbox_area(self, bbox_data, size_limit):
        length = abs(bbox_data['x_min'] - bbox_data['x_max'])
        width = abs(bbox_data['y_min'] - bbox_data['y_max'])

        area = length * width
        if area > size_limit:
            return True
        else:
            return False

    def write(self, data):
        if "rgb" in data and "bounding_box_2d_tight" in data:
            # Make sure that directories exist
            bbox_dir = os.path.join("labels", "json")
            image_dir =  "images"
            bbox_output_dir = os.path.join(self._output_dir, bbox_dir)
            image_output_dir = os.path.join(self._output_dir, image_dir)
            if not os.path.exists(bbox_output_dir):
                os.makedirs(bbox_output_dir)
            if not os.path.exists(image_output_dir):
                os.makedirs(image_output_dir)

            bbox_data = data["bounding_box_2d_tight"]["data"]
            id_to_labels = data["bounding_box_2d_tight"]["info"]["idToLabels"]
            exists = False
            # Check if a defect exists in this image or not
            for id, labels in id_to_labels.items():
                if labels['class'].split("_")[0] in self.LABEL:
                    exists = True
                    break
            if exists:
                json_data = []
                for bbox in bbox_data:
                    target_bbox_data = {'x_min': bbox['x_min'], 'y_min': bbox['y_min'],
                                        'x_max': bbox['x_max'], 'y_max': bbox['y_max']}
                    id = int(bbox[0])
                    label = id_to_labels[str(id)]['class'].split("_")[0]

                    if self.check_bbox_area(target_bbox_data, 0.5):
                        width = int(abs(target_bbox_data["x_max"] - target_bbox_data["x_min"]))
                        height = int(abs(target_bbox_data["y_max"] - target_bbox_data["y_min"]))

                        if width != 2147483647 and height != 2147483647:
                            coco_bbox_data = {"Id": id,
                                              "ObjectClassName": label,
                                              "Left": int(target_bbox_data["x_min"]),
                                              "Top": int(target_bbox_data["y_min"]),
                                              "Right": int(target_bbox_data["x_max"]),
                                              "Bottom": int(target_bbox_data["y_max"])}
                            json_data.append(coco_bbox_data)

                    # Write the rgb image into a file
                    filepath = os.path.join(image_dir, f"{self._frame_id}.{self._image_output_format}")
                    self._backend.write_image(filepath, data["rgb"])

                    bbox_filepath = os.path.join(bbox_dir, f"{self._frame_id}.json")
    
                    # Write the bbox values to the json file
                    buf = io.BytesIO()
                    buf.write(json.dumps(json_data).encode())
                    self._backend.write_blob(bbox_filepath, buf.getvalue())

        if "rgb" in data and "semantic_segmentation" in data:
            # Make sure that directories exist
            semantic_segmentation_dir =  "semantic_segmentation"
            semantic_segmentation_output_dir = os.path.join(self._output_dir, semantic_segmentation_dir)
            if not os.path.exists(semantic_segmentation_output_dir):
                os.makedirs(semantic_segmentation_output_dir)

            semantic_data = data["semantic_segmentation"]["data"]
            id_to_labels = data["semantic_segmentation"]["info"]["idToLabels"]
            exists = False

            # Check if a defect exists in this image or not
            for id, labels in id_to_labels.items():
                if labels['class'].split("_")[0] in self.LABEL:
                    exists = True
                    break
            if exists:
                numpy_data = semantic_data
                json_data = id_to_labels
                for key, value in json_data.items():
                    if '_' in value['class']:
                        new_class = value['class'].split('_')[0]
                        value['class'] = new_class
                filepath = f"{self._frame_id}"

                # Write the label information to the json file
                buf = io.BytesIO()
                buf.write(json.dumps(json_data).encode())
                self._backend.write_blob(os.path.join(semantic_segmentation_dir, filepath + ".json"), buf.getvalue())

                # Write the semantic data values to the npy file
                with open(os.path.join(semantic_segmentation_output_dir, filepath + ".npy"), 'xb') as f:
                    np.save(f, np.array(numpy_data))
        self._frame_id += 1
