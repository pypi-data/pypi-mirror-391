from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, List, Tuple
from time import monotonic_ns as clock_now

import numpy as np

from edgefirst.validator.datasets.utils.transformations import (xyxy2yolo,
                                                                xyxy2xywh,
                                                                reverse_normalization)
from edgefirst.validator.runners.processing.preprocess import preprocess
from edgefirst.validator.runners.processing.postprocess import (process_yolox,
                                                                process_yolov,
                                                                process_modelpack,
                                                                process_yolov_segmentation)
from edgefirst.validator.runners.processing.decode import decode_modelpack_outputs

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import ModelParameters


class Runner:
    """
    Abstract class that provides a template for the other runner classes.

    Parameters
    ----------
    model: Any
        This is typically the path to the model file or a loaded model.
    parameters: Parameters
        These are the model parameters set from the command line.

    Raises
    ------
    FileNotFoundError
        Raised if the path to the model does not exist.
    """

    def __init__(self, model: Any, parameters: ModelParameters):
        self.model = model
        self.parameters = parameters

        # The preprocessed image (letterbox, padded, resized, etc).
        self.image = None
        self.shape = None  # The model input dimensions
        self.image_shape = None  # The original image dimensions.
        # The ratio to adjust bounding boxes to image padding.
        self.ratio = 1.0
        self.num_boxes = 0  # The number of boxes in the model output shape.
        # This is needed to rescale bounding boxes based
        # on the letter box image preprocessing.
        self.shapes = [
            [
                [0, 0],  # imgsz (model input shape) [height, width]
                # ratio_pad [[scale y, scale x], [pad w, pad h]]
                [[1.0, 1.0], [0.0, 0.0]]
            ],
            [1.0, 1.0]  # label ratio [x, y]
        ]
        self.graph_name = "main_graph"

        self.box_outputs = None
        self.mask_outputs = None
        self.score_outputs = None
        self.decoded_masks_outputs = None
        self.class_outputs = None

        self.read_timings = list()
        self.load_timings = list()
        self.backbone_timings = list()
        self.decode_timings = list()
        self.box_timings = list()

    def warmup(self):
        """
        Run the imports to avoid having to include this operations
        during box timing measurements.
        """
        if self.parameters.nms == "torch":
            try:
                import torch  # type: ignore
                import torchvision  # type: ignore
            except ImportError:
                raise ImportError(
                    "Torch and Torchvision is needed to use `torch_nms`.")
        elif self.parameters.nms == "tensorflow":
            try:
                import tensorflow as tf  # type: ignore
            except ImportError:
                raise ImportError(
                    "TensorFlow is needed to use `tensorflow_nms`.")

        try:
            import cv2  # type: ignore
        except ImportError:
            pass

    def get_box_outputs(
        self,
        outputs: Union[List[dict], List[np.ndarray]]
    ) -> Union[int, None]:
        """
        Get the index of the bounding box outputs from the model.
        Checking for Ultralytics and ModelPack variations.

        Parameters
        ----------
        outputs: Union[List[dict], List[np.ndarray]]
            This is either a List[dict] from a TFLite output details
            or a List[np.ndarray] containing the shapes from the model outputs.

        Returns
        -------
        Union[int, None]
            The index is returned if the bounding box output shape exists.
            Otherwise None is returned.
        """
        # Checking ModelPack outputs.
        # Box outputs is in this variation [   1, 6000,    1,    4]
        for i, output in enumerate(outputs):
            if isinstance(output, dict):
                shape = output["shape"]
            else:
                shape = output.shape
            if (len(shape) == 4 and shape[-2] == 1) or (len(shape) == 3
                                                        and shape[-1] == 4):
                self.num_boxes = shape[1]
                return i
        return None

    def get_mask_outputs(
        self,
        outputs: Union[List[dict], List[np.ndarray]]
    ) -> Union[int, None]:
        """
        Get the index of the encoded mask outputs from the model.
        Checking for ModelPack variations only.

        Parameters
        ----------
        outputs: Union[List[dict], List[np.ndarray]]
            This is either a List[dict] from a TFLite output details
            or a List[np.ndarray] containing the shapes from the model outputs.

        Returns
        -------
        Union[int, None]
            The index is returned if the mask output shape exists.
            Otherwise None is returned.
        """
        for i, output in enumerate(outputs):
            if isinstance(output, dict):
                shape = output["shape"]
            else:
                shape = output.shape
            if len(shape) == 4 and shape[-2] != 1:
                return i
        return None

    def get_score_outputs(
        self,
        outputs: Union[List[dict], List[np.ndarray]]
    ) -> Union[int, None]:
        """
        Get the index of the score outputs from the model.
        Checking for ModelPack variations only.

        Parameters
        ----------
        outputs: Union[List[dict], List[np.ndarray]]
            This is either a List[dict] from a TFLite output details
            or a List[np.ndarray] containing the shapes from the model outputs.

        Returns
        -------
        Union[int, None]
            The index is returned if the score output shape exists.
            Otherwise None is returned.
        """
        # Score outputs are in these variations
        # [   1, 6000,   14], [1, 37, 8400], [1, 25200, 85]
        for i, output in enumerate(outputs):
            if isinstance(output, dict):
                shape = output["shape"]
            else:
                shape = output.shape
            if self.num_boxes != 0:
                if len(shape) == 3 and shape[1] == self.num_boxes:
                    return i
                # MobileNet SSD [1, 10]
                elif len(shape) == 2 and i == 2 and shape[1] == self.num_boxes:
                    return i
            else:
                if len(shape) == 3:
                    if ((shape[1] > shape[2]) and (shape[1] / shape[2] > 5)) or (
                            (shape[1] < shape[2]) and (shape[2] / shape[1] > 5)):
                        return i
        return None

    def get_decoded_mask_outputs(
        self,
        outputs: Union[List[dict], List[np.ndarray]]
    ) -> Union[dict, None]:
        """
        Get the index of the decoded mask outputs from the model.
        Checking for ModelPack variations only.

        Parameters
        ----------
        outputs: Union[List[dict], List[np.ndarray]]
            This is either a List[dict] from a TFLite output details
            or a List[np.ndarray] containing the shapes from the model outputs.

        Returns
        -------
        Union[int, None]
            The index is returned if the decoded mask output shape exists.
            Otherwise None is returned.
        """
        # Segmentation will contain both encoded and decoded masks.
        if len(outputs) > 1:
            for i, output in enumerate(outputs):
                if isinstance(output, dict):
                    shape = output["shape"]
                else:
                    shape = output.shape
                if self.num_boxes != 0:
                    if len(shape) == 3 and shape[1] != self.num_boxes:
                        return i
                else:
                    if len(shape) == 3:
                        if ((shape[1] >= shape[2]) and (shape[1] / shape[2] < 5)) or (
                                (shape[1] <= shape[2]) and (shape[2] / shape[1] < 5)):
                            return i
        return None

    def get_class_outputs(
        self,
        outputs: Union[List[dict], List[np.ndarray]]
    ) -> Union[int, None]:
        """
        Get the index of the class outputs. This is primarily seen
        in MobileNet SSD models.

        Parameters
        ----------
        outputs: Union[List[dict], List[np.ndarray]]
            This is either a List[dict] from a TFLite output details
            or a List[np.ndarray] containing the shapes from the model outputs.

        Union[int, None]
            The index is returned if the class output shape exists.
            Otherwise None is returned.
        """
        # Score outputs are in these variations: [1, 10].
        for i, output in enumerate(outputs):
            if isinstance(output, dict):
                shape = output["shape"]
            else:
                shape = output.shape
            if self.num_boxes != 0:
                # MobileNet SSD [1, 10]
                if len(shape) == 2 and i == 1 and shape[1] == self.num_boxes:
                    return i
        return None

    def assign_model_conditions(self):
        """
        Determine if the model is detection, segmentation, or both.
        Also determine if the model is semantic or instance segmentation.
        Also these conditions can be accessed from the model metadata if it
        exists.
        """
        # Condition for ModelPack models (semantic segmentation).
        if not (self.score_outputs is not None and self.box_outputs is None):
            self.parameters.common.semantic = True

        # Determine the type of the model as
        # either Multitask, Segmentation, or Detection.
        if self.box_outputs is not None or self.score_outputs is not None:
            self.parameters.common.with_boxes = True
        else:
            self.parameters.common.with_boxes = False

        if (self.mask_outputs is not None or
                self.decoded_masks_outputs is not None):
            self.parameters.common.with_masks = True
        else:
            self.parameters.common.with_masks = False

        # Read from the Model Metadata.
        if self.parameters.metadata is not None:
            if "outputs" in self.parameters.metadata.keys():
                # Resetting conditions and relying only on metadata for the types.
                self.parameters.common.with_boxes = False
                self.parameters.common.with_masks = False
                for output_details in self.parameters.metadata["outputs"]:
                    if output_details["decoder"] == "yolov8":
                        if output_details["type"] in ["masks", "segmentation"]:
                            self.parameters.common.with_masks = True
                        else:
                            self.parameters.common.with_masks = False
                        self.parameters.common.with_boxes = True
                    else:
                        if output_details["type"] in [
                            "boxes", "scores", "detection"]:
                            self.parameters.common.with_boxes = True
                        elif output_details["type"].lower() in ["masks", "segmentation"]:
                            self.parameters.common.with_masks = True

    def run_single_instance(
        self,
        image: np.ndarray,
        shapes: Tuple[tuple] = None,
        ratio: float = 1.0,
        image_shape: tuple = None
    ) -> Any:
        """Abstract Method"""
        pass

    def preprocessing(
        self,
        image: np.ndarray,
        shapes: Tuple[tuple] = None,
        ratio: float = 1.0,
        image_shape: tuple = None
    ) -> np.ndarray:
        """
        Run postprocessing of the images and return
        the postprocessed image.

        Parameters
        ----------
        image: np.ndarray
            The image input after being preprocessed if caching
            is set. If caching is False, this image does not
            apply any transformations. Typically this is an RGB image array.
        shapes: Tuple[tuple]
            This is used to scale the bounding boxes of the ground
            truth and the model detections based on the letterbox
            transformation. This is needed in case the images are preprocessed.
            ((pad image height, pad image width), (ratio y, ratio x), (pad x, pad y)).
        ratio: float
            Rescaling factor used for the bounding boxes.
            This is needed in case the images are preprocessed.
        image_shape: tuple
            The original image dimensions.
            This is needed in case the images are preprocessed.

        Returns
        -------
        np.ndarray
            Postprocessed image that has been resized, normalized,
            and type casted to the input requirements of the model.
        """

        # Preprocessing
        # If the dataset was cached, the images are already preprocessed.
        if not self.parameters.common.cache:
            start = clock_now()
            image, shapes, ratio, image_shape = preprocess(
                image=image,
                shape=self.shape,
                input_type=self.type,
                preprocessing=self.parameters.common.preprocessing,
                normalization=self.parameters.common.norm
            )
            load_ns = clock_now() - start
            self.load_timings.append(load_ns * 1e-6)

        # Store the image with letterbox, padding, or resized transformations.
        self.image = reverse_normalization(image.copy(),
                                           normalization=self.parameters.common.norm)
        # Tranpose the image from (3, height, width) to (height, width, 3).
        if self.image.shape[0] in [2, 3, 4]:
            self.image = np.transpose(self.image, axes=[1, 2, 0])
        # Remove alpha channel as pillow can't handle saving RGBA JPGs.
        if self.image.shape[-1] == 4:
            self.image = self.image[:, :, :3]
        self.shapes = shapes
        self.ratio = ratio
        self.image_shape = image_shape

        if hasattr(self, "input_details"):
            # is TFLite quantized int8 model
            int8 = self.input_details[0]["dtype"] == np.int8
            # is TFLite quantized uint8 model
            uint8 = self.input_details[0]["dtype"] == np.uint8
            if self.parameters.common.norm != "raw":
                if int8 or uint8:
                    scale, zero_point = self.input_details[0]["quantization"]
                    image = np.round(image / scale + zero_point)  # de-scale
            if int8 or uint8:
                image = image.astype(
                    np.uint8) if uint8 else image.astype(
                    np.int8)
            else:
                image = image.astype(np.float32)
        return image

    def postprocessing(self, outputs: Union[list, np.ndarray]) -> Any:
        """
        Postprocess outputs into boxes, scores, labels or masks.
        This method will perform NMS operations where the outputs
        will be transformed into the following format.

        Models trained using ModelPack separates the outputs and
        directly return the NMS bounding boxes, scores, and
        labels as described below.

        Models converted in YOLOv5 will be a list of length 1 which
        has a shape of (1, number of boxes, 6) and formatted as
        [[[xmin, ymin, xmax, ymax, confidence, label], [...], ...]].

        Models converted in YOLOv7 will directly extract the
        bounding boxes, scores, and labels from the output.

        Parameters
        ----------
        outputs: Union[list, np.ndarray]
            ModelPack outputs will be a list with varying lengths
            which could either contain bounding boxes, labels, scores,
            or masks (encoded and decoded).

            Models converted in YOLOv5 has the following shape
            (batch size, number of boxes, number of classes).

            Models converted in YOLOv7 will already have NMS embedded. The
            output has a shape of (number of boxes, 7) and formatted as
            [[batch_id, xmin, ymin, xmax, ymax, cls, score], ...].

        Returns
        -------
        Any
            This could either return detection outputs after NMS.
                np.ndarray
                    The prediction bounding boxes.. [[box1], [box2], ...].
                np.ndarray
                    The prediction labels.. [cl1, cl2, ...].
                np.ndarray
                    The prediction confidence scores.. [score, score, ...]
                    normalized between 0 and 1.
            This could also return segmentation masks.
                np.ndarray
        """
        if isinstance(outputs, (list, tuple)):
            output = outputs[0] if len(outputs) == 1 else outputs
        else:
            output = outputs

        masks = None
        output = output.numpy() if not isinstance(
            output, (np.ndarray, list)) else output

        if self.parameters.metadata is not None:
            if self.parameters.metadata["outputs"][0]["decoder"] == "modelpack":
                start_decode = clock_now()
                decoded_outputs = decode_modelpack_outputs(
                    outputs=output,
                    metadata=self.parameters.metadata,
                )
                if decoded_outputs is not None:
                    self.box_outputs = decoded_outputs["boxes"]
                    self.score_outputs = decoded_outputs["scores"]
                    self.mask_outputs = decoded_outputs["segmentation"]
                    self.decoded_masks_outputs = decoded_outputs["masks"]
                    output = decoded_outputs["outputs"]
                decode_ns = clock_now() - start_decode
                self.decode_timings.append(decode_ns * 1e-6)

        # YOLO models
        if self.score_outputs is not None and self.box_outputs is None:
            # YOLOv8 Segmentation Model
            if self.mask_outputs is not None or self.decoded_masks_outputs is not None:
                start_seg = clock_now()
                boxes, classes, scores, masks = process_yolov_segmentation(
                    output=output,
                    outputs=[self.box_outputs, self.score_outputs,
                             self.mask_outputs, self.decoded_masks_outputs],
                    input_shape=self.shape,
                    nc=len(self.parameters.labels),
                    iou_thr=self.parameters.iou_threshold,
                    score_thr=self.parameters.score_threshold,
                    max_detections=self.parameters.max_detections,
                    nms_type=self.parameters.nms,
                    method=self.parameters.common.method,
                    box_format=self.parameters.box_format
                )
                box_ns = clock_now() - start_seg
                self.box_timings.append(box_ns * 1e-6)

            # YOLOx model
            elif (self.graph_name not in ["main_graph", "torch_jit", "tf2onnx"] or
                  output.shape[1] == 8400):
                start_yolox = clock_now()
                boxes, classes, scores = process_yolox(
                    output=output,
                    input_shape=self.shape,
                    ratio=self.ratio,
                    image_shape=self.image_shape,
                    iou_thr=self.parameters.iou_threshold,
                    score_thr=self.parameters.score_threshold,
                    max_detections=self.parameters.max_detections,
                    nms_type=self.parameters.nms,
                    box_format=self.parameters.box_format
                )
                self.shapes = None
                box_ns = clock_now() - start_yolox
                self.box_timings.append(box_ns * 1e-6)
            # YOLOv5, YOLOv8, YOLOv11 models
            else:
                start_yolo = clock_now()
                boxes, classes, scores = process_yolov(
                    output=output,
                    input_shape=self.shape,
                    nc=len(self.parameters.labels),
                    iou_thr=self.parameters.iou_threshold,
                    score_thr=self.parameters.score_threshold,
                    max_detections=self.parameters.max_detections,
                    nms_type=self.parameters.nms,
                    method=self.parameters.common.method,
                    box_format=self.parameters.box_format
                )
                box_ns = clock_now() - start_yolo
                self.box_timings.append(box_ns * 1e-6)
        # MobileNet SSD
        elif self.class_outputs is not None:
            start_mobile = clock_now()
            boxes, classes, scores, _ = output

            boxes = np.squeeze(boxes)
            classes = np.squeeze(classes).astype(np.int32)
            scores = np.squeeze(scores)

            if self.parameters.box_format == "yolo":
                boxes = xyxy2yolo(boxes)
            elif self.parameters.box_format == "coco":
                boxes = xyxy2xywh(boxes)
            box_ns = clock_now() - start_mobile
            self.box_timings.append(box_ns * 1e-6)
        # ModelPack models separates the outputs.
        else:
            start_mpk = clock_now()
            boxes, classes, scores, masks = process_modelpack(
                output=output,
                outputs=[self.box_outputs, self.score_outputs,
                         self.mask_outputs, self.decoded_masks_outputs],
                iou_thr=self.parameters.iou_threshold,
                score_thr=self.parameters.score_threshold,
                max_detections=self.parameters.max_detections,
                nms_type=self.parameters.nms,
                box_format=self.parameters.box_format
            )
            box_ns = clock_now() - start_mpk
            self.box_timings.append(box_ns * 1e-6)

        if self.parameters.common.with_boxes and self.parameters.common.with_masks:
            if self.parameters.label_offset != 0:
                classes += self.parameters.label_offset
            return boxes, classes, scores, masks
        elif self.parameters.common.with_boxes:
            if self.parameters.label_offset != 0:
                classes += self.parameters.label_offset
            return boxes, classes, scores
        else:
            return masks

    def get_input_type(self) -> str:
        """Abstract Method"""
        pass

    def get_input_shape(self) -> np.ndarray:
        """Abstract Method"""
        pass

    def timings(self) -> dict:
        """
        Returns a summary of all the timings:
        (mean, avg, max) of (load, inference, box).

        Returns
        -------
        dict
            The timings in milliseconds.

            .. code-block:: python

                {
                    'min_read_time': minimum time to read the input,
                    'max_read_time': maximum time to read the input,
                    'min_load_time': minimum time to preprocess the input,
                    'max_load_time': maximum time to preprocess the input,
                    'min_backbone_time': minimum time to run the model,
                    'max_backbone_time': maximum time to run the model,
                    'min_decode_time': minimum time to decode the outputs,
                    'max_decode_time': maximum time to decode the outputs,
                    'min_box_time': minimum time to process the outputs,
                    'max_box_time': maximum time to process the outputs,
                    'avg_read_time': average time to read the input,
                    'avg_load_time': average time to preprocess the input,
                    'avg_backbone_time': average time to run the model,
                    'avg_decode_time': average time to decode the outputs,
                    'avg_box_time': average time to process the outputs,
                }
        """
        # Remove the first value as an outlier.
        self.read_timings = self.read_timings[1:]
        self.load_timings = self.load_timings[1:]
        self.backbone_timings = self.backbone_timings[1:]
        self.decode_timings = self.decode_timings[1:]
        self.box_timings = self.box_timings[1:]

        return {
            'min_read_time': (np.min(self.read_timings)
                              if len(self.read_timings) else 0),
            'max_read_time': (np.max(self.read_timings)
                              if len(self.read_timings) else 0),
            'min_load_time': (np.min(self.load_timings)
                              if len(self.load_timings) else 0),
            'max_load_time': (np.max(self.load_timings)
                              if len(self.load_timings) else 0),
            'min_backbone_time': (np.min(self.backbone_timings)
                                  if len(self.backbone_timings) else 0),
            'max_backbone_time': (np.max(self.backbone_timings)
                                  if len(self.backbone_timings) else 0),
            'min_decode_time': (np.min(self.decode_timings)
                                if len(self.decode_timings) else 0),
            'max_decode_time': (np.max(self.decode_timings)
                                if len(self.decode_timings) else 0),
            'min_box_time': (np.min(self.box_timings)
                             if len(self.box_timings) else 0),
            'max_box_time': (np.max(self.box_timings)
                             if len(self.box_timings) else 0),
            'avg_read_time': (np.mean(self.read_timings)
                              if len(self.read_timings) else 0),
            'avg_load_time': (np.mean(self.load_timings)
                              if len(self.load_timings) else 0),
            'avg_backbone_time': (np.mean(self.backbone_timings)
                                  if len(self.backbone_timings) else 0),
            'avg_decode_time': (np.mean(self.decode_timings)
                                if len(self.decode_timings) else 0),
            'avg_box_time': (np.mean(self.box_timings)
                             if len(self.box_timings) else 0),
        }
