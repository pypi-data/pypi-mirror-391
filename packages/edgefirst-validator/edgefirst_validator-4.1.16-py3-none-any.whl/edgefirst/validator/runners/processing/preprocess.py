from typing import Tuple
from collections.abc import Iterable

import numpy as np

from edgefirst.validator.datasets.utils.transformations import (letterbox, resize,
                                                                cube_processing,
                                                                pad, rgb2yuyv,
                                                                rgb2rgba,
                                                                image_normalization)


def preprocess(
    image: np.ndarray,
    shape: tuple,
    input_type: str,
    preprocessing: str = "letterbox",
    normalization: str = "unsigned",
    resample: int = None
) -> Tuple[np.ndarray, tuple, float, tuple]:
    """
    Standard preprocessing method. Default parameters are based on
    Ultralytics defaults.

    Parameters
    ----------
    image: np.ndarray
        The image input to preprocess.
    shape: tuple
        The model input shape. This can either be formatted as
        (batch size, channels, height, width) or
        (batch size, height, width, channels).
    input_type: str
        The input datatype of the model.
    preprocessing: str
        The type of image preprocessing to apply. By default 'letterbox'
        is used. However, 'resize' or 'pad' are possible variations.
    normalization: str
        The type of image normalization to apply. Default is set to
        'unsigned'. However 'signed', 'raw', and 'imagenet' are possible
        values.
    resample: int
        This is the type of resampling method in Pillow. By default it
        is Image.NEAREST set to 0. However, other forms are Image.BILINEAR
        set to 2.

    Returns
    -------
    Tuple[np.ndarray, tuple, float, tuple]
        np.ndarray
            The image input after being preprocessed.
        tuple
            This is used to scale the bounding boxes of the ground
            truth and the model detections based on the letterbox
            transformation.
            ((pad image height, pad image width), (ratio y, ratio x), (pad x, pad y)).
        float
            Rescaling factor used for the bounding boxes.
        tuple
            The original image dimensions.
    """
    transpose = False
    # Fetch only (height, width) from the shape.
    # Format for YUYV, RGB, and RGBA
    if shape[-1] in [2, 3, 4]:
        channel = shape[-1]
        shape = shape[1:3]
    else:
        channel = shape[1]
        shape = shape[2:4]
        # Transpose the image to meet requirements of the channel order.
        transpose = True

    transformer = None  # Function that transforms image formats.
    if channel == 2:
        transformer = rgb2yuyv
    elif channel == 4:
        transformer = rgb2rgba

    shapes = [
        [
            shape,  # imgsz (model input shape) [height, width]
            [[shape[0] / image.shape[0], shape[1] / image.shape[1]],
             [0.0, 0.0]]  # ratio_pad [[scale y, scale x], [pad w, pad h]]
        ],
        [1.0, 1.0]  # label ratio [x, y]
    ]
    ratio = 1.0

    if len(image.shape) > 4:
        image = cube_processing(image, shape)
        _, height, width = image.shape
    else:
        height, width, _ = image.shape

        if preprocessing == "letterbox":
            image, label_ratio, shapes = letterbox(image,
                                                   new_shape=shape,
                                                   auto=False,
                                                   scaleup=False)
            shapes = [shapes, label_ratio]
            ratio = label_ratio[0]
        elif preprocessing == "pad":
            image, label_ratio, shapes = pad(image, shape)
            shapes = [shapes, label_ratio]
            ratio = label_ratio[0]
        else:
            # Take only the (height, width).
            image = resize(image, shape, resample=resample)
            ratio = 1.0

        # Convert image format to either YUYV, RGBA or keep as RGB.
        image = transformer(image) if transformer else image

        # Expects batch size, channel, height, width.
        if transpose:
            image = np.transpose(image, axes=[2, 0, 1])

    type = "float32"
    if isinstance(input_type, Iterable):
        type = "float32"
        if "float32" in input_type:
            type = "float32"
        elif "float16" in input_type:
            type = "float16"
    else:
        if isinstance(input_type, np.float32):
            type = "float32"
        elif isinstance(input_type, np.float16):
            type = "float16"
    # Integer types are not performed here. See individual model runners.

    image = image_normalization(image, normalization, type)
    return image, shapes, ratio, (height, width)
