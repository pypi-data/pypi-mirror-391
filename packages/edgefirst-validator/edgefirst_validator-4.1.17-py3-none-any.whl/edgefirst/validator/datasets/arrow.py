"""
Implementations for reading Arrow datasets.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import numpy as np

from edgefirst.validator.datasets import Dataset
from edgefirst.validator.datasets import DetectionInstance
from edgefirst.validator.publishers.utils.logger import logger
from edgefirst.validator.datasets.utils.fetch import (classify_dataset,
                                                      validate_dataset_source)

if TYPE_CHECKING:
    from edgefirst.validator.evaluators import DatasetParameters


class ArrowDataset(Dataset):
    """
    Reads Arrow datasets.

    Parameters
    ----------
    source: str
        The path to the source dataset.
    parameters: DatasetParameters
        This contains dataset parameters set from the command line.
    info_dataset: dict
        Contains information such as:

            .. code-block:: python

                {
                    "classes": [list of unique labels],
                    "validation":
                    {
                        "images: 'path to the images arrow files',
                        "annotations": 'path to the annotations arrow files'
                    }
                }

        *Note: the classes are optional and the path to the images
        and annotations can be the same.*
    """

    def __init__(
        self,
        source: str,
        parameters: DatasetParameters,
        info_dataset: dict = None,
    ):
        super(ArrowDataset, self).__init__(
            source=source,
            parameters=parameters
        )

        if info_dataset is None:
            info_dataset = classify_dataset(source)

        try:
            self.image_source = info_dataset.get(
                "dataset").get('validation').get('images')
            self.annotation_source = info_dataset.get(
                "dataset").get('validation').get('annotations')
        except AttributeError:
            self.image_source = validate_dataset_source(
                info_dataset.get('validation').get('images'))
            self.annotation_source = validate_dataset_source(
                info_dataset.get('validation').get('annotations'))

        try:
            from deepview.datasets.readers import PolarsDetectionReader  # type: ignore
        except ImportError:
            logger(
                "Dependency missing: deepview-datasets is needed for polar datasets.",
                code="ERROR")
        self.reader = PolarsDetectionReader(
            inputs=self.image_source,
            annotations=self.annotation_source,
        )

        labels = info_dataset.get('classes', None)
        if labels is not None:
            self.parameters.labels = [str(label) for label in labels]
        else:
            self.parameters.labels = self.reader.classes

    def build_dataset(self):
        """
        Allows iteration in the dataset.

        Returns
        -------
        Iterator
            Contains the images and boxes.
        """
        return self.reader

    def read_sample(self, sample: tuple) -> DetectionInstance:
        """
        Reads one sample from the dataset.

        Parameters
        ----------
        sample: tuple
            This contains the (image, boxes).

        Returns
        -------
        DetectionInstance
            The ground truth instance objects contains the bounding boxes
            and the labels representing the ground truth of the image.
        """
        if self.parameters.common.with_boxes:
            image = sample[0].astype(np.uint8)
            height, width, _ = image.shape
            boxes = sample[1]

            image_path = self.reader.get_instance_id()
            # Add file extension to allow image saving in disk.
            if os.path.splitext(image_path)[-1] == "":
                image_path += ".png"

            instance = DetectionInstance(image_path)
            instance.height = height
            instance.width = width
            instance.image = image

            labels = (np.squeeze(boxes[..., 4:5].astype(np.int32), axis=1) +
                      self.parameters.label_offset)
            boxes = boxes[..., 0:4]

            if len(boxes) > 0:
                boxes = self.normalizer(
                    boxes, (height, width)) if self.normalizer else boxes
                boxes = self.transformer(boxes) if self.transformer else boxes

            instance.boxes = boxes
            instance.labels = labels
            return instance
        else:
            raise NotImplementedError(
                "Only 'with_boxes' is currently supported for Arrow datasets.")
