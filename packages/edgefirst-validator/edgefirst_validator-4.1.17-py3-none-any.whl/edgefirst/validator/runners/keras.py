from __future__ import annotations

import os
from time import monotonic_ns as clock_now
from typing import TYPE_CHECKING, Any, Tuple

import numpy as np

from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.runners.core import Runner

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import ModelParameters


class KerasRunner(Runner):
    """
    Loads and runs the Keras (.h5, .keras) models using the TensorFlow library.

    Parameters
    ----------
    model: str or tf.keras.Model
        The path to the model or the loaded keras model.
    parameters: ModelParameters
        These are the model parameters set from the command line.

    Raises
    ------
    ImportError
        Raised if the TensorFlow library is not installed.
    FileNotFoundError
        Raised if the path to the model does not exist.
    """

    def __init__(
        self,
        model: Any,
        parameters: ModelParameters,
    ):
        super(KerasRunner, self).__init__(model, parameters)

        # Load Argmax dependency needed for keras
        try:
            from deepview.modelpack.utils.argmax import Argmax
        except ImportError:
            pass

        try:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf  # type: ignore
        except ImportError:
            raise ImportError(
                "TensorFlow is needed to run keras models.")

        if isinstance(model, str):
            if not os.path.exists(model):
                raise FileNotFoundError(
                    "The model '{}' does not exist.".format(model))

            if os.path.exists(os.path.join(model, "saved_model.pb")):
                self.model = tf.saved_model.load(model)
                self.inputs = self.model.signatures["serving_default"].inputs
                self.outputs = self.model.signatures["serving_default"].outputs
            else:
                self.model = tf.keras.models.load_model(model, compile=False)
                self.outputs = self.model.output
                self.inputs = self.model.input

        self.type = self.get_input_type()
        self.shape = self.get_input_shape()
        # Avoid shape [None, height, width, 3]
        self.shape = np.array(
            [dim if dim is not None else 1 for dim in self.shape])
        self.parameters.common.dtype = self.type
        self.parameters.common.shape = self.shape

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

    def warmup(self):
        """
        Run model warmup.
        """
        super().warmup()
        times = []

        # Produce a sample image of zeros.
        image = np.zeros(self.shape, self.type)

        for _ in range(self.parameters.warmup):
            start = clock_now()
            self.model(image)
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
        Run Keras inference on a single image and record the timings.

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

        try:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf  # type: ignore
        except ImportError:
            raise ImportError(
                "TensorFlow is needed to run keras models.")

        # Preprocessing
        image = self.preprocessing(
            image=image,
            shapes=shapes,
            ratio=ratio,
            image_shape=image_shape
        )

        # Inference
        start = clock_now()
        outputs = self.model(image)
        infer_ns = clock_now() - start
        self.backbone_timings.append(infer_ns * 1e-6)

        # Postprocessing
        outputs = [out.numpy() if isinstance(out, tf.Tensor)
                   else out for out in outputs]
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
        try:
            return self.model.input.dtype.as_numpy_dtype
        except AttributeError:
            for input in self.inputs:
                shape = input.shape
                if len(shape) == 4:
                    if shape[1] == 3 or shape[-1] == [3]:
                        return input.dtype
            return self.inputs[0].dtype

    def get_input_shape(self) -> np.ndarray:
        """
        Grabs the model input shape.

        Returns
        -------
        np.ndarray
            The model input shape (batch size, channels, height, width) or
            (batch size, height, width, channels).
        """
        try:
            return self.model.input.shape
        except AttributeError:
            for input in self.inputs:
                shape = input.shape
                if len(shape) == 4:
                    if shape[1] == 3 or shape[-1] == [3]:
                        return shape
            return self.inputs[0].shape
