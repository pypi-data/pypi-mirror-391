from __future__ import annotations

import os
import ctypes
from time import monotonic_ns as clock_now
from typing import TYPE_CHECKING, Any, Tuple

import numpy as np

from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.runners.core import Runner

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import ModelParameters


class ONNXRunner(Runner):
    """
    Loads and runs ONNX models for inference.

    Parameters
    ----------
    model: Any
        This is typically the path to the model or the loaded ONNX model.
    parameters: ModelParameters
        These are the model parameters set from the command line.

    Raises
    ------
    ImportError
        Missing onnxruntime library.
    FileNotFoundError
        Raised if the path to the model does not exist.
    """

    def __init__(
        self,
        model: Any,
        parameters: ModelParameters,
    ):
        super(ONNXRunner, self).__init__(model, parameters)

        try:
            import onnxruntime
        except ImportError:
            raise ImportError(
                "onnxruntime or onnxruntime-gpu is needed to run ONNX models.")

        if isinstance(model, str):
            if not os.path.exists(model):
                raise FileNotFoundError(
                    "The model '{}' does not exist.".format(model))

            providers = self.select_providers()
            logger(f"Selected Providers: {providers}", code="INFO")
            self.model = onnxruntime.InferenceSession(
                model, providers=providers)

        self.type = self.get_input_type()
        self.shape = self.get_input_shape()

        if "float" in self.type:
            self.parameters.common.dtype = "float32"
        else:
            self.parameters.common.dtype = self.type

        self.parameters.common.shape = self.shape

        self.graph_name = self.model.get_modelmeta().graph_name
        self.output_names = [x.name for x in self.model.get_outputs()]
        self.outputs = self.model.get_outputs()

        # Determine the index for the type of outputs.
        self.box_outputs = self.get_box_outputs(self.outputs)
        self.mask_outputs = self.get_mask_outputs(self.outputs)
        self.score_outputs = self.get_score_outputs(self.outputs)
        self.decoded_masks_outputs = self.get_decoded_mask_outputs(
            self.outputs)
        self.class_outputs = self.get_class_outputs(self.outputs)

        self.assign_model_conditions()

        if self.parameters.warmup > 0:
            self.warmup()

    @staticmethod
    def check_tensorrt_runtime() -> list:
        """
        The following libraries are needed to run ONNX
        with TensorrtExecutionProvider.

        - "libnvinfer.so"
        - "libnvinfer_plugin.so"
        - "libnvonnxparser.so"

        Returns
        -------
        list
            A list of the libraries that are missing.
        """
        required_libs = ["libnvinfer.so",
                         "libnvinfer_plugin.so", "libnvonnxparser.so"]
        missing = []
        for lib in required_libs:
            try:
                ctypes.CDLL(lib)
            except OSError:
                missing.append(lib)
        return missing

    def select_providers(self) -> list:
        """
        Specify the providers to load based on
        the type of engine specified.

        Returns
        -------
        list
            A list of the selected providers to deploy.
        """
        import onnxruntime

        selected_providers = ["CPUExecutionProvider"]
        available_providers = onnxruntime.get_available_providers()
        if self.parameters.engine.lower() == "npu":
            preferred_providers = ["NnapiExecutionProvider",
                                   "VsiNpuExecutionProvider",
                                   "TensorrtExecutionProvider",
                                   "CUDAExecutionProvider",
                                   "CPUExecutionProvider"]
            selected_providers = []
            for i, provider in enumerate(preferred_providers):
                if provider in available_providers:
                    if provider == "TensorrtExecutionProvider":
                        missing_libraries = self.check_tensorrt_runtime()
                        if missing_libraries:
                            logger(f"The libraries {missing_libraries} are " +
                                   "needed for TensorrtExecutionProvider. " +
                                   f"Defaulting to {preferred_providers[i+1]}.",
                                   code="WARNING")
                            continue
                    selected_providers.append(provider)
                else:
                    logger(f"{provider} is not present in the system. " +
                           f"Defaulting to {preferred_providers[i+1]}.",
                           code="WARNING")
            if selected_providers in [["TensorrtExecutionProvider",
                                       "CUDAExecutionProvider",
                                       "CPUExecutionProvider"],
                                      ["CUDAExecutionProvider",
                                       "CPUExecutionProvider"]]:
                self.parameters.engine = "gpu"
            elif selected_providers == ["CPUExecutionProvider"]:
                self.parameters.engine = "cpu"
        elif self.parameters.engine.lower() == "gpu":
            preferred_providers = ["TensorrtExecutionProvider",
                                   "CUDAExecutionProvider",
                                   "CPUExecutionProvider"]
            selected_providers = []
            for i, provider in enumerate(preferred_providers):
                if provider in available_providers:
                    if provider == "TensorrtExecutionProvider":
                        missing_libraries = self.check_tensorrt_runtime()
                        if missing_libraries:
                            logger(f"The libraries {missing_libraries} are " +
                                   "needed for TensorrtExecutionProvider. " +
                                   f"Defaulting to {preferred_providers[i+1]}.",
                                   code="WARNING")
                            continue
                    selected_providers.append(provider)
                else:
                    logger(f"{provider} is not present in the system. " +
                           f"Defaulting to {preferred_providers[i+1]}.",
                           code="WARNING")
            if selected_providers == ["CPUExecutionProvider"]:
                self.parameters.engine = "cpu"
                logger(
                    "TensorrtExecutionProvider and CUDAExecutionProvider is " +
                    "not present in the system. Defaulting to CPUExecutionProvider.",
                    code="WARNING")
        return selected_providers

    def warmup(self):
        """
        Run model warmup.
        """
        super().warmup()
        times = []

        # Produce a sample image of zeros.
        image = np.zeros(self.shape)
        if "float32" in self.type:
            image = image.astype(np.float32)
        elif "float16" in self.type:
            image = image.astype(np.float16)
        elif "uint8" in self.type:
            image = np.array(image, dtype=np.uint8)
        elif "int8" in self.type:
            image = image.astype(np.int8)
        elif "uiint32" in self.type:
            image = np.array(image, dtype=np.uint32)
        else:
            image = image.astype(np.float32)

        for _ in range(self.parameters.warmup):
            start = clock_now()
            self.model.run(self.output_names,
                           {self.model.get_inputs()[0].name: image})
            stop = clock_now() - start
            times.append(stop * 1e-6)

        message = "model warmup took %f ms (%f ms avg)" % (np.sum(times),
                                                           np.average(times))
        logger(message, code="INFO")

    def run_single_instance(
        self,
        image: np.ndarray,
        shapes: Tuple[tuple] = None,
        ratio: float = 1.0,
        image_shape: tuple = None
    ) -> Any:
        """
        Run ONNX inference on a single image and record the timings.
        This method does not pad the images to match the input shape of the
        model. This is different to YOLOv5 implementation where images are
        padded: https://github.com/ultralytics/yolov5/blob/master/val.py#L197

        The ONNX runner implementation was taken from::
        https://github.com/ultralytics/yolov5/blob/master/models/common.py#L487

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
        # Preprocessing
        image = self.preprocessing(
            image=image,
            shapes=shapes,
            ratio=ratio,
            image_shape=image_shape
        )

        # Inference
        start = clock_now()
        outputs = self.model.run(self.output_names,
                                 {self.model.get_inputs()[0].name: image})
        infer_ns = clock_now() - start
        self.backbone_timings.append(infer_ns * 1e-6)

        # Postprocessing
        # An output with 7 columns refers to
        # batch_id, xmin, ymin, xmax, ymax, cls, score.
        # Otherwise it is batch_size, number of boxes, number of classes
        # which needs external NMS.
        # Decode and box timings are measured in this function.
        return self.postprocessing(outputs)

    def get_input_type(self) -> str:
        """
        This returns the input type of the model for the
        input with shape in the form
        (batch size, channels, height, width) or
        (batch size, height, width, channels).

        Returns
        -------
        str
            The input type of the model.
        """
        for input in self.model.get_inputs():
            if len(input.shape) == 4:
                if input.shape[1] == 3 or input.shape[-1] == 3:
                    return input.type
        return self.model.get_inputs()[0].type

    def get_input_shape(self) -> np.ndarray:
        """
        This fetches the model input shape.

        Returns
        -------
        np.ndarray
            The model input shape
            (batch size, channels, height, width) or
            (batch size, height, width, channels).
        """
        for input in self.model.get_inputs():
            if len(input.shape) == 4:
                if input.shape[1] == 3 or input.shape[-1] == 3:
                    return input.shape
        return self.model.get_inputs()[0].shape

    def get_metadata(self) -> dict:
        """
        This fetches the model metadata containing stride
        and label name mapping.

        Returns
        -------
        dict
            Contains the model stride and the label mappings.
        """
        return self.model.get_modelmeta().custom_metadata_map
