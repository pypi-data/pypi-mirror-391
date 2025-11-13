"""
Common parent dataset implementations.
"""

from __future__ import annotations

import io
import os
from typing import TYPE_CHECKING, Union

import numpy as np
from PIL import Image

from edgefirst.validator.datasets.instance import Instance
from edgefirst.validator.datasets.utils.transformations import (yolo2xyxy,
                                                                xywh2xyxy,
                                                                normalize,
                                                                denormalize_polygon)

if TYPE_CHECKING:
    from deepview.datasets.generators.detection import BaseObjectDetectionGenerator  # type: ignore
    from deepview.datasets.readers.darknet import DarknetDetectionReader  # type: ignore
    from edgefirst.validator.evaluators import DatasetParameters


class Dataset:
    """
    Abstract dataset class for providing template methods in the dataset.

    Parameters
    ----------
    source: str
        The path to the source dataset.
    parameters: DatasetParameters
        This contains dataset parameters set from the command line.

    Raises
    ------
    ValueError
        Raised if the provided parameters in certain methods
        does not conform to the specified data type.
    """

    def __init__(
        self,
        source: str,
        parameters: DatasetParameters
    ):
        self.source = source
        self.parameters = parameters

        self.transformer = None
        if self.parameters.box_format == 'yolo':
            self.transformer = yolo2xyxy
        elif self.parameters.box_format == 'coco':
            self.transformer = xywh2xyxy
        else:
            self.transformer = None

        self.normalizer = None
        self.denormalizer = None
        if self.parameters.normalized:
            if self.parameters.common.with_masks:
                self.denormalizer = denormalize_polygon
        else:
            if self.parameters.common.with_boxes:
                self.normalizer = normalize

        self.read_timings = list()
        self.load_timings = list()

    def build_dataset(self):
        """Abstract Method"""
        raise NotImplementedError("This is an abstract method.")

    def read_sample(self, instance):
        """Abstract Method"""
        raise NotImplementedError("This is an abstract method.")

    def read_all_samples(
        self,
        info: str = "Validation Progress",
        silent: bool = False
    ):
        """
        Reads all the samples in the dataset.

        Parameters
        ----------
        info: str
            The description of why image instances are being read.
            By default it is to run validation, hence "Validation Progress".
        silent: bool
            If set to true, prevent validation logging.

        Yields
        -------
        Instance
            Yields one sample of the ground truth
            instance which contains information on the image
            as a numpy array, boxes, labels, and image path.
        """
        if silent:
            samples = self.build_dataset()
            for sample in samples:
                yield self.read_sample(sample)
        else:
            try:
                from tqdm import tqdm
            except ImportError:
                pass

            try:
                samples = tqdm(self.build_dataset(), colour="green")
                samples.set_description(info)
                for sample in samples:
                    yield self.read_sample(sample)
            except NameError:
                samples = self.build_dataset()
                num_samples = len(samples)
                for index in range(num_samples):
                    print("\t - [INFO]: Computing metrics for image: " +
                          "%i of %i [%2.f %s]" %
                          (index + 1,
                           num_samples,
                           100 * ((index + 1) / float(num_samples)),
                           '%'), end='\r')
                    yield self.read_sample(samples[index])

    def timings(self):
        """
        Returns a summary of all the timings:
        (mean, avg, max) of the preprocessing time.

        Returns
        -------
            timings in ms: dict

            .. code-block:: python

                {
                 'min_input_time': minimum time to load an image,
                 'max_input_time': maximum time to load an image,
                 'avg_input_time': average time to load an image,
                }
        """
        return {
            'min_input_time': (np.min(self.load_timings)
                               if len(self.load_timings) else 0),
            'max_input_time': (np.max(self.load_timings)
                               if len(self.load_timings) else 0),
            'avg_input_time': (np.mean(self.load_timings)
                               if len(self.load_timings) else 0),
        }


class BaseDataset(Dataset):
    """
    This class utilizes deepview-datasets methods for iterating through
    the images and annotations.

    Parameters
    ----------
    source: str
        The path to the dataset.
    iterator: Iterator
        Object in deepview-datasets for iterating through
        the images or annotations. This can either be a generator if
        a YAML file was passed, or a Reader if a directory was passed.
    """

    def __init__(
        self,
        source: str,
        iterator: Union[BaseObjectDetectionGenerator, DarknetDetectionReader]
    ):
        super(BaseDataset, self).__init__(source)
        self.iterator = iterator

        if isinstance(self.iterator, BaseObjectDetectionGenerator):
            self.storage = self.iterator.reader.storage
            self.labels = self.iterator.reader.classes
        else:
            self.storage = self.iterator.storage
            self.labels = self.iterator.classes

    def build_dataset(
            self) -> Union[BaseObjectDetectionGenerator, DarknetDetectionReader]:
        """
        Returns the iterator object which already contains all the images
        and annotations read in the dataset.

        Returns
        -------
        Union[BaseObjectDetectionGenerator, DarknetDetectionReader]
            BaseObjectDetectionGenerator
                A generator if a YAML file was passed.
            DarknetDetectionReader
                Reader if a directory was passed.
        """
        return self.iterator

    def read_sample(self, sample: tuple) -> Instance:
        """
        Returns the ground truth instance object which is needed to be read
        by validator.

        Parameters
        ----------
        sample: tuple
            This contains the (image, boxes) in one sample.

        Returns
        -------
        Instance
            An object that contains the image, boxes, labels, etc.
        """
        from edgefirst.validator.datasets.utils.transformations import yolo2xyxy

        image, boxes = sample
        if len(image.shape) < 2:
            image = Image.open(io.BytesIO(image)).convert('RGB')
            image = np.asarray(image, dtype=np.uint8)
        height, width, _ = image.shape

        if isinstance(self.iterator, BaseObjectDetectionGenerator):
            image_path = self.iterator.reader.get_instance_id()
        else:
            image_path = self.iterator.get_instance_id()

        # Add file extension to allow image saving in disk.
        if os.path.splitext(image_path)[-1] == "":
            image_path += ".png"

        instance = Instance(image_path)
        instance.height = height
        instance.width = width
        instance.image = image

        boxes = boxes[np.sum(boxes, axis=-1) != 0]
        instance.boxes = yolo2xyxy(boxes[..., 0:4])

        labels = boxes[..., 4:5]
        instance.labels = labels
        return instance
