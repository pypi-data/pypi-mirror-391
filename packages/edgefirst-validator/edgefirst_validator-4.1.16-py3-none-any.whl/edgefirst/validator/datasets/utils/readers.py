"""
This module contains functions for reading various dataset files.
"""

import os
import json
import warnings

import yaml
import numpy as np
from PIL import Image, ImageFile

from edgefirst.validator.publishers.utils.logger import logger

ImageFile.LOAD_TRUNCATED_IMAGES = True


def read_image(image_path: str, rotate: bool = False) -> np.ndarray:
    """
    Opens the image using pillow.Image and if the image is neither in the
    format: [RGB, RGBA, CMYK, YCVCr] then the image will be converted to RGB.

    Parameters
    ----------
    image_path: str
        The path to the image to read.
    rotate: bool
        If set to True, read from the image EXIF and
        apply the rotation specified.

    Returns
    -------
    np.ndarray
        The image represented as a numpy array.
    """
    if rotate:
        from edgefirst.validator.datasets.utils.transformations import rotate_image
        image = rotate_image(image)
    else:
        image = Image.open(image_path)
    if image.mode in ["RGB", "RGBA", "CMYK", "YCbCr"]:
        image = np.asarray(image)
    else:
        image.convert("RGB")
        image = np.asarray(image, dtype=np.uint8)
        image = np.stack((image,) * 3, axis=-1)
    return image


def read_labels_file(file_path: str) -> list:
    """
    Opens a text file containing the string labels from
    either the dataset or the model. It returns the list of string labels,
    as the contents in the text file.

    Parameters
    ----------
    file_path: str
        The path to the labels.txt file.

    Returns
    -------
    list
        The list of string labels as the contents of the text
        file with a string label per line.
    """
    with open(file_path) as file:
        labels = [line.rstrip()
                  for line in file.readlines()
                  if line not in ["\n", "", "\t"]]
    return labels


def read_yaml_file(file_path: str, local: bool = True):
    """
    Reads YAML files with Au-Zone specific format
    for collecting dataset information.

    Parameters
    ----------
    file_path: str
        The path to the YAML file.
    local: bool
        If True, use local dataset readers. Otherwise,
        use deepview-datasets by default.

    Returns
    -------
    Union[dict [local reader], ObjectDetectionGenerator (deepview-datasets)]
        Stores the YAML file contents.

    Raises
    ------
    FileNotFoundError
        Raised if the path to the file does not exist.
    """
    if local:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML file not found: '{file_path}'")
        with open(file_path) as file:
            return yaml.full_load(file)
    else:
        from deepview.datasets.generators import ObjectDetectionGenerator  # type: ignore
        handler = ObjectDetectionGenerator(
            from_config=file_path  # config is the path to the yaml file
        )
        ds_iterator = handler.get_val_generator()
        return ds_iterator


def read_toml_file(file_path: str) -> dict:
    """
    Reads TOML files using tomli.

    Parameters
    ----------
    file_path: str
        The path to the TOML file.

    Returns
    -------
    dict
        The contents of the TOML file.
    """
    import tomli
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"TOML file not found: '{file_path}'")
    with open(file_path, "rb") as f:
        return tomli.load(f)


def read_npy_file(annotation_path: str) -> np.ndarray:
    """
    Reads NumPy files which typically contains radar data.

    Parameters
    ----------
    annotation_path: str
        The path to the NumPy file.

    Returns
    -------
    np.ndarray
        Radar cube with shape (seq, range, rx, doppler, complex).
    """
    try:
        return np.load(annotation_path)
    except (FileNotFoundError, TypeError):
        return np.array([])


def read_detection_text_file(
    annotation_path: str,
    label_offset: int = 0,
    shape: tuple = None,
    normalizer=None,
    transformer=None
) -> dict:
    """
    Reads the text file annotation to retrieve the
    ground truth bounding boxes and the labels.

    Parameters
    ----------
    annotation_path: str
        This is the path to the text file annotation.
    label_offset: int
        Used to offset the label indices by a specified amount.
    shape: tuple
        The (height, width) image dimensions for
        normalizing the bounding boxes (optional).
    normalizer: Function
        Normalizes bounding boxes.
    transformer: Function
        Transforms bounding boxes to a different format.

    Returns
    -------
    dict
        This contains information such as boxes and labels.

            .. code-block:: python

                {
                    'boxes': list of bounding boxes,
                    'labels': list of labels
                }
    """
    annotations = {
        "boxes": np.array([]),
        "labels": np.array([]).astype(np.int32)
    }

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            annotation = np.genfromtxt(annotation_path)
    except (FileNotFoundError, TypeError):
        return annotations

    if len(annotation) > 0:
        annotation = annotation.reshape(-1, 5)
        boxes = annotation[:, 1:5]
        boxes = normalizer(boxes, shape) if normalizer else boxes
        boxes = transformer(boxes) if transformer else boxes
        annotations["boxes"] = boxes
    else:
        return annotations

    labels = annotation[:, 0:1].flatten().astype(np.int32) + label_offset
    annotations["labels"] = labels
    return annotations


def read_segmentation_text_file(
    annotation_path: str,
    label_offset: int = 0,
    shape: tuple = None,
    normalizer=None,
    transformer=None,
    resample: int = 1000
) -> dict:
    """
    Reads a segmentation annotation file and converts it to bounding boxes.
    Source: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/utils.py#L180

    Parameters
    ----------
    annotation_path : str
        Path to the segmentation annotation text file.
        Assumes annotation file is in Ultralytics YOLO segment format.
    label_offset: int
        Used to offset the label indices by a specified amount.
    shape: tuple
        The (height, width) image dimensions for
        normalizing the bounding boxes (optional).
    normalizer: Function
        Normalizes bounding boxes.
    transformer: Function
        Transforms bounding boxes to a different format.
    resample: int
        The number of points to resample the segments.

    Returns
    -------
    dict
        A dictionary with the keys "boxes", "labels", "segments"
        storing the boxes in the shape (n, 4) -> [x, y, x, y], the labels
        of each box, and the segment coordinates (n, 2) -> [x, y].
    """
    from edgefirst.validator.datasets.utils.transformations import (segments2boxes,
                                                                    resample_segments)
    annotations = {
        "boxes": np.array([]),
        "labels": np.array([]).astype(np.int32),
        "segments": np.array([])
    }

    if annotation_path is None:
        return annotations

    segments = []

    with open(annotation_path, encoding="utf-8") as f:
        lb = [x.split() for x in f.read().strip().splitlines() if len(x)]
        if any(len(x) > 6 for x in lb):  # is segment
            classes = np.array([x[0] for x in lb], dtype=np.float32)
            segments = [np.array(x[1:], dtype=np.float32).reshape(-1, 2)
                        for x in lb]  # (cls, xy1...)
            lb = np.concatenate(
                (classes.reshape(-1, 1), segments2boxes(segments)), 1)  # (cls, xywh)
        lb = np.array(lb, dtype=np.float32)
        lb[..., 1:] = normalizer(
            lb[..., 1:], shape) if normalizer else lb[..., 1:]
        lb[..., 1:] = transformer(lb[..., 1:]) if transformer else lb[..., 1:]

    # Segments are being resampled.
    # https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/dataset.py#L274
    # NOTE: do NOT resample oriented boxes.
    if len(segments) > 0:
        # make sure segments interpolate correctly if
        # original length is greater than resample.
        max_len = max(len(s) for s in segments)
        resample = (max_len + 1) if resample < max_len else resample
        # list[np.array(resample, 2)] * num_samples
        segments = np.stack(resample_segments(segments, n=resample), axis=0)
        # Denormalize segments.
        segments[..., 0] *= shape[1]
        segments[..., 1] *= shape[0]
    else:
        segments = np.zeros((0, resample, 2), dtype=np.float32)

    annotations["boxes"] = lb[..., 1:]
    annotations["labels"] = lb[..., 0] + label_offset
    annotations["segments"] = segments

    return annotations


def read_detection_json_file(
    annotation_path: str,
    label_offset: int = 0,
    shape: tuple = None,
    normalizer=None,
    transformer=None
) -> dict:
    """
    Reads from the JSON annotation to retrieve the
    ground truth detection bounding boxes and labels.

    Parameters
    ----------
    annotation_path: str
        This is the path to the JSON annotation.
    label_offset: int
        Used to offset the label indices by a specified amount.
    shape: tuple
        The (height, width) image dimensions for
        normalizing the bounding boxes (optional).
    normalizer: Function
        Normalizes bounding boxes.
    transformer: Function
        Transforms bounding boxes to a different format.

    Returns
    -------
    dict
        This contains information such as boxes and labels.

            .. code-block:: python

                {
                    'boxes': list of bounding boxes,
                    'labels': list of labels
                }
    """
    annotations = {
        "boxes": np.array([]),
        "labels": np.array([]).astype(np.int32)
    }

    try:
        with open(annotation_path) as file:
            data: dict = json.load(file)

        annotation = np.array(data.get("boxes"))
        annotation = normalizer(
            annotation, shape) if normalizer else annotation
        boxes = transformer(
            annotation[:, 0:5]) if transformer else annotation[:, 0:5]
        labels = data.get("labels") + label_offset

    # TypeError is due to the annotation path being None.
    except (FileNotFoundError, TypeError, KeyError):
        return annotations

    annotations["boxes"] = boxes
    annotations["labels"] = labels
    return annotations


def read_3d_detection_json_file(
    annotation_path: str,
    label_offset: int = 0
) -> dict:
    """
    Reads from the JSON annotation to retrieve the 3D ground truth
    detection bounding boxes, angles, calibration, and labels.

    Parameters
    ----------
    annotation_path: str
        This is the path to the JSON annotation.
    label_offset: int
        Used to offset the label indices by a specified amount.

    Returns
    -------
    dict
        This contains 3D bounding box information.

            .. code-block:: python

                {
                    'boxes': list of 2D bounding boxes,
                    'centers': 3D bounding box centers (x,y,z),
                    'sizes': 3D bounding box sizes (w,h,l),
                    'angles': 3D bounding box heading angles (yaw heading in radians),
                    'view': (3x4) np.array calibration matrix,
                    'labels': list of labels
                }
    """
    annotations = {
        "boxes": np.array([]),
        "centers": np.array([]),
        "sizes": np.array([]),
        "angles": np.array([]),
        "view": np.array([]),
        "labels": np.array([]).astype(np.int32)
    }

    try:
        with open(annotation_path) as file:
            data: dict = json.load(file)

        boxes_3d = np.array(data.get("3d-boxes"))
        angles = np.array(data.get("angles")).flatten()

        if len(boxes_3d) > 0 and len(angles) > 0:
            centers = boxes_3d[:, 0:3]
            sizes = boxes_3d[:, 3:6]
            view = np.array(data.get("calibration"))

            boxes = np.array(data.get("boxes"))
            labels = boxes[:, 4:5].flatten().astype(np.int32) + label_offset
            boxes = boxes[:0:4]  # Exclude the labels.
        else:
            return annotations

    except UnicodeDecodeError:
        logger(f"Encountered UnicodeDecodeError for '{annotation_path}'. " +
               "Returning an empty ground truth schema for this image.",
               code="WARNING")
        return annotations
    # TypeError is due to the annotation path being None.
    except (FileNotFoundError, TypeError, KeyError):
        return annotations

    annotations["boxes"] = boxes
    annotations["centers"] = centers
    annotations["sizes"] = sizes
    annotations["angles"] = angles
    annotations["view"] = view
    annotations["labels"] = labels

    return annotations


def read_segmentation_json_file(
    annotation_path: str,
    shape: tuple,
    label_offset: int = 0,
    denormalizer=None,
) -> dict:
    """
    Reads from a JSON annotation file to retrieve segmentation polygons
    such as multiple (x,y) coordinates around an object to be segmented.

    Parameters
    ----------
    annotation_path: str
        This is the path to the JSON annotation.
    shape: tuple
        This contains the image (height, width) dimensions
        for denormalizing the polygon.
    label_offset: int
        The integer to offset the label indices which
        is used for integer to string mapping for the labels.
    denormalizer: Function
        Denormalizes segmentation coordinates.

    Returns
    -------
    dict
        This contains segmentation information.

            .. code-block:: python

                {
                    'segments': list of polygon segments
                                [[[x,y], [x,y], ...]...],
                    'labels': list of labels
                }
    """
    annotations = {
        "segments": np.array([]),
        "labels": np.array([]).astype(np.int32)
    }

    try:
        with open(annotation_path) as file:
            data = json.load(file)

        segments, labels = list(), list()
        for segment in data["segment"]:
            for polygon in segment:
                cls = polygon["class"]
                poly = polygon["polygon"]
                # label_offset should be 1 if there is a background class.
                labels.append(cls + label_offset)
                # a list of vertices
                x_y = []
                for vertex in poly:
                    vertex = denormalizer(vertex, shape[0], shape[1]) \
                        if denormalizer else vertex
                    x_y.append(float(vertex[0]))
                    x_y.append(float(vertex[1]))
                segments.append(x_y)

    except UnicodeDecodeError:
        logger(
            f"Encountered UnicodeDecodeError for '{annotation_path}'. " +
            "Returning an empty ground truth schema for this image. ",
            code="WARNING"
        )
        return annotations

    # TypeError is due to the annotation path being None.
    except (FileNotFoundError, TypeError, KeyError):
        return annotations

    annotations["segments"] = segments
    annotations["labels"] = labels
    return annotations


def read_pose_json_file(
    annotation_path: str,
    label_offset: int = 0,
    shape: tuple = None,
    normalizer=None,
    transformer=None
) -> dict:
    """
    Reads from a JSON annotation file to retrieve headpose angles.

    Parameters
    ----------
    annotation_path: str
        The path to the annotation file.
    label_offset: int
        Used to offset the label indices by a specified amount.
    normalizer: Function
        Normalizes bounding boxes.
    transformer: Function
        Transforms bounding boxes to a different format.

    Returns
    -------
    dict
        This contains the angles and the labels.

            .. code-block:: python

                {
                    "boxes": list of bounding boxes,
                    "angles": [roll, pitch, yaw],
                    "labels": [helmet]
                }

    Raises
    ------
    ValueError
        Raised if there are no bounding boxes for every angle.
    """
    annotations = {
        "boxes": np.array([[]]),
        "angles": np.array([[]]),
        "labels": np.array([]).astype(np.int32)
    }

    try:
        with open(annotation_path) as file:
            data: dict = json.load(file)

        angles = data.get("angles")
        if data.get("boxes") is None:
            raise ValueError(
                "There are no bounding boxes for this file '{}'".format(
                    os.path.basename(annotation_path)))

        labels, boxes = list(), list()
        if len(data.get("boxes")):
            labels = (
                np.array(data.get("boxes"))[:, 4:5].astype(np.int32) +
                label_offset
            )
            boxes = np.array(data.get("boxes"))
            boxes = boxes[:, 0:4]
            boxes = normalizer(boxes, shape) if normalizer else boxes
            boxes = transformer(boxes) if transformer else boxes

    except UnicodeDecodeError:
        logger(
            f"Encountered UnicodeDecodeError for '{annotation_path}'. " +
            "Returning an empty ground truth schema for this image. ",
            code="WARNING"
        )
        return annotations

    # TypeError is due to the annotation path being None.
    except (FileNotFoundError, TypeError, KeyError):
        return annotations

    annotations["angles"] = angles
    annotations["labels"] = labels
    annotations["boxes"] = boxes
    return annotations
