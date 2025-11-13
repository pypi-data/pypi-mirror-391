"""
This module contains functions for transforming dataset artifacts.
"""

import os
import math
import numbers
from io import BytesIO
from typing import Union, Tuple, Any, List

import numpy as np
from PIL import Image, ImageDraw, ExifTags

# Transform label synonyms to a common representation.
COCO_LABEL_SYNC = {
    "motorbike": "motorcycle",
    "aeroplane": "airplane",
    "sofa": "couch",
    "pottedplant": "potted plant",
    "diningtable": "dining table",
    "tvmonitor": "tv"
}

# Functions for Sensor Transformations


def bgr2rgb(image: np.ndarray) -> np.ndarray:
    """
    Converts BGR image to RGB image.

    Parameters
    ----------
    image: (height, width, 3) np.ndarray
        The BGR image NumPy array.

    Returns
    -------
    np.ndarray
        The RGB image NumPy array.
    """
    return image[:, :, ::-1]


def rgb2bgr(image: np.ndarray) -> np.ndarray:
    """
    Converts RGB image to BGR image.

    Parameters
    ----------
    image: (height, width, 3) np.ndarray
        The RGB image NumPy array.

    Returns
    -------
    np.ndarray
        The BGR image NumPy array.
    """
    return bgr2rgb(image)


def rgb2yuyv(image: np.ndarray) -> np.ndarray:
    """
    Convert an RGB image to YUYV format using OpenCV.

    Parameters
    ----------
    image: np.ndarray
        The 3-channel RGB image NumPy array.

    Returns
    -------
    np.ndarray
        The 2-channel YUYV image array.

    Raises
    -------
    ImportError
        Raised if OpenCV is not installed.
    """
    try:
        import cv2  # type: ignore
    except ImportError:
        raise ImportError(
            "OpenCV is not installed in the system for YUYV image conversion.")
    return cv2.cvtColor(image, cv2.COLOR_RGB2YUV_YUY2)


def yuyv2rgb(image: np.ndarray) -> np.ndarray:
    """
    Convert a YUYV image to RGB format using OpenCV.

    Parameters
    ----------
    image: np.ndarray
        The input 2-channel YUYV image.

    Returns
    -------
    np.ndarray
        The output 3-channel RGB image.
    """
    try:
        import cv2  # type: ignore
    except ImportError:
        raise ImportError(
            "OpenCV is not installed in the system for YUYV image conversion.")
    return cv2.cvtColor(image, cv2.COLOR_YUV2RGB_YUY2)


def rgb2rgba(image: np.ndarray) -> np.ndarray:
    """
    Convert a 3-channel RGB image to 4-channel RGBA image.

    Parameters
    ----------
    image: np.ndarray
        The 3-channel RGB image array.

    Returns
    -------
    np.ndarray
        The 4-channel RGBA image array with the alpha value set to 255.
    """
    # Assuming rgb is shape (H, W, 3)
    if image.shape[-1] == 3:
        h, w, _ = image.shape
        alpha_channel = np.full((h, w, 1), 255, dtype=np.uint8)
        return np.concatenate((image, alpha_channel), axis=-1)
    return image


def imagenet(image: np.ndarray) -> np.ndarray:
    """
    Normalize the image with imagenet normalization.

    Parameters
    ----------
    image: np.ndarray
        The image RGB array with shape
        (3, height, width) or (height, width, 3).

    Returns
    -------
    np.ndarray
        The image with imagenet normalization.
    """
    mean = np.array([0.079, 0.05, 0]) + 0.406
    std = np.array([0.005, 0, 0.001]) + 0.224

    if image.shape[0] == 3:
        for channel in range(image.shape[0]):
            image[channel, :, :] = (image[channel, :, :] / 255
                                    - mean[channel]) / std[channel]
    else:
        for channel in range(image.shape[2]):
            image[:, :, channel] = (image[:, :, channel] / 255
                                    - mean[channel]) / std[channel]
    return image


def reverse_imagenet(image: np.ndarray) -> np.ndarray:
    """
    Reverse the ImageNet normalization applied by the `imagenet` function.

    Parameters
    ----------
    image: np.ndarray
        Normalized image with shape (3, height, width) or (height, width, 3)

    Returns
    -------
    np.ndarray
        The de-normalized image in the 0–255 range (uint8).
    """
    mean = np.array([0.079, 0.05, 0]) + 0.406
    std = np.array([0.005, 0, 0.001]) + 0.224
    image = np.squeeze(image, axis=0)

    if image.shape[0] == 3:
        # (3, H, W) shape
        for channel in range(3):
            image[channel] = (
                image[channel] * std[channel] + mean[channel]) * 255
    else:
        # (H, W, 3) shape
        for channel in range(3):
            image[:, :, channel] = (
                image[:, :, channel] * std[channel] + mean[channel]) * 255

    return image.astype(np.uint8)


def image_normalization(
    image: np.ndarray,
    normalization: str,
    input_type: str = "float32"
):
    """
    Performs image normalizations (signed, unsigned, raw).

    Parameters
    ----------
    image: np.ndarray
        The image to perform normalization.
    normalization: str
        This is the type of normalization to perform
        ("signed", "unsigned", "raw", "imagenet").
    input_type: str
        This is the NumPy datatype to convert. Ex. "uint8"

    Returns
    -------
    np.ndarray
        Depending on the normalization, the image will be returned.
    """
    if normalization.lower() == 'signed':
        return np.expand_dims(
            (image.astype(np.float32) / 127.5) - 1.0, 0).astype(np.dtype(input_type))
    elif normalization.lower() == 'unsigned':
        return np.expand_dims(image.astype(np.float32) /
                              255.0, 0).astype(np.dtype(input_type))
    elif normalization.lower() == 'imagenet':
        return np.expand_dims(imagenet(image.astype(np.float32)), 0).astype(
            np.dtype(input_type))
    else:
        return np.expand_dims(image, 0).astype(np.dtype(input_type))


def reverse_normalization(
    image: np.ndarray,
    normalization: str,
):
    """
    Revert the normalization applied to the image.

    Parameters
    ----------
    image: np.ndarray
        The image to perform normalization.
    normalization: str
        This is the type of normalization to perform
        ("signed", "unsigned", "raw", "imagenet").

    Returns
    -------
    np.ndarray
        The de-normalized image in the 0–255 range (uint8).
    """
    if normalization.lower() == 'signed':
        return ((np.squeeze(image, axis=0) + 1.0) * 127.5).astype(np.uint8)
    elif normalization.lower() == 'unsigned':
        return (np.squeeze(image, axis=0) * 255.0).astype(np.uint8)
    elif normalization.lower() == 'imagenet':
        return reverse_imagenet(image)
    else:
        return (np.squeeze(image, axis=0)).astype(np.uint8)


def crop_image(image: np.ndarray, box: Union[list, np.ndarray]) -> np.ndarray:
    """
    Crops the image to only the area that is covered by
    the box provided. This is primarily used in pose validation.

    Parameters
    ----------
    image: np.ndarray
        The frame to crop before feeding to the model.
    box: Union[list, np.ndarray]
        This contains non-normalized [xmin, ymin, xmax, ymax].

    Returns
    -------
    np.ndarray
        The image cropped to the area of the bounding box.
    """
    x1, y1, x2, y2 = box
    box_area = image[y1:y2, x1:x2, ...]
    return box_area


def rotate_image(data: Union[bytes, str]) -> Image.Image:
    """
    Read from the ImageExif to apply rotation on the image.

    Parameters
    ----------
    data: Union[bytes, str]
        Read image file as a bytes object or a string path
        to the image file.

    Returns
    -------
    Image.Image
        The pillow Image with rotation applied.
    """
    if isinstance(data, bytes):
        data = BytesIO(data)
    try:
        image = Image.open(data)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.transpose(Image.ROTATE_180)
        elif exif[orientation] == 6:
            image = image.transpose(Image.ROTATE_270)
        elif exif[orientation] == 8:
            image = image.transpose(Image.ROTATE_90)
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        image = Image.open(data).convert('RGB')
    return image


def resize(
    image: Union[str, np.ndarray],
    size: tuple = None,
    resample: int = None
) -> np.ndarray:
    """
    Resizes the images with the specified dimension.
    The original aspect ratio is not maintained.

    Parameters
    ----------
    image: Union[str, np.ndarray]
        The path to the image file or the image RGB NumPy array.
    size: tuple
        Specify the (height, width) size of the new image.
    resample: int
        This is the type of resampling method in Pillow. By default it
        is Image.NEAREST set to 0. However, other forms are Image.BILINEAR
        set to 2.

    Returns
    -------
    np.ndarray
        Resized image.

    Raises
    ------
    FileNotFoundError
        Raised if the image path provided does not exist.
    ValueError
        Raised if the provided image is neither an image path or np.ndarray.
    """
    if size is None:
        return image

    # Resize method requires (width, height).
    size = (size[1], size[0])
    if isinstance(image, str):
        if os.path.exists(image):
            from edgefirst.validator.datasets.utils.readers import read_image
            image = read_image(image)
            if resample is not None:
                image = image.resize(size, resample)
            else:
                image = image.resize(size)
            return np.asarray(image)
        else:
            raise FileNotFoundError(
                "Image file not found: '{}'".format(image))

    elif isinstance(image, np.ndarray):
        img = Image.fromarray(np.uint8(image))
        if resample is not None:
            img = img.resize(size, resample)
        else:
            img = img.resize(size)
        return np.asarray(img)
    else:
        raise ValueError(
            "The image provided must be a path to the file or " +
            "an RGB NumPy array. Got: {}".format(type(image))
        )


def rescale(image: np.ndarray, img_size: int = 640) -> Tuple[np.ndarray, list]:
    """
    Implementation based on YOLOv5 and YOLOv7 `load_image`
    which provides rescaling image pre-processing.

    Parameters
    ----------
    image: np.ndarray
        This is the image to rescale prior
        to letterbox transformation.
    img_size: int
        This is the eventual size of the image with a square
        resolution which should match the model's input shape.

    Returns
    -------
    Tuple[np.ndarray, list]
        np.ndarray
            This is the image that is rescaled based on the input
            shape of the model.
        list
            This contains the ratio between the original image height
            and width versus the new scaled height and width of the image.
    """
    height, width, _ = image.shape
    # Resize image to img_size -> Original image height and width.
    r = img_size / max(height, width)
    if r != 1:  # always resize down, only resize up if training with augmentation
        # YOLOv7 requires resizing with cv2.INTER_LINEAR interpolation by default.
        # However, if r < 1 and augment parameter is True, cv2.INTER_AREA is
        # used.
        image = resize(image, (math.ceil(height * r), math.ceil(width * r)), 2)

        # The following is an alternative which uses OpenCV for a better match with YOLO.
        # To match exactly with YOLOv7, change math.ceil to int typecast.
        # image = cv2.resize(
        #           image,
        #           (math.ceil(width * r), math.ceil(height * r)),
        #           interpolation=cv2.INTER_LINEAR)

    ratio = [image.shape[0] / height, image.shape[1] / width]
    return image, ratio


def pad(
    image: np.ndarray,
    input_size: tuple
) -> Tuple[np.ndarray, list, list]:
    """
    Performs image padding based on the implementation provided in YOLOx:\
    https://github.com/Megvii-BaseDetection/YOLOX/blob/main/yolox/data/data_augment.py#L142

    The image is always padded on the right and at the bottom portions.

    Parameters
    ----------
    image: np.ndarray
        This is the input image to pad.
    input_size: tuple
        This is the model input size (generally) or the output image
        resolution after padding in the order (height, width).

    Returns
    --------
    Tuple[np.ndarray, list, list]
        np.ndarray
            This is the padded image.
        list
            Rescaling factor used for the bounding boxes.
        list
            This is used to scale the bounding boxes of the ground
            truth and the model detections based on the letterbox
            transformation.
            ((pad image height, pad image width), (ratio y, ratio x), (pad x, pad y)).
    """
    shape = image.shape[:2]  # current shape [height, width]
    if len(image.shape) == 3:
        padded_image = np.ones(
            (input_size[0], input_size[1], 3), dtype=np.uint8) * 114
    else:
        padded_image = np.ones(input_size, dtype=np.uint8) * 114

    r = min(input_size[0] / image.shape[0], input_size[1] / image.shape[1])

    resized_image = resize(
        image, (int(image.shape[0] * r), int(image.shape[1] * r)),
        Image.Resampling.BILINEAR
    )
    padded_image[: int(image.shape[0] * r),
                 : int(image.shape[1] * r)] = resized_image
    padded_image = rgb2bgr(padded_image)  # RGB2BGR
    padded_image = np.ascontiguousarray(padded_image, dtype=np.float32)

    # The bounding box offset to add due to image padding.
    # Requires normalization due to the bounding boxes are already normalized.
    new_unpad = int(round(image.shape[0] * r)), int(round(image.shape[1] * r))
    dw = (padded_image.shape[1] - new_unpad[1])  # / new_unpad[1]
    dh = (padded_image.shape[0] - new_unpad[0])  # / new_unpad[0]

    # The image was not rescaled, so default to 1.0.
    shapes = [
        # imgsz (model input shape) [height, width]
        [padded_image.shape[0], padded_image.shape[1]],
        [[padded_image.shape[0] / shape[0], padded_image.shape[1] / shape[1]],
         [dw, dh]]  # ratio_pad [[scale y, scale x], [pad w, pad h]]
    ]
    return padded_image, [r, r], shapes


def letterbox(
    image: np.ndarray,
    new_shape: tuple = (640, 640),
    constant: int = 114,
    auto: bool = True,
    scalefill: bool = False,
    scaleup: bool = True,
    stride: int = 32
) -> Tuple[np.ndarray, list, list]:
    """
    Applies the letterbox image transformations based in YOLOv5 and YOLOv7.

    Parameters
    ----------
    image : np.ndarray
        Input image array (HWC format).
    new_shape : tuple, optional
        Target shape (height, width) for output image, by default (640, 640).
    constant : int, optional
        Padding pixel value (0–255), by default 114 (gray).
    auto : bool, optional
        If True, adds padding so final shape is a multiple of `stride`.
    scalefill : bool, optional
        If True, stretches the image to fill `new_shape` without padding.
    scaleup : bool, optional
        If False, only scales down images to prevent enlargement.
    stride : int, optional
        Used to constrain final shape as a multiple of this value.

    Returns
    -------
    Tuple[np.ndarray, list, list]
        np.ndarray
            The resized and padded image in HWC format.
        list
            Scaling factors (width, height) applied to original boxes.
        list
            This is used to scale the bounding boxes of the ground
            truth and the model detections based on the letterbox
            transformation. Tuple containing padded image size, scale ratio,
            and padding offsets.
            ((pad image height, pad image width), (ratio y, ratio x), (pad x, pad y)).
    """
    image, image_ratio = rescale(image, max(new_shape[0], new_shape[1]))

    # Resize and pad image while meeting stride-multiple constraints
    shape = image.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    # Compute padding
    label_ratio = [r, r]  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - \
        new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scalefill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        # width, height ratios
        label_ratio = [new_shape[1] / shape[1], new_shape[0] / shape[0]]

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        image = Image.fromarray(image)
        image = image.resize(new_unpad, Image.Resampling.BILINEAR)
        image = np.asarray(image)

    # New shape after resizing
    shape = image.shape[:2]  # (height, width)

    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))

    padded_image = np.zeros(
        (3, shape[0] + top + bottom, shape[1] + left + right))
    for i, _ in enumerate(padded_image):
        padded_image[i, :, :] = np.pad(image[:, :, i],
                                       ((top, bottom), (left, right)),
                                       mode='constant',
                                       constant_values=constant
                                       )
    padded_image = np.transpose(padded_image, axes=(1, 2, 0)).astype(np.uint8)

    # The following is an alternative which uses OpenCV for a better match with YOLO.
    # if shape[::-1] != new_unpad: # resize
    #     image = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)
    # top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    # left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    # padded_image = cv2.copyMakeBorder(
    #                   image, top, bottom, left, right, cv2.BORDER_CONSTANT,
    #                   value=(constant, constant, constant))  # add border

    shapes = [
        # imgsz (model input shape) [height, width]
        [padded_image.shape[0], padded_image.shape[1]],
        [image_ratio, [dw, dh]]  # ratio_pad [[scale y, scale x], [pad w, pad h]]
    ]
    return padded_image, label_ratio, shapes


def batch_shape(
    img_size: int = 640,
    pad: float = 0.5,
    stride: int = 32,
    batch_size: int = 1
) -> np.ndarray:
    """
    Derive the shape of the images in a given batch which is based on
    YOLOv7 image preprocessing if the parameter `rect` is set to True.

    The output shape is passed to the letterbox operation. However, this does
    yield different shapes which could fail on models that are configured
    to accept only limited input shapes (640,640,3) for example.

    Parameters
    ----------
    img_size: int
        This is the eventual size of the image with a square
        resolution which should match the model's input shape.
    pad: float
        Padding factor applied after aspect ratio scaling.
    stride: int
        Model stride to ensure shapes are divisible by this value.
    batch_size: int
        This is the size of the batch.

    Returns
    -------
    np.ndarray
        Array of shape (batch, 2) with image shapes (height, width).
    """
    # This contains the unique shapes of the images in a given batch.
    shapes = np.array([[640, 426]])  # width, height
    n = len(shapes)  # number of images
    bi = np.floor(np.arange(n) / batch_size).astype(int)  # batch index
    nb = bi[-1] + 1  # number of batches

    # Sort by aspect ratio
    s = shapes  # wh
    ar = s[:, 1] / s[:, 0]  # aspect ratio
    irect = ar.argsort()
    # shapes = s[irect]  # wh #NOSONAR
    ar = ar[irect]

    # Set training image shapes
    shapes = [[1, 1]] * nb
    for i in range(nb):
        ari = ar[bi == i]
        mini, maxi = np.min(ari), np.max(ari)
        if maxi < 1:
            shapes[i] = [maxi, 1]
        elif mini > 1:
            shapes[i] = [1, 1 / mini]

    return np.ceil(np.array(shapes) * img_size /
                   stride + pad).astype(int) * stride


def cube_processing(cube: np.ndarray, input_size: tuple) -> np.ndarray:
    """
    Radar cube preprocessing.

    Parameters
    ----------
    cube: np.ndarray
        The radar cube with shape (seq, range, rx, doppler, complex).
    input_size: tuple
        The input size (height, width). Ex. (192, 256).

    Returns
    -------
    np.ndarray
        The radar cube with the final model input shape (8, height, width).
    """
    # seq, range, rx, doppler, complex -> seq, rx, range, doppler, complex
    cube = np.transpose(cube, (0, 2, 1, 3, 4))
    # seq * rx, range, doppler * complex
    cube = np.reshape(cube, (2 * 4, 200, 128 * 2))
    # crop to input size to maintain mod 32 size.
    cube = cube[:, :input_size[0], :input_size[1]]
    cube = cube / 1000.0
    return cube


def softmax(x: np.ndarray) -> np.ndarray:
    """
    Transform values between 0 and 1.

    Parameters
    ----------
    x: np.ndarray
        An array of values to transform.

    Returns
    -------
    np.ndarray
        The array with softmax transformations.
    """
    # Subtract the maximum for numerical stability
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / np.sum(e_x, axis=-1, keepdims=True)

# Functions for Annotation Transformations


def clamp(
    value: Union[float, int],
    min: Union[float, int] = 0,
    max: Union[float, int] = 1
) -> Union[float, int]:
    """
    Clamps a given value between 0 and 1 by default.
    If the value is in between the set min and max, then it is returned.
    Otherwise it returns either min or max depending on which is the closest.

    Parameters
    ----------
    value: Union[float, int]
        Value to clamp between 0 and 1 (default).
    min: Union[float, int]
        Minimum acceptable value. Default to 0.
    max: Union[float, int]
        Maximum acceptable value. Default to 1.

    Returns
    -------
    Union[float, int]
        This is the clamped value.
    """
    return min if value < min else max if value > max else value


def standardize_coco_labels(labels: Union[list, np.ndarray]) -> list:
    """
    Converts synonyms of COCO labels to standard COCO labels using the
    provided labels mapping "COCO_LABEL_SYNC". This requires that the labels
    provided contain strings.

    Parameters
    ----------
    labels: list or np.ndarray
        This contains a list of string labels to map to
        standard COCO labels.

    Returns
    -------
    list
        Converted string labels to standard COCO labels.
    """
    synced_labels = list()
    for label in labels:
        for key in COCO_LABEL_SYNC.keys():
            if label == key:
                label = COCO_LABEL_SYNC[key]
        synced_labels.append(label)
    return synced_labels


def labels2string(
    int_labels: Union[list, np.ndarray],
    string_labels: Union[list, np.ndarray]
) -> list:
    """
    Converts label indices into their string represenations.

    Parameters
    ----------
    int_labels: Union[list, np.ndarray]
        A list of integer labels as indices to convert into strings.
    string_labels: Union[list, np.ndarray]
        A list of unique string labels used to map the label
        indices into their string representations.

    Returns
    -------
    list
        A list of string labels.
    """
    labels = []
    for label in int_labels:
        labels.append(string_labels[int(label)] if isinstance(
            label, (numbers.Number, np.ndarray)) else label)
    return labels


def normalize(boxes: np.ndarray, shape: tuple = None) -> np.ndarray:
    """
    Normalizes the boxes to the width and height
    of the image or model input resolution.

    Parameters
    ----------
    boxes: np.ndarray
        Contains bounding boxes to normalize [[boxes1], [boxes2]].
    shape: tuple
        The (height, width) shape of the image to normalize the annotations.

    Returns
    -------
        Normalized boxes: np.ndarray
            new x-coordinate = old x-coordinate/width
            new y-coordinate = old y-coordinate/height
    """
    if shape is None:
        return boxes

    if isinstance(boxes, list):
        boxes = np.array(boxes)
    boxes[..., 0:1] /= shape[1]
    boxes[..., 1:2] /= shape[0]
    boxes[..., 2:3] /= shape[1]
    boxes[..., 3:4] /= shape[0]
    return boxes


def denormalize(boxes: np.ndarray, shape: tuple = None) -> np.ndarray:
    """
    Denormalizes the boxes by the width and height of the image
    or model input resolution to get the pixel values of the boxes.

    Parameters
    ----------
    boxes: np.ndarray
        Contains bounding boxes to denormalize [[boxes1], [boxes2]].
    shape: tuple
        The (height, width) shape of the image to denormalize the annotations.

    Returns
    -------
    np.ndarray
        Denormalized set of bounding boxes in pixels values.
    """
    if shape is None:
        return boxes

    if isinstance(boxes, list):
        boxes = np.array(boxes)
    boxes[..., 0:1] *= shape[1]
    boxes[..., 1:2] *= shape[0]
    boxes[..., 2:3] *= shape[1]
    boxes[..., 3:4] *= shape[0]
    return boxes.astype(np.int32)


def normalize_polygon(vertex: Union[list, np.ndarray], shape: tuple) -> list:
    """
    Normalizes the vertex coordinate of a polygon.

    Parameters
    ----------
    vertex: Union[list, np.ndarray]
        This contains [x, y] coordinate.
    shape: tuple
        The (height, width) shape of the image to normalize the annotations.

    Returns
    -------
    list
        This contains normalized [x, y] coordinates.
    """
    return [float(vertex[0]) / shape[1], float(vertex[1]) / shape[0]]


def denormalize_polygon(vertex: Union[list, np.ndarray], shape: tuple) -> list:
    """
    Denormalizes the vertex coordinate of a polygon.

    Parameters
    ----------
    vertex: Union[list, np.ndarray]
        This contains [x, y] coordinate.
    shape: tuple
        The (height, width) shape of the image to denormalize the annotations.

    Returns
    -------
    list
        This contains denormalized [x, y] coordinates.
    """
    return [int(float(vertex[0]) * shape[1]), int(float(vertex[1]) * shape[0])]


def yolo2xyxy(boxes: np.ndarray) -> np.ndarray:
    """
    Converts YOLO (xcycwh) format into PascalVOC (xyxy) format.

    Parameters
    ----------
    boxes: np.ndarray
        Contains lists for each boxes in YOLO format [[boxes1], [boxes2]].

    Returns
    -------
    np.ndarray
        Contains list for each boxes in PascalVOC format.
    """
    w_c = boxes[..., 2:3]
    h_c = boxes[..., 3:4]
    boxes[..., 0:1] = boxes[..., 0:1] - w_c / 2
    boxes[..., 1:2] = boxes[..., 1:2] - h_c / 2
    boxes[..., 2:3] = boxes[..., 0:1] + w_c
    boxes[..., 3:4] = boxes[..., 1:2] + h_c
    return boxes


def xyxy2yolo(boxes: np.ndarray) -> np.ndarray:
    """
    Converts PascalVOC (xyxy) into YOLO (xcycwh) format.

    Parameters
    ----------
    boxes: np.ndarray
        Contains lists for each boxes in PascalVOC format [[boxes1], [boxes2]].

    Returns
    -------
    np.ndarray
        Contains list for each boxes in YOLO format.
    """
    w_c = boxes[..., 2:3] - boxes[..., 0:1]
    h_c = boxes[..., 3:4] - boxes[..., 1:2]
    boxes[..., 0:1] = boxes[..., 0:1] + w_c / 2
    boxes[..., 1:2] = boxes[..., 1:2] + h_c / 2
    boxes[..., 2:3] = w_c
    boxes[..., 3:4] = h_c
    return boxes


def xywh2xyxy(boxes: np.ndarray) -> np.ndarray:
    """
    Converts COCO (xywh) format to PascalVOC (xyxy) format.

    Parameters
    ----------
    boxes: np.ndarray
        Contains lists for each boxes in COCO format [[boxes1], [boxes2]].

    Returns
    -------
    np.ndarray
        Contains list for each boxes in PascalVOC format.
    """
    boxes[..., 2:3] = boxes[..., 2:3] + boxes[..., 0:1]
    boxes[..., 3:4] = boxes[..., 3:4] + boxes[..., 1:2]
    return boxes


def xyxy2xywh(boxes: np.ndarray) -> np.ndarray:
    """
    Converts PascalVOC (xyxy) format to COCO (xywh) format.

    Parameters
    ----------
    boxes: np.ndarray
        Contains lists for each boxes in COCO format [[boxes1], [boxes2]].

    Returns
    -------
    np.ndarray
        Contains list of each boxes in COCO format.
    """
    boxes[..., 2:3] = boxes[..., 2:3] - boxes[..., 0:1]
    boxes[..., 3:4] = boxes[..., 3:4] - boxes[..., 1:2]
    return boxes


def get_center_point(box: Union[list, np.ndarray]) -> np.ndarray:
    """
    If given the [xmin, ymin, xmax, ymax] of the bounding box,
    this function finds the centerpoint of the bounding box in [x,y].

    Parameters
    ----------
    box: Union[list, np.ndarray]
        The [xmin, ymin, xmax, ymax] of the bounding box.

    Returns
    -------
    np.ndarray
        The centerpoint coordinate [x,y].
    """
    width = box[2] - box[0]
    height = box[3] - box[1]
    return np.array([box[0] + width / 2, box[1] + height / 2])


def scale(
    boxes: np.ndarray,
    w: int = 640,
    h: int = 640,
    padw: int = 0,
    padh: int = 0,
) -> np.ndarray:
    """
    Convert nx4 boxes from [xc, yc, w, h] normalized to
    [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    This method provides a combined functionality from both functions in YOLOv5.
    Converts xywh to xyxy format.
    https://github.com/ultralytics/yolov5/blob/master/utils/dataloaders.py#L790
    Converts xyxy to xywh format.
    https://github.com/ultralytics/yolov5/blob/master/utils/dataloaders.py#L805
    Converts xywh to xyxy format.
    https://github.com/ultralytics/yolov5/blob/master/val.py#L273

    Parameters
    ----------
    boxes: np.ndarray (nx4)
        This is already in xyxy format.
    w: int
        This is the width of the image before any letterbox
        transformation.
    h: int
        This is the height of the image before any letterbox
        transformation.
    padw: int
        The width padding in relation to the letterbox.
    padh: int
        The height padding in relation to the letterbox.

    Returns
    -------
    np.ndarray
        The bounding boxes rescaled to be centered around the
        objects of an image with letterbox transformation.
    """
    y = np.copy(boxes)
    y[..., 0] = (w * (boxes[..., 0]) + padw)  # top left boxes
    y[..., 1] = (h * (boxes[..., 1]) + padh)  # top left y
    y[..., 2] = (w * (boxes[..., 2]) + padw)  # bottom right boxes
    y[..., 3] = (h * (boxes[..., 3]) + padh)  # bottom right y
    return y


def unscale(
    boxes: np.ndarray,
    w: int = 640,
    h: int = 640,
    padw: int = 0,
    padh: int = 0,
    n_w: int = 640,
    n_h: int = 640
) -> np.ndarray:
    """
    Reverses the effects of the method above `scale`. Given a set of
    bounding boxes that are centered around objects within a letterboxed/padded
    image, the bounding boxes are then transformed to be centered around
    objects in an image without any transformation.

    Parameters
    ----------
    boxes: np.ndarray (nx4)
        This is already in xyxy format. The bounding boxes scaled
        to be centered around the objects of an image with letterbox/padded
        transformation.
    w: int
        This is the width of the image before any transformation.
    h: int
        This is the height of the image before any transformation.
    padw: int
        The width padding in relation to the letterbox/padding
        transformation.
    padh: int
        The height padding in relation to the letterbox/padding
        transformation.
    n_w: int
        The new width of the image after transformation (letterbox/padding).
    n_h: int
        The new height of the image after transformation (letterbox/padding).

    Returns
    -------
    np.ndarray
        The bounding boxes rescaled to be centered around the
        objects of an image without any letterbox transformations.
    """
    y = np.copy(boxes)
    y[..., 0] = (n_w * (boxes[..., 0]) - padw) / w  # top left boxes
    y[..., 1] = (n_h * (boxes[..., 1]) - padh) / h  # top left y
    y[..., 2] = (n_w * (boxes[..., 2]) - padw) / w  # bottom right boxes
    y[..., 3] = (n_h * (boxes[..., 3]) - padh) / h  # bottom right y
    return y


def scale_coords(
    inference_shape: tuple,
    box: np.ndarray,
    image_shape: tuple,
    ratio_pad: tuple = ((1.0, 1.0), (0.0, 107.0))
) -> np.ndarray:
    """
    Ultralytics and YOLOv7 bounding box rescaling.

    Parameters
    ----------
    inference_shape: tuple
        This is the (height, width) of the model input shape.
    box: np.ndarray
        The bounding box to scale in the format of (xmin, ymin, xmax, ymax).
    image_shape: tuple
        This is the original dimensions (height, width) of the image
        in the dataset.
    ratio_pad: tuple
        This contains ((ratio y, ratio x), (pad x, pad y)) which is the
        same variable seen in Ultralytics and YOLOv7 where ratio is the
        ratio between the inference shape and the original image shape and
        pad x and pad y are letterbox padding values.

    Returns
    -------
    np.ndarray
        These are the rescaled bounding boxes based on the
        letter box image transformations.
    """
    # Denormalize coordinates
    box = box * np.array(
        [inference_shape[1],
         inference_shape[0],
         inference_shape[1],
         inference_shape[0]])

    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(inference_shape[0] / image_shape[0],
                   inference_shape[1] / image_shape[1])
        pad = ((inference_shape[1] - image_shape[1] * gain) / 2,
               (inference_shape[0] - image_shape[0] * gain) / 2)  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    # Commented out is for normalized coordinates.
    box[:, [0, 2]] -= pad[0]  # (pad[0]/inference_shape[1])  # x padding
    box[:, [1, 3]] -= pad[1]  # (pad[1]/inference_shape[0])  # y padding
    box[:, :4] /= gain

    box[:, 0] = np.clip(box[:, 0], 0, image_shape[1])  # x1
    box[:, 1] = np.clip(box[:, 1], 0, image_shape[0])  # y1
    box[:, 2] = np.clip(box[:, 2], 0, image_shape[1])  # x2
    box[:, 3] = np.clip(box[:, 3], 0, image_shape[0])  # y2
    return box


def clamp_boxes(boxes: np.ndarray, clamp: int,
                shape: tuple = None) -> np.ndarray:
    """
    Clamps bounding boxes with size less than the provided clamp value to
    the clamp value in pixels. The minimum width and height  (dimensions)
    of the bounding is the clamp value in pixels.

    Parameters
    ----------
    boxes: np.ndarray
        The bounding boxes to clamp. The bounding boxes with dimensions
        larger than the clamp value will be kept, but the smaller boxes will
        be resized to the clamp value.
    clamp: int
        The minimum dimensions allowed for the height and width of the
        bounding box. This value is in pixels.
    shape: tuple
        If None is provided (by default), it assumes the boxes are in pixels.
        Otherwise, if shape is provided, the boxes are normalized which
        will transform the boxes in pixel representations first to be
        compared to the clamp value provided which is in pixels. The
        shape provided should be the (height, width) of the image.

    Returns
    -------
    np.ndarray
        The bounding boxes where the smaller boxes have been
        sized to the clamp value provided.
    """
    if len(boxes) == 0:
        return boxes

    if shape is None:
        height, width = (1, 1)
    else:
        height, width = shape

    widths = ((boxes[..., 2:3] - boxes[..., 0:1]) * width).flatten()
    heights = ((boxes[..., 3:4] - boxes[..., 1:2]) * height).flatten()
    modify = np.transpose(
        np.nonzero(((widths < clamp) + (heights < clamp)))).flatten()

    boxes[modify, 2:3] = boxes[modify, 0:1] + clamp / width
    boxes[modify, 3:4] = boxes[modify, 1:2] + clamp / height
    return boxes


def ignore_boxes(
    ignore: int,
    boxes: np.ndarray,
    labels: np.ndarray,
    scores: np.ndarray = None,
    shape: tuple = None
) -> Tuple[np.ndarray, np.ndarray, Union[None, np.ndarray]]:
    """
    Removes the boxes, labels, and scores provided if the boxes have dimensions
    less than the provided value set by the ignore parameter in pixels.

    Parameters
    ----------
    ignore: int
        The size of the boxes lower than this value will be removed. This
        value is in pixels.
    boxes: np.ndarray
        The bounding boxes array with shape (n, 4). The bounding boxes with
        dimensions less than the ignore parameter will be removed.
    labels: np.ndarray
        The labels associated to each bounding box. For every bounding box
        that was removed, the labels will also be removed.
    scores: np.ndarray
        (Optional) the scores associated to each bounding box. For every
        bounding box that was removed, the scores will also be removed.
    shape: tuple
        If None is provided (by default), it assumes the boxes are in pixels.
        Otherwise, if shape is provided, the boxes are normalized which
        will transform the boxes in pixel representations first to be
        compared to the ignore value provided which is in pixels. The
        shape provided should be the (height, width) of the image.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, Union[None, np.ndarray]]
        np.ndarray
            The bounding boxes where the smaller boxes have been
            removed
        np.ndarray
            The labels which contains only the labels of
            the existing bounding boxes.
        Union[None, np.ndarray]
            If scores is not provided, None is returned. Otherwise,
            the scores of the returned bounding boxes are returned.
    """
    if shape is None:
        height, width = (1, 1)
    else:
        height, width = shape

    widths = ((boxes[..., 2:3] - boxes[..., 0:1]) * width).flatten()
    heights = ((boxes[..., 3:4] - boxes[..., 1:2]) * height).flatten()
    keep = np.transpose(
        np.nonzero(((widths >= ignore) * (heights >= ignore)))).flatten()

    boxes = np.take(boxes, keep, axis=0)
    labels = np.take(labels, keep, axis=0)
    if scores is not None:
        scores = np.take(scores, keep, axis=0)

    return boxes, labels, scores

# Functions for Segmentation Transformations


def segments2boxes(segments: list, box_format: str = "yolo") -> np.ndarray:
    """
    Convert segment labels to box labels, i.e.
    (xy1, xy2, ...) to (xcycwh).
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/ops.py#L632

    Parameters
    ----------
    segments: list
        List of segments where each segment is a list of points,
        each point is [x, y] coordinates.
    box_format: str
        Default output box format is in "yolo" format [xc, yc, width, height].
        Otherwise, "pascalvoc" [xmin, ymin, xmax, ymax] and
        "coco" [xmin, ymin, width, height] are also accepted.

    Returns
    -------
    np.ndarray
        Bounding box coordinates in YOLO format.
    """
    boxes = []
    for s in segments:
        x, y = s.T  # segment xy
        boxes.append([x.min(), y.min(), x.max(), y.max()])  # xyxy

    if box_format == "yolo":
        return xyxy2yolo(np.array(boxes))  # cls, xywh
    elif box_format == "coco":
        return xyxy2xywh(np.array(boxes))
    else:
        return np.array(boxes)


def resample_segments(segments: list, n: int = 1000) -> list:
    """
    Resample segments to n points each using linear interpolation.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/ops.py#L649

    Parameters
    ----------
    segments: list
        List of (N, 2) arrays where N is the number of points in each segment.
    n: int
        Number of points to resample each segment to.

    Returns
    -------
    list
        Resampled segments with n points each.
    """
    for i, s in enumerate(segments):
        if len(s) == n:
            continue
        s = np.concatenate((s, s[0:1, :]), axis=0)
        x = np.linspace(0, len(s) - 1, n - len(s) if len(s) < n else n)
        xp = np.arange(len(s))
        x = np.insert(x, np.searchsorted(x, xp), xp) if len(s) < n else x
        segments[i] = (
            np.concatenate([np.interp(x, xp, s[:, i])
                           for i in range(2)], dtype=np.float32).reshape(2, -1).T
        )  # segment xy
    return segments


def format_segments(
    segments: np.ndarray,
    shape: tuple,
    ratio_pad: tuple,
    colors: Union[list, np.ndarray],
    mask_ratio: int = 4,
    mask_overlap: bool = True,
    semantic: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert polygon segments to bitmap masks.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/augment.py#L2224

    Parameters
    ----------
    segments: np.ndarray
        Mask segments with shape (# polygons, # coordinates, 2)
    shape: tuple
        This represents the (height, width) of the model input shape.
    ratio_pad: tuple
        This contains the scale and the padding factors after letterbox
        transformations in the form ((scale x, scale y), (pad x, pad y)).
    colors: Union[list, np.ndarray]
        The label to specify to each polygon.
    mask_ratio: int, optional
        Masks are downsampled according to mask_ratio. Default is set 4
        where the masks dimensions are divided by 4.
    mask_overlap: bool, optional
        If True, masks are overlapped and sorted by area. If False,
        each mask is represented separately.
    semantic: bool, optional
        Specify if the type of segmentation is semantic segmentation.
        By default this is False and set to instance segmentation as
        seen in Ultralytics.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        np.ndarray
            Bitmap masks with shape (N, H, W) or (1, H, W)
            if mask_overlap is True.
        np.ndarray
            Resorting the ground truth based on these indices.
    """
    scale_h, scale_w = ratio_pad[0]
    padw, padh = ratio_pad[1]

    if len(segments):
        segments[..., 0] *= scale_w
        segments[..., 1] *= scale_h
        segments[..., 0] += padw
        segments[..., 1] += padh

    sorted_idx = None

    if semantic:
        masks = create_mask_image(
            polygons=segments,
            labels=colors,
            shape=shape
        )
        masks = masks[None]  # (640, 640) -> (1, 640, 640)
    else:
        if mask_overlap:
            masks, sorted_idx = polygons2masks_overlap(
                imgsz=shape,
                segments=segments,
                downsample_ratio=mask_ratio
            )
            masks = masks[None]  # (640, 640) -> (1, 640, 640)
        else:
            masks = polygons2masks(
                imgsz=shape,
                segments=segments,
                colors=colors,
                downsample_ratio=mask_ratio
            )
    return masks, sorted_idx


def polygon2mask(
    imgsz: Tuple[int, int],
    polygons: List[np.ndarray],
    color: int = 1,
    downsample_ratio: int = 1
) -> np.ndarray:
    """
    Convert a list of polygons to a binary mask of the specified image size.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/utils.py#L297

    Parameters
    ----------
    imgsz: Tuple[int, int]
        The size of the image as (height, width).
    polygons: List[np.ndarray]
        A list of polygons. Each polygon is an array with shape (N, M), where
        N is the number of polygons, and M is the number of points
        such that M % 2 = 0.
    color: int, optional
        The color value to fill in the polygons on the mask.
    downsample_ratio: int, optional
        Factor by which to downsample the mask.

    Returns
    -----------
    np.ndarray
        A binary mask of the specified image size with the polygons filled in.
    """
    polygons = np.asarray(polygons, dtype=np.int32)
    polygons = polygons.reshape((polygons.shape[0], -1, 2))
    mask = create_mask_image(
        polygons=polygons,
        labels=color,
        shape=imgsz
    )

    if downsample_ratio > 1:
        nh, nw = (imgsz[0] // downsample_ratio, imgsz[1] // downsample_ratio)
        mask = resize(mask, (nh, nw), resample=Image.Resampling.BILINEAR)
    return mask


def polygons2masks(
    imgsz: Tuple[int, int],
    segments: List[np.ndarray],
    colors: Union[list, np.ndarray],
    downsample_ratio: int = 1
) -> np.ndarray:
    """
    Convert a list of polygons to a set of binary masks
    of the specified image size.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/utils.py#L322

    Parameters
    ----------
    imgsz: Tuple[int, int]
        The size of the image as (height, width).
    segments: List[np.ndarray]
        A list of polygons. Each polygon is an array with shape (N, M), where
        N is the number of polygons, and M is the number of points
        such that M % 2 = 0.
    colors: Union[list, np.ndarray]
        The color value to fill each polygon in the masks.
    downsample_ratio: int, optional
        Factor by which to downsample each mask.

    Returns
    -------
    np.ndarray
        A set of binary masks of the specified image size
        with the polygons filled in.
    """
    return np.array([polygon2mask(imgsz, [x.reshape(-1)],
                                  color, downsample_ratio)
                     for x, color in zip(segments, colors)])


def polygons2masks_overlap(
    imgsz: Tuple[int, int],
    segments: List[np.ndarray],
    downsample_ratio: int = 1
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert polygon segments to an overlap mask with sorted area priority.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/utils.py#L341

    Parameters
    ----------
    imgsz : Tuple[int, int]
        Image size as (height, width).
    segments : List[np.ndarray]
        List of polygons as arrays of (x, y) coordinates.
    downsample_ratio : int, optional
        Factor to downsample the output mask, by default 1.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        np.ndarray
            Overlap mask where larger areas take precedence.
        np.ndarray
            Indices of polygons sorted by descending area.
    """
    masks = np.zeros(
        (imgsz[0] // downsample_ratio, imgsz[1] // downsample_ratio),
        dtype=np.int32 if len(segments) > 255 else np.uint8,
    )
    areas = []
    ms = []
    for si in range(len(segments)):
        mask = polygon2mask(imgsz, [segments[si].reshape(-1)],
                            downsample_ratio=downsample_ratio, color=1)
        ms.append(mask.astype(masks.dtype))
        areas.append(mask.sum())
    areas = np.asarray(areas)
    index = np.argsort(-areas)
    ms = np.array(ms)[index]
    for i in range(len(segments)):
        mask = ms[i] * (i + 1)
        masks = masks + mask
        masks = np.clip(masks, a_min=0, a_max=i + 1)
    return masks, index


def crop_mask(masks: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """
    Crop masks to bounding box regions.
    https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/ops.py#L673

    Parameters
    ----------
    masks: np.ndarray
        Masks with shape (N, H, W).
    boxes: np.ndarray
        Bounding box coordinates with shape (N, 4)
        in relative point form.

    Returns
    -------
    np.ndarray
        Cropped masks.
    """
    _, h, w = masks.shape
    x1, y1, x2, y2 = np.split(
        boxes[:, :, np.newaxis], 4, axis=1)  # shape (n, 1, 1)
    r = np.arange(w, dtype=boxes.dtype)[None, None, :]  # rows shape(1,1,w)
    c = np.arange(h, dtype=boxes.dtype)[None, :, None]  # cols shape(1,h,1)
    return masks * ((r >= x1) * (r < x2) * (c >= y1) * (c < y2))


def scale_masks(
    masks: np.ndarray,
    shape: np.ndarray,
    padding: bool = True
) -> np.ndarray:
    """
    Rescale segment masks to target shape.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/ops.py#L745

    Parameters
    ----------
    masks: np.ndarray
        Masks with shape (N, C, H, W).
    shape: tuple
        Target height and width as (height, width).
    padding: bool
        Whether masks are based on YOLO-style augmented images with padding.

    Returns
    -------
    np.ndarray
        Rescaled masks.
    """
    # Fetch only (height, width) from the shape.
    # Format for YUYV, RGB, and RGBA
    if shape[-1] in [2, 3, 4]:
        ih, iw = shape[1:3]
    else:
        ih, iw = shape[2:4]

    mh, mw = masks.shape[1:]
    gain = min(mh / ih, mw / iw)  # gain  = old / new
    pad = [mw - iw * gain, mh - ih * gain]  # wh padding
    if padding:
        pad[0] /= 2
        pad[1] /= 2
    top, left = (int(pad[1]), int(pad[0])) if padding else (0, 0)  # y, x
    bottom, right = (int(mh - pad[1]), int(mw - pad[0]))
    masks = masks[..., top:bottom, left:right]
    # masks: (N, H, W), new_shape: (new_H, new_W)
    n, _, _ = masks.shape
    resized = np.zeros((n, ih, iw), dtype=masks.dtype)

    for i in range(n):
        mask_resized = resize(masks[i], size=(ih, iw),
                              resample=Image.Resampling.BILINEAR)
        resized[i] = np.array(mask_resized)
    masks = resized
    return masks


def process_mask(
    protos: np.ndarray,
    masks_in: np.ndarray,
    bboxes: np.ndarray,
    shape: tuple,
    upsample: bool = False
) -> np.ndarray:
    """
    Apply masks to bounding boxes using mask head output.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/ops.py#L692

    Parameters
    ----------
    protos: np.ndarray
        Mask prototypes with shape (mask_dim, mask_h, mask_w).
    masks_in: np.ndarray
        Mask coefficients with shape (N, mask_dim)
        where N is number of masks after NMS.
    bboxes: np.ndarray
        Bounding boxes with shape (N, 4) where
        N is number of masks after NMS.
    shape: tuple
        Input image size as (height, width).
    upsample: bool
        Whether to upsample masks to original image size.

    Returns
    -------
    np.ndarray
        A binary mask tensor of shape [n, h, w], where n is the
        number of masks after NMS, and h and w are the height and
        width of the input image. The mask is applied to the bounding boxes.
    """
    c, mh, mw = protos.shape  # CHW

    # Fetch only (height, width) from the shape.
    # Format for YUYV, RGB, and RGBA
    if shape[-1] in [2, 3, 4]:
        ih, iw = shape[1:3]
    else:
        ih, iw = shape[2:4]

    masks = np.matmul(masks_in, protos.astype(np.float32).reshape(c, -1))
    masks = masks.reshape(-1, mh, mw)  # CHW

    width_ratio = mw / iw
    height_ratio = mh / ih

    downsampled_bboxes = bboxes.copy()
    downsampled_bboxes[:, 0] *= width_ratio
    downsampled_bboxes[:, 2] *= width_ratio
    downsampled_bboxes[:, 3] *= height_ratio
    downsampled_bboxes[:, 1] *= height_ratio

    masks = crop_mask(masks, downsampled_bboxes)  # CHW
    masks = (masks > 0.0).astype(np.uint8)

    if upsample:
        masks = np.squeeze(masks[None], axis=0)
        # masks: (N, H, W), new_shape: (new_H, new_W)
        n, _, _ = masks.shape
        resized = np.zeros((n, ih, iw), dtype=masks.dtype)

        for i in range(n):
            mask_resized = resize(masks[i], size=(
                ih, iw), resample=Image.Resampling.BILINEAR)
            resized[i] = np.array(mask_resized)
        masks = resized
    return masks


def process_mask_native(
    protos: np.ndarray,
    masks_in: np.ndarray,
    bboxes: np.ndarray,
    shape: tuple
) -> np.ndarray:
    """
    Apply masks to bounding boxes using mask
    head output with native upsampling.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/utils/ops.py#L725

    Parameters
    ----------
    protos: np.ndarray
        Mask prototypes with shape (mask_dim, mask_h, mask_w).
    masks_in: np.ndarray
        Mask coefficients with shape (N, mask_dim)
        where N is number of masks after NMS.
    bboxes: np.ndarray
        Bounding boxes with shape (N, 4)
        where N is number of masks after NMS.
    shape: tuple
        Input image size as (height, width).

    Returns
    -------
    np.ndarray
        Binary mask tensor with shape (H, W, N).
    """
    c, mh, mw = protos.shape  # CHW
    masks = np.matmul(masks_in, protos.astype(np.float32).reshape(c, -1))
    masks = masks.reshape(-1, mh, mw)  # CHW
    masks = scale_masks(masks, shape)  # CHW
    masks = crop_mask(masks, bboxes)  # CHW
    return masks > 0.0  # returns a boolean array


def create_mask_image(
    polygons: Union[list, np.ndarray],
    labels: Union[list, np.ndarray, int],
    shape: tuple
) -> np.ndarray:
    """
    Creates a NumPy array of masks from a given list of polygons.

    Parameters
    ----------
    polygons: Union[list, np.ndarray]
        This contains the polygon points. Ex.
        [[[x1,y1], [x2,y2], ... ,[xn,yn]], [...], ...]
    labels: Union[list, np.ndarray, int]
        The integer label of each polygon for assigning the mask.
        If an integer is supplied, then a constant label is applied
        for all the polygons.
    shape: tuple
        This is the shape (height, width) of the mask.

    Returns
    -------
    np.ndarray
        The 2D mask image with shape (height, width) specified.
    """
    mask = Image.new('L', (shape[1], shape[0]), 0)
    canvas = ImageDraw.Draw(mask)
    polygons = polygons.tolist() if isinstance(polygons, np.ndarray) else polygons
    if isinstance(labels, (int, np.ScalarType)):
        labels = np.full(len(polygons), labels, dtype=np.int32)
    for c, polygon in zip(labels, polygons):
        polygon = [tuple(pt) for pt in polygon]  # requires a list of Tuples.
        if len(polygon) >= 2:
            canvas.polygon(polygon, outline=int(c), fill=int(c))
    # This array contains a mask of the image where the objects are
    # outlined by class number
    return np.array(mask)


def create_binary_mask(mask: np.ndarray) -> np.ndarray:
    """
    Creates a binary NumPy array of 1's and 0's encapsulating
    every object (regardless of class) in the image as a 1 and
    background as 0.

    Parameters
    ----------
    mask: np.ndarray
        2D array mask of class labels unique to each object.

    Returns
    -------
    np.ndarray
        Binary 2D mask of 1's and 0's.
    """
    return np.where(mask > 0, 1, mask)


def create_mask_class(mask: np.ndarray, cls: int) -> np.ndarray:
    """
    Separates a mask with more than one classes into an individual
    mask of 1's and 0's where 1 represents the specified class and
    0 represents other classes including background.

    Parameters
    ----------
    mask: np.ndarray
        Multiclass mask of class labels unique to each object.
    cls: int
        The integer representing the class in the mask
        to keep as a value of 1. The other classes will be treated as
        0's.

    Returns
    -------
    np.ndarray
        Binary 2D mask of 1's and 0's.
    """
    temp_mask = np.where(mask != cls, 0, mask)
    temp_mask[temp_mask == cls] = 1
    return temp_mask


def create_mask_classes(
    new_mask: np.ndarray,
    cls: int,
    current_mask: np.ndarray = None
) -> np.ndarray:
    """
    Appends a current mask with another mask of different class
    i.e converting a binary mask (new mask) into a mask with its
    class and then appending the original mask to include
    the new mask with its class.

    Parameters
    ----------
    new_mask: np.ndarray
        The current binary (0, 1) 2D mask.
    cls: int
        Class representing the 1's in the new mask. This is the class
        to append to the current mask.
    current_mask: (height, width) np.ndarray
        Current multiclass mask.

    Returns
    -------
    np.ndarray
        Multiclass mask with an additional class added.
    """
    new_mask = np.where(new_mask == 1, cls, new_mask)
    if current_mask is not None:
        return np.add(current_mask, new_mask)
    else:
        return new_mask


def create_mask_background(mask: np.ndarray) -> np.ndarray:
    """
    Creates a binary mask for the background class with 1's in the
    image and the rest of the objects will have values of 0's. This function
    switches the labels for background to 1 and positive classes to 0's.

    Parameters
    ----------
    mask: np.ndarray
        Multiclass mask array representing each image pixels.

    Returns
    -------
    np.ndarray
        Binary mask of 1's and 0's, where 1's is background and
        objects are 0's
    """
    # 2 is a temporary class
    temp_mask = np.where(mask != 0, 2, mask)
    temp_mask[temp_mask == 0] = 1
    temp_mask[temp_mask == 2] = 0
    return temp_mask


def convert_to_serializable(obj: Any):
    """
    Recursively convert NumPy types to
    Python-native types for JSON serialization.

    Parameters
    ----------
    obj: Any
        Any NumPy type.

    Returns
    -------
    obj
        The object with a native
        python type representation.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, np.generic):
        return obj.item()  # Convert other NumPy scalars
    elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return 0
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    else:
        return obj
