from __future__ import annotations

import json
from time import monotonic_ns as clock_now
from typing import TYPE_CHECKING, Any, Tuple

import numpy as np

from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.runners.core import Runner

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import ModelParameters


class TensorRTRunner(Runner):
    """
    Loads and runs TensorRT Engines (.engine, .trt).  These models
    are intended to be deployed on a device with a dedicated GPU.
    This implementation was taken from the following sources:
    https://github.com/NVIDIA/TensorRT/blob/main/samples/python/efficientdet/infer.py
    https://github.com/ultralytics/ultralytics/blob/main/ultralytics/nn/autobackend.py#L326

    Parameters
    ----------
    model: Any
        This is typically the path to the model or the loaded TensorRT model.
    parameters: ModelParameters
        These are the model parameters set from the command line.

    Raises
    ------
    ImportError
        Missing tensorrt library.
    FileNotFoundError
        Raised if the path to the model does not exist.
    """

    def __init__(
        self,
        model: Any,
        parameters: ModelParameters,
    ):
        super(TensorRTRunner, self).__init__(model, parameters)

        try:
            import tensorrt as trt
        except ImportError:
            raise ImportError(
                "tensorrt is needed to run TensorRT models.")
        try:
            import pycuda.driver as cuda  # type: ignore
        except ImportError:
            raise ImportError(
                "pycuda is needed to perform memory allocations for TensorRT.")

        # Use autoprimaryctx if available (pycuda >= 2021.1) to
        # prevent issues with other modules that rely on the primary
        # device context.
        try:
            import pycuda.autoprimaryctx  # type: ignore
        except ModuleNotFoundError:
            try:
                import pycuda.autoinit  # type: ignore
            except ImportError:
                raise ImportError(
                    "supported NVIDIA GPU device is needed.")

        # TensorRT are intended to run on the GPU.
        self.parameters.engine = "gpu"
        self.logger = trt.Logger(trt.Logger.INFO)
        trt.init_libnvinfer_plugins(self.logger, namespace="")

        # Read file
        if isinstance(model, str):
            with open(model, "rb") as f, trt.Runtime(self.logger) as runtime:
                assert runtime
                try:
                    meta_len = int.from_bytes(
                        f.read(4), byteorder="little")  # read metadata length
                    metadata = json.loads(
                        f.read(meta_len).decode("utf-8"))  # read metadata
                    dla = metadata.get("dla", None)
                    if dla is not None:
                        runtime.DLA_core = int(dla)
                except UnicodeDecodeError:
                    # engine file may lack embedded Ultralytics metadata
                    f.seek(0)
                self.model = runtime.deserialize_cuda_engine(
                    f.read())  # read engine
                assert self.model

        self.context = self.model.create_execution_context()
        assert self.context

        self.output_names = []
        self.outputs = []
        self.inputs = []
        self.allocations = []

        is_trt10 = not hasattr(self.model, "num_bindings")
        num = range(
            self.model.num_io_tensors) if is_trt10 else range(
            self.model.num_bindings)

        for i in num:
            if is_trt10:
                name = self.model.get_tensor_name(i)
                dtype = np.dtype(trt.nptype(self.model.get_tensor_dtype(name)))
                shape = tuple(self.context.get_tensor_shape(name))
                is_input = self.model.get_tensor_mode(
                    name) == trt.TensorIOMode.INPUT
                if is_input:
                    if -1 in tuple(self.model.get_tensor_shape(name)):
                        self.context.set_input_shape(
                            name, tuple(self.model.get_tensor_profile_shape(name, 0)[1]))
                else:
                    self.output_names.append(name)
                shape = tuple(self.context.get_tensor_shape(name))
            else:  # TensorRT < 10.0
                name = self.model.get_binding_name(i)
                dtype = np.dtype(trt.nptype(self.model.get_binding_dtype(i)))
                is_input = self.model.binding_is_input(i)
                if is_input:
                    if -1 in tuple(self.model.get_binding_shape(i)):  # dynamic
                        self.context.set_binding_shape(
                            i, tuple(self.model.get_profile_shape(0, i)[1]))
                else:
                    self.output_names.append(name)
                shape = tuple(self.context.get_binding_shape(i))

            size = dtype.itemsize
            for s in shape:
                size *= s
            allocation = cuda.mem_alloc(size)
            host_allocation = None if is_input else np.zeros(shape, dtype)

            binding = {
                "index": i,
                "name": name,
                "dtype": dtype,
                "shape": list(shape),
                "allocation": allocation,
                "host_allocation": host_allocation,
            }

            self.allocations.append(allocation)
            if is_input:
                self.inputs.append(binding)
            else:
                self.outputs.append(binding)

        assert len(self.inputs) > 0
        assert len(self.outputs) > 0
        assert len(self.allocations) > 0

        self.shape = self.get_input_shape()
        self.type = self.get_input_type()
        self.parameters.common.shape = self.shape
        outputs = [np.zeros(out["shape"], np.dtype(out["dtype"]))
                   for out in self.outputs]

        # Determine the index for the type of outputs.
        self.box_outputs = self.get_box_outputs(outputs)
        self.mask_outputs = self.get_mask_outputs(outputs)
        self.score_outputs = self.get_score_outputs(outputs)
        self.decoded_masks_outputs = self.get_decoded_mask_outputs(outputs)
        self.class_outputs = self.get_class_outputs(outputs)

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
            self.infer(image)
            stop = clock_now() - start
            times.append(stop * 1e-6)

        message = "model warmup took %f ms (%f ms avg)" % (np.sum(times),
                                                           np.average(times))
        logger(message, code="INFO")

    def infer(self, image: np.ndarray) -> list:
        """
        Executes inference on a batch of images.

        Parameters
        ----------
        image: np.ndarray
            The image input after being preprocessed.
            Typically this is an RGB image array with the same
            input shape as the model.

        Returns
        -------
        list
            Raw model outputs stored inside a list.

        Raises
        ------
        ImportError
            Raised if the pycuda library is not installed.
        """
        try:
            import pycuda.driver as cuda  # type: ignore
        except ImportError:
            raise ImportError(
                "pycuda driver is needed for TensorRT inference.")

        # Copy I/O and Execute.
        image = np.ascontiguousarray(image)
        cuda.memcpy_htod(self.inputs[0]['allocation'], image)
        self.context.execute_v2(self.allocations)
        for o in range(len(self.outputs)):
            cuda.memcpy_dtoh(
                self.outputs[o]['host_allocation'],
                self.outputs[o]['allocation'])
        return [o['host_allocation'] for o in self.outputs]

    def run_single_instance(
        self,
        image: np.ndarray,
        shapes: Tuple[tuple] = None,
        ratio: float = 1.0,
        image_shape: tuple = None
    ) -> Any:
        """
        Run TensorRT inference on a single image and record the timings.
        Memory copying to and from the GPU device be performed here.

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
        outputs = self.infer(image)
        infer_ns = clock_now() - start
        self.backbone_timings.append(infer_ns * 1e-6)

        # Postprocessing
        # An output with 7 columns refers to
        # batch_id, xmin, ymin, xmax, ymax, cls, score.
        # Otherwise it is batch_size, number of boxes, number of classes
        # which needs external NMS.
        # Decoder and box timings are measured in this function.
        return self.postprocessing(outputs)

    def input_spec(self) -> Tuple[tuple, np.dtype]:
        """
        Grabs the specs for the input tensor
        of the network. Useful to prepare memory allocations.

        Returns
        -------
        Tuple[tuple, np.dtype]
            tuple
                The shape of the input tensor.
            np.dtype
                The input datatype.
        """
        return self.inputs[0]['shape'], self.inputs[0]['dtype']

    def output_spec(self) -> list:
        """
        Grabs the specs for the output tensors of the network.
        Useful to prepare memory allocations.

        Returns
        -------
        list
            A list with two items per element, the shape and (numpy)
            datatype of each output tensor.
        """
        specs = list()
        for o in self.outputs:
            specs.append((o['shape'], o['dtype']))
        return specs

    def get_input_type(self) -> np.dtype:
        """
        This returns the input type of the model for the
        input with shape in the form
        (batch size, channels, height, width) or
        (batch size, height, width, channels).

        Returns
        -------
        np.dtype
            The input type of the model.
        """
        return self.inputs[0]['dtype']

    def get_input_shape(self) -> list:
        """
        This fetches the model input shape.

        Returns
        -------
        list
            The model input shape
            [batch size, channels, height, width] or
            [batch size, height, width, channels].
        """
        return self.inputs[0]['shape']
