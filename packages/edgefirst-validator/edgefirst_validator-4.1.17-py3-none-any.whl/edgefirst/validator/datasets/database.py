"""
Implementations for reading LMDB databases.
"""

from __future__ import annotations

import os
import json
import glob
from pathlib import Path
from zipfile import ZipFile
from time import monotonic_ns as clock_now
from typing import TYPE_CHECKING, Union, Any, Tuple

import lmdb
import numpy as np
import polars as pl
from PIL import Image, ImageDraw
from turbojpeg import TurboJPEG, TJPF_RGB

from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.datasets.utils.fetch import get_shape
from edgefirst.validator.datasets.utils.readers import read_image
from edgefirst.validator.datasets.utils.transformations import (rotate_image,
                                                                format_segments,
                                                                resample_segments)
from edgefirst.validator.datasets import Dataset
from edgefirst.validator.datasets import (SegmentationInstance,
                                          DetectionInstance,
                                          MultitaskInstance)

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import DatasetParameters
    from edgefirst.validator.datasets import Instance


class Database(Dataset):
    def __init__(
        self,
        source: Any,
        parameters: DatasetParameters
    ):
        """
        Abstract database class for providing template methods in the database.

        Parameters
        ----------
        source: Any
            This is typically the path to the LMDB database file.
        parameters: DatasetParameters
            This contains dataset parameters set from the command line.
        """
        super(Database, self).__init__(source=source, parameters=parameters)
        # Tracking the dynamic shapes of the images across all samples.
        # Default value is set to the model input shape.
        self.shape = self.parameters.common.shape

        if self.parameters.common.with_boxes:
            self.box_placeholder = np.full(
                shape=(1, 5), fill_value=-1, dtype=np.float32)

    def image(self, index: int) -> np.ndarray:
        """Abstract Method"""
        raise NotImplementedError("Abstract Method")

    def labels(self, index: int) -> np.ndarray:
        """
        Fetch the labels at the specified sample.

        Parameters
        ----------
        index: int
            The index of the sample in the dataset.

        Returns
        -------
            np.ndarray
                The labels in the sample containing np.int32 elements.
        """
        return np.array([])

    def boxes(self, index: int) -> np.ndarray:
        """Abstract Method"""
        raise NotImplementedError("Abstract Method")

    def mask(self, index: int) -> np.ndarray:
        """Abstract Method"""
        raise NotImplementedError("Abstract Method")

    def segments(self, index: int) -> np.ndarray:
        """Abstract Method"""
        raise NotImplementedError("Absract Method")

    def name(self, index: int) -> str:
        """Abstract Method"""
        raise NotImplementedError("Abstract Method")

    def __len__(self) -> int:
        """Abstract Method"""
        raise NotImplementedError("Abstract Method")

    def __iter__(self):
        """
        Iterate through the database to
        yield a single sample.

        Yields
        ------
        tuple
            This can contain the following elements
            (name, image, boxes, masks) for multitask, (name, image, boxes)
            for detection, (name, image, masks) for segmentation.
        """
        for index in range(len(self)):
            yield self.get_instance(index)

    def get_instance(self, index: int) -> tuple:
        """
        Get a single annotation instance from the database.

        Parameters
        ----------
        index: int
            Specify the index of the instance to fetch.

        Returns
        -------
        tuple
            This can contain the following elements
            (name, image, boxes, masks) for multitask, (name, image, boxes)
            for detection, (name, image, masks) for segmentation.

        Raises
        ------
        TypeError
            Raised of with_boxes and with_masks are both set to False
            which indicates neither tasks were selected.
        """
        image_data = self.image(index)
        name = self.name(index)

        # Allow image extension for saving visualizations.
        if os.path.splitext(name)[-1] == "":
            name += ".png"

        # The cache will contain the preprocessed annotations.
        if self.parameters.common.with_boxes and self.parameters.common.with_masks:
            _, shapes, _, _ = image_data
            if shapes is not None:
                imgsz = shapes[0][0]
                ratio_pad = shapes[0][1]
            else:
                imgsz, ratio_pad = None, None

            mask, sorted_idx = self.mask(
                index, imgsz=imgsz, ratio_pad=ratio_pad)
            boxes = self.boxes(index)

            boxes = (self.normalizer(boxes, self.parameters.common.shape)
                     if self.normalizer else boxes)
            boxes = self.transformer(boxes) if self.transformer else boxes

            if sorted_idx is not None:
                boxes = boxes[sorted_idx]

            return name, image_data, boxes, (mask, mask.shape)
        elif self.parameters.common.with_boxes:
            boxes = self.boxes(index)

            boxes = (self.normalizer(boxes, self.parameters.common.shape)
                     if self.normalizer else boxes)
            boxes = self.transformer(boxes) if self.transformer else boxes

            return name, image_data, boxes
        elif self.parameters.common.with_masks:
            mask, _ = self.mask(index)
            return name, image_data, (mask, mask.shape)
        else:
            raise TypeError("No task was assigned for this dataset.")

    def build_dataset(self) -> list:
        """
        Returns the list of indices of the dataset samples
        for iteration.
        """
        return list(range(len(self)))

    def read_sample(self, index: int) -> Instance:
        """
        Reads one sample from the dataset and creates
        the ground truth instance. This method is for reading
        non-cached datasets.

        Parameters
        ----------
        index: int
            The dataset sample index.

        Returns
        -------
        Instance
            A type of ground truth instance container to
            store the annotations.
        """
        image, shapes, ratio, image_shape = self.image(index)
        height, width, _ = image.shape
        name = self.name(index)
        # Allow image extension for saving visualizations.
        if os.path.splitext(name)[-1] == "":
            name += ".png"

        if self.parameters.common.with_boxes and self.parameters.common.with_masks:
            boxes = self.boxes(index)
            # Returns the masks and the labels.
            segments, _ = self.segments(index)

            boxes = boxes[boxes[:, -1] != -1]
            if len(boxes):
                labels = boxes[..., 4]
                boxes = boxes[..., 0:4]
                boxes = (self.normalizer(boxes, self.parameters.common.shape)
                         if self.normalizer else boxes)
                boxes = self.transformer(boxes) if self.transformer else boxes
            else:
                labels = self.labels(index)
                boxes = np.array([])

            instance = MultitaskInstance(name)
            instance.image = image
            instance.height = height
            instance.width = width
            instance.boxes = boxes
            instance.labels = labels
            instance.polygons = segments
            instance.shapes = shapes
            instance.ratio = ratio
            instance.image_shape = image_shape

        elif self.parameters.common.with_boxes:
            boxes = self.boxes(index)

            boxes = boxes[boxes[:, -1] != -1]
            if len(boxes):
                labels = boxes[..., 4]
                boxes = boxes[..., 0:4]
                boxes = (self.normalizer(boxes, self.parameters.common.shape)
                         if self.normalizer else boxes)
                boxes = self.transformer(boxes) if self.transformer else boxes
            else:
                labels = np.array([])
                boxes = np.array([])

            instance = DetectionInstance(name)
            instance.image = image
            instance.height = height
            instance.width = width
            instance.boxes = boxes
            instance.labels = labels
            instance.shapes = shapes
            instance.ratio = ratio
            instance.image_shape = image_shape

        elif self.parameters.common.with_masks:
            segments, labels = self.segments(index)

            instance = SegmentationInstance(name)
            instance.image = image
            instance.height = height
            instance.width = width
            instance.polygons = segments
            instance.labels = labels
            instance.shapes = shapes
            instance.ratio = ratio
            instance.image_shape = image_shape

        else:
            raise TypeError("No task was assigned for this dataset.")

        return instance


class EdgeFirstDatabase(Database):
    def __init__(
        self,
        source: str,
        parameters: DatasetParameters,
        sessions: Union[list, tuple] = None,
    ):
        """
        Reads EdgeFirst Database/Datasets.

        Parameters
        ----------
        source: str
            This is the path to the Arrow file containing the
            annotations of EdgeFirst Datasets.
        parameters: DatasetParameters
            This contains dataset parameters set from the command line.
        sessions: Union[list, tuple]
            Filter to only use the specified sessions. By default, use
            all the sessions.

        Raises
        ------
        FileNotFoundError
            Raised if the source provided does not exist.
        ValueError
            Raised if the dataset does not contain any files.
        """
        self.__zipf__ = dict()
        self.source = source if source.endswith(
            "*.arrow") else os.path.join(source, "*.arrow")

        super(EdgeFirstDatabase, self).__init__(
            source=self.source,
            parameters=parameters
        )

        self.zip_file_name = None

        self.root_folder = os.path.dirname(
            self.source) if self.source.endswith("*.arrow") else self.source

        if not os.path.exists(self.root_folder):
            raise FileNotFoundError(
                "Dataset folder was not found at: ", self.root_folder)

        if len(glob.glob(self.source)) == 1:
            arrow = glob.glob(self.source)[0]
            self.zip_file_name = os.path.splitext(os.path.basename(arrow))[0]
        elif len(glob.glob(self.source)) == 0:
            raise ValueError(
                "Dataset directory does not contain any *.arrow file.")

        self.jpeg = TurboJPEG()
        self.dataframe = pl.scan_ipc(self.source)

        if sessions is not None:
            self.dataframe = self.dataframe.filter(
                pl.col("name").is_in(sessions))

        self.all_images = glob.glob(
            os.path.join(self.root_folder, "**", "*"),
            recursive=True)

        self.all_images_dict = {}
        for image in self.all_images:
            if not os.path.isfile(image) or \
                    image.endswith(".txt") or \
                    image.endswith(".mask.png") or \
                    image.endswith(".depth.png") or \
                    image.endswith(".radar.png") or \
                    image.endswith(".radar.pcd") or \
                    image.endswith(".lidar.png") or \
                    image.endswith(".lidar.pcd") or \
                    image.endswith(".lidar.reflect") or \
                    image.endswith(".lidar.jpeg"):
                continue

            name = os.path.splitext(os.path.basename(image))[0]
            if name.endswith(".camera"):
                name = name[:-7]
            self.all_images_dict[name] = image

        self.dataframe = self.dataframe.with_row_index().collect()
        self.samples = self.dataframe.group_by(["name", "frame"]) \
            .agg(pl.col("index")) \
            .get_column("index").to_list()

        if len(self.samples) == 0:
            raise ValueError(
                "There are no validation samples found in this dataset.")

        # List the classes based on the label column of the dataframe.
        if self.parameters.labels is None:
            self.parameters.labels = self.dataframe.filter(
                pl.col('label').is_not_null()).select(
                pl.col('label')).unique().get_column('label').to_list()
            self.parameters.labels.sort()

        if self.parameters.common.with_masks:
            self.parameters.labels = ['background'] + self.parameters.labels

        mask_col = self.dataframe["mask"]
        box_col = self.dataframe["box2d"]
        is_all_mask_null = mask_col.null_count() == len(mask_col)
        is_all_box_null = box_col.null_count() == len(box_col)

        if is_all_mask_null and is_all_box_null:
            raise ValueError("There are no annotations in this dataset.")
        elif self.parameters.common.with_masks and not self.parameters.common.with_boxes:
            if is_all_mask_null:
                raise ValueError("There are no mask annotations in the dataset " +
                                 "to validate the segmentation model.")
        elif self.parameters.common.with_boxes and not self.parameters.common.with_masks:
            if is_all_box_null:
                raise ValueError("There are no box annotations in the dataset " +
                                 "to validate the detection model.")
        else:
            if is_all_mask_null:
                logger("There were no mask annotations found in this dataset.",
                       code="WARNING")

            if is_all_box_null:
                logger("There were no box annotations found in this dataset.",
                       code="WARNING")

    def __len__(self) -> int:
        """
        Returns the number of samples in the dataset.
        """
        return len(self.samples)

    def __del__(self):
        """
        Clears the dataset dictionary container.
        """
        if self.__zipf__:
            for key, handler in self.__zipf__.items():
                handler.close()

    @staticmethod
    def load_asset(path: Path, name: str,
                   frame: int) -> Union[np.ndarray, None]:
        """
        Reads frames or images from the dataset.

        Parameters
        ----------
        path: Path
            The path to the directory containing the image.
        name: str
            The name of the asset file.
        frame: int
            The frame number. If None or -1, then this indicates
            the asset is an image, not a frame.

        Returns
        -------
        Union[np.ndarray, None]
            This returns the NumPy image array. If it doesn't exist, None
            is returned.
        """
        suffixes = [f"_{frame}.camera.jpeg", f"{frame}.jpeg",
                    f"{frame}.jpg", f"{frame}.png"]
        # Check whether the asset is a frame or an image.
        if frame is None or frame < 0:
            suffixes = [".jpeg", ".jpg", ".png"]

        for suffix in suffixes:
            asset = path / f"{name}{suffix}"
            if asset.exists():
                with asset.open("rb") as file:
                    return file.read()
        return None

    def name(self, index: int) -> str:
        """
        Fetch the name of the dataset sample.

        Parameters
        ----------
        index: int
            The dataset sample index.

        Returns
        -------
        str
            The name of the sample. This is typically the basename
            of the image.
        """
        index = self.samples[index][0]
        name = self.dataframe.item(index, "name")
        frame = self.dataframe.item(index, "frame")
        if frame is None:
            return name
        return f"{name}_{frame}"

    def image(self, index: int) -> Tuple[np.ndarray, tuple, float, tuple]:
        """
        Reads the image file from the dataset. This method should
        also handle any image preprocessing specified when caching is
        required. Image preprocessing will include image resizing, letterbox,
        or padding and transformations to either YUYV or RGBA.

        Parameters
        ----------
        index: int
            The dataset sample index.

        Returns
        -------
        Tuple[np.ndarray, tuple, float, tuple]
            np.ndarray
                The image input after being preprocessed if caching
                is set. If caching is False, this image does not
                apply any transformations.
            tuple
                This is used to scale the bounding boxes of the ground
                truth and the model detections based on the letterbox
                transformation.
                ((pad image height, pad image width), (ratio y, ratio x), (pad x, pad y)).
            float
                Rescaling factor used for the bounding boxes.
            tuple
                The original image dimensions.

        Raises
        ------
        FileNotFoundError
            Raised if the image file does not exist in the dataset.
        """
        name = self.name(index)
        image = self.all_images_dict.get(name)

        if image is None:
            raise FileNotFoundError(f"Image '{name}' was not found")

        start = clock_now()
        with open(image, "rb") as file:
            data = file.read()
        try:
            # Apply image rotation stored in the Exif.
            data = rotate_image(data)
        except BaseException:
            data = self.jpeg.decode(data, pixel_format=TJPF_RGB)

        read_ns = clock_now() - start
        self.read_timings.append(read_ns * 1e-6)

        image = np.array(data, dtype=np.uint8)
        shapes, ratio, image_shape = None, None, None
        if self.parameters.common.cache:
            from edgefirst.validator.runners.processing.preprocess import preprocess
            start = clock_now()
            image, shapes, ratio, image_shape = preprocess(
                image=image,
                shape=self.parameters.common.shape,
                input_type=self.parameters.common.dtype,
                preprocessing=self.parameters.common.preprocessing,
                normalization=self.parameters.common.norm,
            )
            load_ns = clock_now() - start
            self.load_timings.append(load_ns * 1e-6)
        else:
            image_shape = image.shape

        self.shape = image_shape
        return image, shapes, ratio, image_shape

    def labels(self, index: int) -> np.ndarray:
        """
        Fetch the labels at the specified sample.

        Parameters
        ----------
        index: int
            The index of the sample in the dataset.

        Returns
        -------
            np.ndarray
                The labels in the sample containing np.int32 elements.
        """
        indices = self.samples[index]
        labels = (
            self.dataframe.lazy()
            .filter(pl.col("label").is_not_null())
            .filter(pl.col("index").is_in(indices))
            .select("label")
            .collect()
            .get_column("label")
            .to_list()
        )
        labels = np.array([
            self.parameters.labels.index(label) for label in labels],
            dtype=np.int32
        )
        return labels

    def boxes(self, index: int) -> np.ndarray:
        """
        Fetches the bounding box annotations at the specified sample.

        Parameters
        ----------
        index: int
            The index of the sample in the dataset.

        Returns
        -------
        np.ndarray
            The bounding box array. This array is formatted
            as [xmin, ymin, xmax, ymax, label].
        """
        indices = self.samples[index]
        boxes = self.dataframe.lazy()
        boxes = boxes.filter(pl.col("box2d").is_not_null())
        boxes = boxes.filter(pl.col("index").is_in(indices))

        boxes = boxes.select([pl.col("label"), "box2d"])
        data = boxes.collect()
        boxes = data.get_column("box2d").to_numpy()
        labels = data.get_column("label")
        labels = labels.to_list()
        labels = np.array([
            self.parameters.labels.index(label) for label in labels],
            dtype=np.float32
        )
        boxes = np.hstack([boxes, labels[:, None]])

        if boxes.shape[0] == 0:
            boxes = self.box_placeholder
        return boxes

    def segments(
        self,
        index: int,
        resample: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetches the mask annotations as polygons.

        Parameters
        ----------
        index: int
            The index of the sample in the dataset.
        resample: int
            The number of points to resample the segments.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            np.ndarray
                A flattened array containing [x, y, x, y, ... nan, ...]
                coordinates for the mask polygons where each mask
                is separated by NaN to indicate a separate object.
            np.ndarray
                Returns the labels for each mask.
        """
        indices = self.samples[index]
        polygons = self.dataframe.lazy()
        polygons = polygons.filter(pl.col("mask").is_not_null())
        polygons = polygons.filter(pl.col("index").is_in(indices))
        polygons = polygons.filter(
            pl.col('label').is_in(self.parameters.labels))
        polygons = polygons.select([pl.col("label"), "mask"])
        polygons = polygons.collect()

        labels = polygons.get_column("label").to_list()
        # Conversion to integer.
        labels = [self.parameters.labels.index(label) for label in labels]
        polygons = polygons.get_column("mask").to_numpy()

        segments = []
        for polygon in polygons:
            if len(polygon) == 0:
                continue
            # Use numpy operations to speed up the process
            valid_indices = np.ma.clump_unmasked(
                np.ma.masked_invalid(polygon))
            # Contours is a single object with multiple masks, the length
            # of the contours is the number of masks of this object.
            contours = [polygon[s] for s in valid_indices]
            # A weak solution as it combines masks of the same object, but
            # it reproduces the format from Ultralytics as polygons (n, p, 2)
            # where n is the number of object, p is the number of points,
            # and 2 (x, y) coordinate points.
            contours = np.concatenate(contours).reshape(-1, 2)
            segments.append(contours)

        # Get the original shape of the image.
        height, width = get_shape(self.shape)
        # Segments are being resampled.
        # https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/dataset.py#L274
        # NOTE: do NOT resample oriented boxes.
        if len(segments) > 0:
            # make sure segments interpolate correctly if
            # original length is greater than resample.
            max_len = max(len(s) for s in segments)
            resample = (max_len + 1) if resample < max_len else resample
            # list[np.array(resample, 2)] * num_samples
            segments = np.stack(resample_segments(
                segments, n=resample), axis=0)
            # Denormalize segments.
            segments[..., 0] *= width
            segments[..., 1] *= height
        else:
            segments = np.zeros((0, resample, 2), dtype=np.float32)

        return segments, np.array(labels).astype(np.int32)

    def mask(
        self,
        index: int,
        imgsz: tuple = None,
        ratio_pad: tuple = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetches the mask annotations at the specified sample.

        Parameters
        ----------
        index: int
            The index of the sample in the dataset.
        imgsz: tuple
            The (height, width) input shape of the model.
        ratio_pad:
            The letterbox scaling factors
            ((ratio y, ratio x), (pad x, pad y)).

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            np.ndarray
                The mask array.
            np.ndarray
                Resorting the ground truth based on these indices.
        """
        segments, labels = self.segments(index)
        sorted_idx = None

        if (self.parameters.common.cache and
            self.parameters.common.method in ["ultralytics", "yolov7"]
                and None not in [imgsz, ratio_pad]):

            mask, sorted_idx = format_segments(
                segments=segments,
                shape=imgsz,
                ratio_pad=ratio_pad,
                colors=labels,
                semantic=self.parameters.common.semantic
            )
        else:
            height, width = get_shape(self.shape)
            if len(segments) == 0:
                return np.zeros(shape=(height, width),
                                dtype=np.uint8), sorted_idx

            mask = Image.new('I', (width, height), 0)
            canvas = ImageDraw.Draw(mask)

            for segment, label in zip(segments, labels):
                segment = segment.astype(np.int32).tolist()
                # A polygon needs atleast 2 points.
                if len(segment) < 2:
                    continue

                canvas.polygon(segment, outline=label, fill=label)
            mask = np.array(mask, dtype=np.uint8)

        return mask, sorted_idx

    def get_storage_handler(self, file: str) -> ZipFile:
        """
        Returns a cached ZipFile handler or
        opens and caches a new one.

        Parameters
        ----------
        file : str
            Path to the ZIP file.

        Returns
        -------
        ZipFile
            A ZipFile handler for the specified file.
        """
        handler = self.__zipf__.get(file)
        if handler is None:
            handler = ZipFile(file, "r")
            self.__zipf__[file] = handler

        return handler


class DarknetDatabase(Database):
    def __init__(
        self,
        source: Union[list, tuple],
        parameters: DatasetParameters
    ):
        """
        Reads from a DarkNet Database.

        Parameters
        ----------
        source: Union[list, tuple]
            These are the paths to the directories that contains
            (images, boxes, masks).
        parameters: DatasetParameters
            This contains dataset parameters set from the command line.
        """
        super(DarknetDatabase, self).__init__(
            source=source,
            parameters=parameters
        )

        self.image_path = source[0]
        self.box_path = source[1]
        self.mask_path = source[2]

        self.class_offset = np.array(
            [[0, 0, 0, 0, 0]], dtype=np.float32)
        if 'background' in self.parameters.labels:
            self.class_offset = np.array(
                [[0, 0, 0, 0, 1]], dtype=np.float32)

        images = []
        for ext in ['*.[pP][nN][gG]', '*.[jJ][pP][gG]', '*.[jJ][pP][eE][gG]']:
            images += glob.glob(os.path.join(self.image_path, ext))

        group = dict()
        for image in images:
            key = os.path.splitext(os.path.basename(image))[0]
            group[key] = [image, None, None]

        if self.parameters.common.with_boxes:
            annotations = glob.glob(os.path.join(
                self.box_path, '*.[tT][xX][tT]'))
            for annotation in annotations:
                key = os.path.splitext(os.path.basename(annotation))[0]
                if key in group:
                    group[key][1] = annotation

        if self.parameters.common.with_masks:
            annotations = glob.glob(os.path.join(
                self.mask_path, '*.[pP][nN][gG]'))
            for annotation in annotations:
                key = os.path.splitext(os.path.basename(annotation))[0]
                if key in group:
                    group[key][2] = annotation

        self.storage = []
        for key, value in group.items():
            self.storage.append(value)

    def __len__(self) -> int:
        """
        Returns the number of samples in the dataset.
        """
        return len(self.storage)

    def name(self, index: int) -> str:
        """
        Fetch the name of the dataset sample.

        Parameters
        ----------
        index: int
            The dataset sample index.

        Returns
        -------
        str
            The name of the sample. This is typically the basename
            of the image.
        """
        sample = self.storage[index][0]
        return os.path.basename(sample)

    def image(self, index: int) -> Tuple[np.ndarray, tuple, float, tuple]:
        """
        Reads the image file from the dataset. This method
        should also handle any image preprocessing specified when
        caching is required. Image preoricessing will include image
        resizing, letterbox, or padding and transformations to either
        YUYV or RGBA.

        Parameters
        ----------
        index: int
            The dataset sample index.

        Returns
        -------
        Tuple[np.ndarray, tuple, float, tuple]
            np.ndarray
                The image input after being preprocessed if caching
                is set. If caching is False, this image does not
                apply any transformations.
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
        img_path = self.storage[index][0]

        start = clock_now()
        image = read_image(img_path, rotate=True)
        read_ns = clock_now() - start
        self.read_timings.append(read_ns * 1e-6)

        shapes, ratio, image_shape = None, None, None
        if self.parameters.common.cache:
            from edgefirst.validator.runners.processing.preprocess import preprocess
            start = clock_now()
            image, shapes, ratio, image_shape = preprocess(
                image=image,
                shape=self.parameters.common.shape,
                input_type=self.parameters.common.dtype,
                preprocessing=self.parameters.common.preprocessing,
                normalization=self.parameters.common.norm,
                resample=Image.Resampling.BILINEAR
            )
            load_ns = clock_now() - start
            self.load_timings.append(load_ns * 1e-6)
        else:
            image_shape = image.shape

        self.shape = image_shape
        return image, shapes, ratio, image_shape

    def boxes(self, index: int) -> np.ndarray:
        """
        Fetches the bounding box annotations at the specified sample.

        Parameters
        -----------
        index: int
            The index of the sample in the dataset.

        Returns
        -------
        np.ndarray
            The bounding box array. This array is formatted
            as [xmin, ymin, xmax, ymax, label].
        """
        box_file = self.storage[index][1]
        if box_file is None:
            return self.box_placeholder

        boxes = np.genfromtxt(box_file, delimiter=' ', ndmin=2)
        boxes = np.roll(boxes, 4, axis=-1)
        boxes = boxes + self.class_offset
        return boxes

    def segments(self, index: int):
        """
        Fetches the mask annotations as polygons.

        Parameters
        ----------
        index: int
            The index of the sample in the dataset.
        """
        raise NotImplementedError(
            "Fetching the mask segments is not yet implemented.")

    def mask(
        self,
        index: int,
        imgsz: tuple = None,
        ratio_pad: tuple = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetches the mask annotations at the specified sample.

        Parameters
        ----------
        index: int
            The index of the sample in the dataset.
        imgsz: tuple
            The (height, width) input shape of the model.
        ratio_pad:
            The letterbox scaling factors
            ((ratio y, ratio x), (pad x, pad y)).

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            np.ndarray
                The mask array.
            np.ndarray
                Resorting the ground truth based on these indices.
        """
        height, width = get_shape(self.shape)
        sorted_idx = None
        mask = np.zeros(shape=(height, width), dtype=np.uint8)

        if (self.parameters.common.cache and
                self.parameters.common.method in ["ultralytics", "yolov7"]):

            raise NotImplementedError(
                "Caching the mask with Ultralytics is not yet supported.")

        else:
            mask_file = self.storage[index][2]
            if mask_file is None:
                return np.zeros(shape=(height, width), dtype=np.uint8)

            mask = Image.open(mask_file)
            mask = mask.resize((width, height), Image.Resampling.NEAREST)
            mask = np.array(mask, dtype=np.uint8)

        return mask, sorted_idx


class LMDBDatabase(Database):
    """
    Reads from LMDB database cache. This is the cache file.
    It should already store preprocessed images and annotations. The
    shape for the images across all samples remains consistent to the
    input shape of the model.

    Parameters
    ----------
    MAP_SIZE : int
        The maximum size of the LMDB database.
    source: str
        This is the path to the LMDB Database file.
    parameters: DatasetParameters
        This contains dataset parameters set from the command line.
    """

    MAP_SIZE = 32 * 1024 * 1024 * 1024

    def __init__(
        self,
        source: str,
        parameters: DatasetParameters
    ):
        super(LMDBDatabase, self).__init__(
            source=source,
            parameters=parameters
        )

        if not os.path.isfile(self.source):
            raise FileNotFoundError(
                "Specify the path to the cache file. Got: '{}'".format(
                    self.source))

        self.db = lmdb.open(
            str(self.source).encode(),
            map_size=LMDBDatabase.MAP_SIZE,
            max_dbs=10,
            subdir=False,
            lock=False
        )
        self.camera_db = self.db.open_db(b'camera')
        self.boxes_db = self.db.open_db(b'box2d')
        self.masks_db = self.db.open_db(b'masks')
        self.names_db = self.db.open_db(b'names')
        self.labels_db = self.db.open_db(b'labels')

        with self.db.begin() as txn:
            labels = txn.get(b'labels', db=self.labels_db)
            if labels:
                labels = json.loads(labels.decode())
                self.parameters.labels = [str(c) for c in labels]

        with self.db.begin() as txn:
            cur = txn.cursor(self.names_db)
            keys = [key.decode() for key, _ in cur]
        self.samples = keys

    def __len__(self) -> int:
        """
        Returns the number of samples in the dataset.
        """
        return len(self.samples)

    def __del__(self):
        """
        Closes the database.
        """
        self.db.close()

    def __iter__(self):
        """
        Iterate through the database to
        yield a single sample.

        Yields
        ------
        tuple
            This can contain the following elements
            (name, image, boxes, masks) for multitask, (name, image, boxes)
            for detection, (name, image, masks) for segmentation.
        """
        for key in self.samples:
            yield self.get_instance(key)

    def name(self, index: int) -> str:
        """
        Fetch the name of the dataset sample.

        Parameters
        ----------
        index: int
            The dataset sample index.

        Returns
        -------
        str
            The name of the sample. This is typically the basename
            of the image.
        """
        return self.samples[index]

    def image(self, key: str) -> Tuple[np.ndarray, tuple, float, tuple]:
        """
        Fetches the preprocessed image stored in the cache.

        Parameters
        ----------
        key: str
            The database key for the sample to fetch.

        Returns
        -------
        Tuple[np.ndarray, tuple, float, tuple]
            np.ndarray
                The image input after being preprocessed if caching
                is set. If caching is False, this image does not
                apply any transformations.
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
        # The shape stored inside the parameters at this point is
        # based on the preprocessed image.
        image = np.zeros(self.parameters.common.shape, dtype=np.uint8)
        shapes, ratio, image_shape = None, None, None

        with self.db.begin(buffers=True) as txn:
            image_shape_tx = txn.get(
                f'{key}/shape'.encode(), db=self.camera_db)
            if image_shape_tx:
                image_shape = tuple(np.frombuffer(
                    image_shape_tx, dtype=np.int32))

            image_tx = txn.get(key.encode(), db=self.camera_db)
            if image_tx:
                # Note: this will fail for float16 types.
                # Caching results in floating types for the images.
                if self.parameters.common.cache:
                    dtype = np.float32
                    shape = self.parameters.common.shape
                else:
                    dtype = np.uint8
                    shape = image_shape

                # The shape should remain consistent for all images
                # when the dataset is cached. However, allowing dynamic shapes.
                image = np.frombuffer(image_tx, dtype=dtype).reshape(shape)

            shapes_tx = txn.get(f'{key}/shapes'.encode(), db=self.camera_db)
            if shapes_tx:
                shapes = json.loads(bytes(shapes_tx).decode())

            ratio_tx = txn.get(f'{key}/ratio'.encode(), db=self.camera_db)
            if ratio_tx:
                ratio = float(np.frombuffer(ratio_tx, dtype=np.float32)[0])

        return image, shapes, ratio, image_shape

    def boxes(self, key: str) -> np.ndarray:
        """
        Fetches the boxes stored in the cache.

        Parameters
        -----------
        key: str
            The database key for the sample to fetch.

        Returns
        -------
        np.ndarray
            The bounding box array. This array is formatted
            as [xmin, ymin, xmax, ymax, label].
        """
        boxes = self.box_placeholder
        with self.db.begin(buffers=True) as txn:
            boxes_tx = txn.get(key.encode(), db=self.boxes_db)
            if boxes_tx:
                boxes = np.frombuffer(boxes_tx, dtype=np.float32)
                if len(boxes) == 0 or boxes[0] == -1:
                    boxes = self.box_placeholder
                else:
                    boxes = boxes.reshape(-1, 5)
        return boxes

    def mask(self, key: str) -> np.ndarray:
        """
        Fetches the masks stored in the cache.

        Parameters
        -----------
        key: str
            The database key for the sample to fetch.

        Returns
        -------
        np.ndarray
            The masks array.
        """
        # Reading Mask
        mask = None
        with self.db.begin(buffers=True) as txn:
            mask_shape_tx = txn.get(f'{key}/mask_shape'.encode(),
                                    db=self.masks_db)
            if mask_shape_tx:
                mask_shape = tuple(np.frombuffer(
                    mask_shape_tx, dtype=np.int32))
            else:
                mask_shape = get_shape(self.shape)

            masks_tx = txn.get(key.encode(), db=self.masks_db)
            if masks_tx:
                mask = np.frombuffer(masks_tx, dtype=np.uint8)
                mask = mask.reshape(mask_shape) if mask.shape[0] > 0 \
                    else np.zeros(shape=mask_shape, dtype=np.uint8)

        if mask is None:
            mask = np.zeros(shape=mask_shape, dtype=np.uint8)
        return mask

    def get_instance(self, key: str):
        """
        Get a single annotation instance from the database.

        Parameters
        ----------
        key: str
            Specify the instance key to fetch from the database.

        Returns
        -------
        tuple
            This can contain the following elements
            (name, image, boxes, masks) for multitask, (name, image, boxes)
            for detection, (name, image, masks) for segmentation.

        Raises
        ------
        TypeError
            Raised of with_boxes and with_masks are both set to False
            which indicates neither tasks were selected.
        """
        image_data = self.image(key)
        if self.parameters.common.with_boxes and self.parameters.common.with_masks:
            boxes = self.boxes(key)
            masks = self.mask(key)
            return key, image_data, boxes, masks
        elif self.parameters.common.with_boxes:
            boxes = self.boxes(key)
            return key, image_data, boxes
        elif self.parameters.common.with_masks:
            masks = self.mask(key)
            return key, image_data, masks
        else:
            raise TypeError("No task was assigned for this dataset")

    def build_dataset(self) -> list:
        """
        Returns a list of keys from the database.
        """
        return self.samples

    def read_sample(self, key: str) -> Instance:
        """
        Builds the ground truth instances from the sample.

        Parameters
        ----------
        key: str
            Specify the instance key to fetch from the database.

        Returns
        -------
        Instance
            The ground truth instance objects contains the annotations
            representing the ground truth of the image.
        """
        image, shapes, ratio, image_shape = self.image(key)
        height, width = image_shape

        if self.parameters.common.with_boxes and self.parameters.common.with_masks:
            boxes = self.boxes(key)
            mask = self.mask(key)

            # There is no need to transform and normalize bounding boxes
            # here as the cache should already store transformed boxes.
            boxes = boxes[boxes[:, -1] != -1]
            if len(boxes):
                labels = boxes[..., 4]
                boxes = boxes[..., 0:4]
            else:
                labels = np.array([])
                boxes = np.array([])

            instance = MultitaskInstance(key)
            instance.image = image
            instance.height = height
            instance.width = width
            instance.boxes = boxes
            instance.labels = labels
            instance.mask = mask
            instance.shapes = shapes
            instance.ratio = ratio
            instance.image_shape = image_shape

        elif self.parameters.common.with_boxes:
            boxes = self.boxes(key)

            # There is no need to transform and normalize bounding boxes
            # here as the cache should already store transformed boxes.
            boxes = boxes[boxes[:, -1] != -1]
            if len(boxes):
                labels = boxes[..., 4]
                boxes = boxes[..., 0:4]
            else:
                labels = np.array([])
                boxes = np.array([])

            instance = DetectionInstance(key)
            instance.image = image
            instance.height = height
            instance.width = width
            instance.boxes = boxes
            instance.labels = labels
            instance.shapes = shapes
            instance.ratio = ratio
            instance.image_shape = image_shape

        elif self.parameters.common.with_masks:
            mask = self.mask(key)

            instance = SegmentationInstance(key)
            instance.image = image
            instance.height = height
            instance.width = width
            instance.mask = mask
            instance.shapes = shapes
            instance.ratio = ratio
            instance.image_shape = image_shape

        else:
            raise TypeError("No task was assigned for this dataset.")

        return instance
