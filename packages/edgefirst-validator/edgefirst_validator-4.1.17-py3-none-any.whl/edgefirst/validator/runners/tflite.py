from __future__ import annotations

import os
from time import monotonic_ns as clock_now
from typing import TYPE_CHECKING, Any, Tuple

import numpy as np

from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.runners.core import Runner

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import ModelParameters


class TFliteRunner(Runner):
    """
    Loads and runs TensorFlow Lite models for inference.

    Parameters
    ----------
    model: Any
        The is typically the path to the model or the loaded TFLite model.
    parameters: ModelParameters
        These are the model parameters set from the command line.

    Raises
    ------
    ImportError
        Raised if tflite_runtime and TensorFlow is not intalled.
    FileNotFoundError
        Raised if the path to the model does not exist.
    """

    def __init__(
        self,
        model: Any,
        parameters: ModelParameters,
    ):
        super(TFliteRunner, self).__init__(model, parameters)

        try:
            from tflite_runtime.interpreter import Interpreter  # type: ignore
        except ImportError:
            logger("tflite_runtime is not installed. Defaulting to TensorFlow.",
                   code="WARNING")
            try:
                import tensorflow as tf  # type: ignore
                Interpreter = tf.lite.Interpreter
            except ImportError:
                raise ImportError(
                    "TensorFlow or tflite_runtime is needed to run TFLite models.")

        if isinstance(model, str):
            if not os.path.exists(model):
                raise FileNotFoundError(
                    "The model '{}' does not exist.".format(model))

            ext_delegate = self.select_delegates()
            logger(f"Engine: {self.parameters.engine}", code="INFO")

            if ext_delegate:
                self.model = Interpreter(
                    model_path=model,
                    experimental_delegates=[ext_delegate]
                )  # load TFLite model
            else:
                self.model = Interpreter(model_path=model)  # load TFLite model

        self.model.allocate_tensors()  # allocate

        self.input_details = self.model.get_input_details()
        self.type = self.get_input_type()
        self.shape = self.get_input_shape()
        self.parameters.common.dtype = self.type
        self.parameters.common.shape = self.shape

        self.output_details = self.model.get_output_details()
        # Determine the index for the type of outputs.
        self.box_outputs = self.get_box_outputs(self.output_details)
        self.mask_outputs = self.get_mask_outputs(self.output_details)
        self.score_outputs = self.get_score_outputs(self.output_details)
        self.decoded_masks_outputs = self.get_decoded_mask_outputs(
            self.output_details)
        self.class_outputs = self.get_class_outputs(self.output_details)

        self.assign_model_conditions()

        if self.parameters.warmup > 0:
            self.warmup()

    def select_delegates(self) -> Any:
        """
        Specify the delegates to load based on
        the type of engine specified.

        Returns
        -------
        Any
            This is either the loaded delegate object or None
            if it doesn't exist.
        """
        try:  # https://coral.ai/docs/edgetpu/tflite-python/#update-existing-tf-lite-code-for-the-edge-tpu
            from tflite_runtime.interpreter import load_delegate  # type: ignore
        except ImportError:
            try:
                import tensorflow as tf  # type: ignore
                load_delegate = tf.lite.experimental.load_delegate
            except ImportError:
                raise ImportError(
                    "TensorFlow or tflite_runtime is needed to run TFLite models.")

        ext_delegate = None
        if (os.path.exists(self.parameters.engine) and
                self.parameters.engine.endswith(".so")):
            ext_delegate = load_delegate(self.parameters.engine, {})
        elif self.parameters.engine.lower() == "npu":
            if os.path.exists("/usr/lib/libvx_delegate.so"):
                self.parameters.engine = "/usr/lib/libvx_delegate.so"
                ext_delegate = load_delegate(self.parameters.engine, {})
                logger("Using '/usr/lib/libvx_delegate.so' for NPU inference.",
                       code="INFO")
            elif os.path.exists("/usr/lib/libneutron_delegate.so"):
                self.parameters.engine = "/usr/lib/libneutron_delegate.so"
                ext_delegate = load_delegate(self.parameters.engine, {})
                logger("Using '/usr/lib/libneutron_delegate.so' for NPU inference.",
                       code="INFO")
            else:
                logger(
                    "Specified NPU, but cannot find '/usr/lib/libvx_delegate.so'. " +
                    "Specify the path to libvx_delegate.so in your system. " +
                    "Defaulting to use the CPU instead.", code="WARNING")
                self.parameters.engine = "cpu"
        elif self.parameters.engine.lower() == "gpu":
            logger(
                "Inference with the GPU is currently not supported for TFLite. " +
                "Defaulting to use the CPU instead.", code="WARNING")
            self.parameters.engine = "cpu"
        return ext_delegate

    def warmup(self):
        """
        Run model warmup.
        """
        super().warmup()
        times = []

        for _ in range(self.parameters.warmup):
            start = clock_now()
            self.model.invoke()
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
        Run TFLite inference on a single image and record the timings.
        This method does not pad the images to match the input shape of the
        model. This is different to YOLOv5 implementation where images are
        padded: https://github.com/ultralytics/yolov5/blob/master/val.py#L197

        The TFLite runner implementation was taken from::
        https://github.com/ultralytics/yolov5/blob/master/models/common.py#L579

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
        # is TFLite quantized int8 model
        int8 = self.input_details[0]["dtype"] == np.int8
        # is TFLite quantized uint8 model
        uint8 = self.input_details[0]["dtype"] == np.uint8
        self.model.set_tensor(self.input_details[0]['index'], image)

        # Inference
        start = clock_now()
        self.model.invoke()
        infer_ns = clock_now() - start
        self.backbone_timings.append(infer_ns * 1e-6)

        # Postprocessing
        outputs = []
        for output in self.output_details:
            x = self.model.get_tensor(output["index"])
            if (int8 or uint8) and x.dtype != np.float32:
                scale, zero_point = output["quantization"]
                if scale > 0:
                    x = (x.astype(np.float32) - zero_point) * scale  # re-scale
            outputs.append(x)

        # Decode and box timings are measured in this function.
        return self.postprocessing(outputs)

    def get_input_type(self) -> str:
        """
        This returns the input type of the model with shape
        (batch size, channels, height, width) or
        (batch size, height, width, channels).

        Returns
        -------
        str
            The input type of the model.
        """
        for input in self.input_details:
            shape = input["shape"]
            # Detection shapes are in the form (batch size, height, width,
            # channels=3).
            if len(shape) == 4:
                if shape[1] == 3 or shape[-1] == [3]:
                    return input["dtype"].__name__
        return self.input_details[0]["dtype"].__name__

    def get_input_shape(self) -> np.ndarray:
        """
        Grabs the model input shape.

        Returns
        -------
        np.ndarray
            The model input shape (batch size, channels, height, width) or
            (batch size, height, width, channels).
        """
        for input in self.input_details:
            shape = input["shape"]
            # Detection shapes are in the form (batch size, height, width,
            # channels=3).
            if len(shape) == 4:
                if shape[1] == 3 or shape[-1] == [3]:
                    return shape
        # If it does not conform with expected format, return the first
        # element.
        return self.input_details[0]["shape"]
